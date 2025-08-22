import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import TopProducts from "./pages/TopProducts";
import ChannelActivity from "./pages/ChannelActivity";
import SearchMessages from "./pages/SearchMessages";

export default function App() {
  return (
    <Router>
      <nav className="p-4 bg-gray-800 text-white flex gap-4">
        <Link to="/">Top Products</Link>
        <Link to="/channel">Channel Activity</Link>
        <Link to="/search">Search</Link>
      </nav>

      <div className="p-6">
        <Routes>
          <Route path="/" element={<TopProducts />} />
          <Route path="/channel" element={<ChannelActivity />} />
          <Route path="/search" element={<SearchMessages />} />
        </Routes>
      </div>
    </Router>
  );
}
