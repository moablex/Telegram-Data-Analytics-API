import { useState } from "react";

export default function SearchMessages() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = () => {
    fetch(`http://localhost:8000/api/search/messages?query=${query}`)
      .then(res => res.json())
      .then(data => setResults(data));
  };

  return (
    <div>
      <h1 className="text-2xl mb-4">Search Messages</h1>
      <input
        className="border p-2 mr-2"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter keyword"
      />
      <button onClick={handleSearch} className="bg-blue-500 text-white p-2 rounded">
        Search
      </button>

      <ul className="mt-4 space-y-2">
        {results.map((m) => (
          <li key={m.message_id} className="p-2 bg-gray-100 rounded">
            <b>{m.channel_name}</b>: {m.message}
          </li>
        ))}
      </ul>
    </div>
  );
}
