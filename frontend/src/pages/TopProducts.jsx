import { useEffect, useState } from "react";
import api from "../api";
import ChartCard from "../components/ChartCard";
import DataTable from "../components/DataTable";

export default function TopProducts() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    api.get("/reports/top-products?limit=10")
      .then((res) => {
        console.log("API Response:", res.data); // Debug
        const formatted = res.data.map((item) => ({
          product_name: item.product_name,
          mentions: item.mention_count,
        }));
        setProducts(formatted);
      })
      .catch((err) => console.error("API Error:", err));
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Top Products</h1>

      {products.length > 0 ? (
        <>
          <ChartCard
            title="Most Mentioned Products"
            data={products}
            dataKeyX="product_name"
            dataKeyY="mentions"
          />
          <DataTable columns={["product_name", "mentions"]} data={products} />
        </>
      ) : (
        <p className="text-gray-500">No products found.</p>
      )}
    </div>
  );
}
