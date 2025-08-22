import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="bg-blue-600 p-4 text-white flex gap-6">
      <Link to="/">Home</Link>
      <Link to="/top-products">Top Products</Link>
      <Link to="/channels/activity">Channel Activity</Link>
    </nav>
  );
}
