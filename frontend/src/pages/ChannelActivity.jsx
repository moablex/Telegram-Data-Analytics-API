import { useEffect, useState } from "react";
import api from "../api";
import ChartCard from "../components/ChartCard";

export default function ChannelActivity() {
  const [activity, setActivity] = useState([]);
  const channelName = "my_channel"; // you can replace with dynamic route later

  useEffect(() => {
    api.get(`/channels/${channelName}/activity`)
      .then((res) => setActivity(res.data))
      .catch((err) => console.error(err));
  }, [channelName]);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Channel Activity: {channelName}</h1>
      <ChartCard
        title="Daily Posting Activity"
        data={activity}
        dataKeyX="date"
        dataKeyY="messages"
      />
    </div>
  );
}
