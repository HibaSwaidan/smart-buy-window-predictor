import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts"

function StatCard({ label, value }) {
  return (
    <div className="rounded-2xl border border-gray-100 bg-gray-50 p-4">
      <p className="text-xs font-semibold text-gray-500">{label}</p>
      <p className="text-lg font-extrabold text-gray-900 mt-1">{value}</p>
    </div>
  )
}

function PriceChart({ data = [] }) {
  const formattedData = data.map((item) => ({
    ...item,
    displayDate: new Date(item.date).toLocaleDateString("en-US", {
      month: "short",
      year: "numeric",
    }),
  }))

  const prices = data
    .map((item) => item.price)
    .filter((price) => price !== null && price !== undefined)

  const currentPrice = prices.length ? prices[prices.length - 1] : 0
  const lowestPrice = prices.length ? Math.min(...prices) : 0
  const highestPrice = prices.length ? Math.max(...prices) : 0
  const priceRange = highestPrice - lowestPrice

  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-200">
      <div className="mb-6">
        <p className="text-sm font-semibold text-blue-600 mb-1">
          Historical Pricing
        </p>

        <h3 className="text-xl font-bold text-gray-900">
          Price History Trend
        </h3>

        <p className="text-sm text-gray-500 mt-2">
          Recent price movement used as part of the buy-window recommendation.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <StatCard label="Current Price" value={`$${currentPrice.toFixed(2)}`} />
        <StatCard label="Lowest Shown" value={`$${lowestPrice.toFixed(2)}`} />
        <StatCard label="Highest Shown" value={`$${highestPrice.toFixed(2)}`} />
        <StatCard label="Price Range" value={`$${priceRange.toFixed(2)}`} />
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart
          data={formattedData}
          margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />

          <XAxis
            dataKey="displayDate"
            tick={{ fontSize: 12, fill: "#6b7280" }}
            axisLine={false}
            tickLine={false}
          />

          <YAxis
            tickFormatter={(v) => `$${v}`}
            tick={{ fontSize: 12, fill: "#6b7280" }}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip
            formatter={(v) => [`$${Number(v).toFixed(2)}`, "Price"]}
            labelFormatter={(label) => `Date: ${label}`}
            contentStyle={{
              borderRadius: "12px",
              border: "1px solid #e5e7eb",
              boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
            }}
          />

          <Line
            type="monotone"
            dataKey="price"
            stroke="#2563eb"
            strokeWidth={3}
            dot={{ r: 4, strokeWidth: 2 }}
            activeDot={{ r: 7 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PriceChart