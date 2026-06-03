import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from "recharts"

function PriceChart({ data }) {
  const formattedData = data.map((item) => ({
    ...item,
    displayDate: new Date(item.date).toLocaleDateString("en-US", {
      month: "short",
      year: "numeric"
    })
  }))

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
      <h3 className="text-gray-900 font-semibold text-lg mb-4">
        Price History
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#f0f0f0"
          />

          <XAxis
            dataKey="displayDate"
            tick={{ fontSize: 12 }}
          />

          <YAxis
            tickFormatter={(v) => `$${v}`}
            tick={{ fontSize: 12 }}
          />

          <Tooltip
            formatter={(v) => [`$${v}`, "Price"]}
            labelFormatter={(label) => `Date: ${label}`}
          />

          <Line
            type="monotone"
            dataKey="price"
            stroke="#2563eb"
            strokeWidth={3}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PriceChart