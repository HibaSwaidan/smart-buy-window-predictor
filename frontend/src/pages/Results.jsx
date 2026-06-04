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
        <div className="bg-white rounded-3xl border border-gray-200 shadow-md p-6">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="w-full md:w-44 h-56 md:h-44 bg-gradient-to-br from-gray-100 to-gray-50 rounded-2xl overflow-hidden flex items-center justify-center border border-gray-100 shadow-sm">
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

            <div className="flex-1 w-full">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600">
                  {data.category}
                </span>

                <span className="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                  Historical Analysis
                </span>
              </div>

              <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 mt-4 leading-tight">
                {data.title}
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-5">
                <div className="rounded-2xl bg-blue-50 border border-blue-100 p-4">
                  <p className="text-xs font-medium text-blue-700">
                    Current Price
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    ${data.current_price}
                  </p>
                </div>

                <div className="rounded-2xl bg-gray-50 border border-gray-100 p-4">
                  <p className="text-xs font-medium text-gray-500">
                    Product ASIN
                  </p>
                  <p className="text-sm font-semibold text-gray-900 mt-2">
                    {data.asin}
                  </p>
                </div>

                <div className="rounded-2xl bg-green-50 border border-green-100 p-4">
                  <p className="text-xs font-medium text-green-700">
                    Analysis Type
                  </p>
                  <p className="text-sm font-semibold text-gray-900 mt-2">
                    Buy Window
                  </p>
                </div>
              </div>

              <div className="mt-5 rounded-2xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600 leading-relaxed">
                  This result combines price-drop probability, availability risk,
                  and historical product signals to estimate whether it is better
                  to buy now or wait.
                </p>
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
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">
                Price Drop Probability
              </h3>

              <span className="text-xs font-medium px-2 py-1 rounded-full bg-green-100 text-green-700">
                Opportunity
              </span>
            </div>

            <div className="mb-5 rounded-xl bg-green-50 border border-green-100 p-4">
              <p className="text-sm text-green-700 font-medium">
                Highest probability window
              </p>

              <p className="text-2xl font-bold text-green-700 mt-1">
                14 Days
              </p>
            </div>

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
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">
                Availability Risk
              </h3>

              <span className="text-xs font-medium px-2 py-1 rounded-full bg-yellow-100 text-yellow-700">
                Risk
              </span>
            </div>

            <div className="mb-5 rounded-xl bg-blue-50 border border-blue-100 p-4">
              <p className="text-sm text-blue-700 font-medium">
                Lowest risk window
              </p>

              <p className="text-2xl font-bold text-blue-700 mt-1">
                7 Days
              </p>
            </div>

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

        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-sm font-semibold text-blue-600 mb-1">
              Explainable Recommendation
            </p>

            <h3 className="text-xl font-bold text-gray-900">
              Why this recommendation?
            </h3>

            <p className="text-sm text-gray-500 mt-2">
              These are the strongest signals influencing the model's decision.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            {data.top_factors.map((factor, index) => (
              <div
                key={index}
                className="rounded-xl border border-gray-200 bg-gray-50 p-4 hover:bg-white hover:shadow-sm transition"
              >
                <span className="inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700 mb-4">
                  Signal {index + 1}
                </span>

                <p className="font-semibold text-gray-900">
                  {factor.feature}
                </p>

                <p className="text-sm text-gray-600 mt-2 leading-relaxed">
                  {factor.effect}
                </p>
              </div>
            ))}
          </div>
        </div>

        <PriceChart data={data.price_history} />

        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-3xl border border-blue-100 p-8 text-center shadow-sm">
          <h3 className="text-lg font-bold text-gray-900">
            Want to analyze another product?
          </h3>

          <p className="text-sm text-gray-500 mt-2">
            Paste a different Amazon URL or ASIN to compare another buying decision.
          </p>

          <button
            onClick={onReset}
            className="mt-5 bg-blue-600 text-white px-8 py-3 rounded-xl text-sm font-medium hover:bg-blue-700 hover:-translate-y-0.5 transition-all duration-300 shadow-sm"
          >
            Analyze Another Product
          </button>
        </div>
      </div>
    </div>
  )
}

export default Results