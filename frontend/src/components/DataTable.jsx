export default function DataTable({ columns, data }) {
    return (
      <table className="min-w-full border border-gray-200 rounded-lg">
        <thead className="bg-gray-100">
          <tr>
            {columns.map((col) => (
              <th key={col} className="px-4 py-2 text-left border-b">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td key={col} className="px-4 py-2 border-b">{row[col]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  }
  