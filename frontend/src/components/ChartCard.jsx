import React from "react";

const ChartCard = ({ title, children }) => {
  return (
    <div className="bg-white rounded-2xl shadow p-4 mb-6">
      <h2 className="text-lg font-semibold mb-2">{title}</h2>
      {children}
    </div>
  );
};

export default ChartCard;