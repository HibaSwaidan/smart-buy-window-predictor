import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts"

function PriceChart({ data }) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <h3 className="text-gray-700 font-medium mb-4">Price History</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={(v) => `$${v}`} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v) => `$${v}`} />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PriceChart