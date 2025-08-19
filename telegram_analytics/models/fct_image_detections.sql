

SELECT
    message_id,
    channel,
    image_path,
    object_class,
    confidence,
    bbox
FROM {{ source('public', 'stg_image_detections') }}
