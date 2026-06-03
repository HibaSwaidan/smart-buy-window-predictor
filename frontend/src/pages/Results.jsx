import Verdict from "../components/Verdict"
import PriceChart from "../components/PriceChart"

function MetricRow({ label, value, type }) {
  const percent = Math.round(value * 100)

  const barColor =
    type === "risk"
      ? percent < 30
        ? "bg-green-500"
        : percent < 60
        ? "bg-yellow-500"
        : "bg-red-500"
      : percent >= 70
      ? "bg-green-500"
      : percent >= 40
      ? "bg-yellow-500"
      : "bg-red-500"

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-semibold text-gray-900">{percent}%</span>
      </div>

      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${barColor}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}

function Results({ data, onReset }) {
  return (
    <div className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <div className="flex flex-col md:flex-row gap-5 items-start">
            <div className="w-full md:w-40 h-40 bg-gray-100 rounded-xl overflow-hidden flex items-center justify-center">
              {data.image_url ? (
                <img
                  src={data.image_url}
                  alt={data.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-gray-400 text-sm">No image</span>
              )}
            </div>

            <div className="flex-1">
              <div className="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600">
                {data.category}
              </div>

              <h2 className="text-3xl font-bold text-gray-900 mt-3">
                {data.title}
              </h2>

              <div className="flex flex-wrap gap-4 mt-3 text-sm text-gray-500">
                <span>ASIN: {data.asin}</span>
              </div>

              <p className="text-gray-600 mt-4">
                Current price:{" "}
                <span className="font-semibold text-gray-900">
                  ${data.current_price}
                </span>
              </p>

              <div className="mt-4 inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
                Analysis based on historical price and availability signals
              </div>
            </div>
          </div>
        </div>

        <Verdict
          recommendation={data.recommendation}
          confidence={data.confidence}
          reason={data.reason}
          recommended_window={data.recommended_window}
        />

        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-4">
              Price Drop Probability
            </h3>

            <div className="space-y-4">
              <MetricRow
                label="Within 7 days"
                value={data.price_drop_probability.days_7}
                type="opportunity"
              />

              <MetricRow
                label="Within 14 days"
                value={data.price_drop_probability.days_14}
                type="opportunity"
              />

              <MetricRow
                label="Within 30 days"
                value={data.price_drop_probability.days_30}
                type="opportunity"
              />
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-4">
              Availability Risk
            </h3>

            <div className="space-y-4">
              <MetricRow
                label="Within 7 days"
                value={data.availability_risk.days_7}
                type="risk"
              />

              <MetricRow
                label="Within 14 days"
                value={data.availability_risk.days_14}
                type="risk"
              />

              <MetricRow
                label="Within 30 days"
                value={data.availability_risk.days_30}
                type="risk"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">
            Top Factors Behind This Recommendation
          </h3>

          <div className="space-y-3">
            {data.top_factors.map((factor, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-3">
                <p className="font-medium text-gray-900">{factor.feature}</p>
                <p className="text-sm text-gray-600">{factor.effect}</p>
              </div>
            ))}
          </div>
        </div>

        <PriceChart data={data.price_history} />

        <button
          onClick={onReset}
          className="w-full border border-gray-300 text-gray-600 py-3 rounded-lg text-sm hover:bg-gray-100"
        >
          Check another product
        </button>
      </div>
    </div>
  )
}

export default Results