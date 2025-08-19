
import os
import json
import psycopg2
import logging
from dotenv import load_dotenv
from ultralytics import YOLO
from tqdm import tqdm

# Load env vars
load_dotenv()

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
IMAGES_DIR = "data/images"
MODEL_PATH = "yolov8n.pt"  # or yolov8s.pt
YOLO_CONFIDENCE_THRESHOLD = 0.3

# PostgreSQL connection
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS stg_image_detections (
    message_id INTEGER,
    channel TEXT,
    image_path TEXT,
    object_class TEXT,
    confidence FLOAT,
    bbox JSONB
);
""")
conn.commit()

# Load model
model = YOLO(MODEL_PATH)

def process_image(image_path, channel):
    try:
        results = model(image_path)[0]  # get first result
        detections = []

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < YOLO_CONFIDENCE_THRESHOLD:
                continue

            class_id = int(box.cls[0])
            label = model.names[class_id]
            bbox = [float(v) for v in box.xyxy[0].tolist()]  # [x1, y1, x2, y2]

            detections.append({
                "object_class": label,
                "confidence": conf,
                "bbox": bbox,
            })

        return detections
    except Exception as e:
        logger.error(f"Error processing {image_path}: {str(e)}")
        return []

def extract_message_id(filename):
    try:
        return int(filename.split("_")[-1].split(".")[0])
    except:
        return None

def scan_and_detect():
    for channel in os.listdir(IMAGES_DIR):
        channel_dir = os.path.join(IMAGES_DIR, channel)
        if not os.path.isdir(channel_dir):
            continue

        logger.info(f"Scanning {channel_dir}...")
        for filename in tqdm(os.listdir(channel_dir), desc=f"Detecting in {channel}"):
            if not filename.endswith(".jpg"):
                continue

            image_path = os.path.join(channel_dir, filename)
            message_id = extract_message_id(filename)
            if not message_id:
                continue

            detections = process_image(image_path, channel)
            for d in detections:
                cursor.execute("""
                INSERT INTO stg_image_detections (message_id, channel, image_path, object_class, confidence, bbox)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    message_id,
                    channel,
                    image_path,
                    d["object_class"],
                    d["confidence"],
                    json.dumps(d["bbox"])
                ))
    conn.commit()
    logger.info("✅ Detection results saved to stg_image_detections")

if __name__ == "__main__":
    scan_and_detect()
    cursor.close()
    conn.close()
