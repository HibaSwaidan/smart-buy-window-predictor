import Verdict from "../components/Verdict"
import PriceChart from "../components/PriceChart"

function getRecommendationTheme(recommendation) {
  if (recommendation === "buy") {
    return "bg-green-50 border-green-100 text-green-700"
  }

  if (recommendation === "wait" || recommendation === "wait_track") {
    return "bg-blue-50 border-blue-100 text-blue-700"
  }

  if (recommendation === "wait_caution") {
    return "bg-amber-50 border-amber-100 text-amber-700"
  }

  return "bg-yellow-50 border-yellow-100 text-yellow-700"
}

function HorizonCard({ prediction }) {
  const probabilityPercent = Math.round((prediction.probability || 0) * 100)
  const theme = getRecommendationTheme(prediction.recommendation)

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-gray-500">
            {prediction.horizon}-day outlook
          </p>

          <p className="text-3xl font-bold text-gray-900 mt-2">
            {probabilityPercent}%
          </p>

          <p className="text-xs text-gray-500 mt-1">
            probability of meaningful price drop
          </p>
        </div>

        <span
          className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${theme}`}
        >
          {prediction.recommendation_label}
        </span>
      </div>

      <div className="mt-5">
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full bg-blue-600"
            style={{ width: `${Math.min(probabilityPercent, 100)}%` }}
          />
        </div>

        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span>Buy zone ≤ {Math.round(prediction.buy_threshold * 100)}%</span>
          <span>Wait zone ≥ {Math.round(prediction.wait_threshold * 100)}%</span>
        </div>
      </div>

      <p className="text-sm text-gray-600 leading-relaxed mt-4">
        {prediction.explanation?.[0] ||
          "This horizon estimates the chance of a meaningful price drop within the selected window."}
      </p>
    </div>
  )
}

function ExplanationCard({ text, index }) {
  const labels = [
    "Price outlook",
    "Availability signal",
    "Combined recommendation",
    "Suggested action",
  ]

  return (
    <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 hover:bg-white hover:shadow-sm transition">
      <span className="inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700 mb-4">
        {labels[index] || `Step ${index + 1}`}
      </span>

      <p className="text-sm text-gray-700 leading-relaxed">{text}</p>
    </div>
  )
}

function Results({ data, onReset }) {
  const riskScore = data.availability_risk?.score ?? 0
  const riskLevel = data.availability_risk?.level || "UNKNOWN"
  const horizonPredictions = data.horizon_predictions || []

  const windowLabel =
    data.recommendation === "buy"
      ? "All windows support buying now"
      : data.recommendation === "uncertain"
      ? "No confident window selected"
      : data.best_horizon
      ? `${data.best_horizon} days`
      : "Not selected"

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="max-w-5xl mx-auto space-y-6">
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
                  Multi-Horizon Analysis
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
                    Recommendation Scope
                  </p>

                  <p className="text-sm font-semibold text-gray-900 mt-2">
                    {windowLabel}
                  </p>
                </div>
              </div>

              <div className="mt-5 rounded-2xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600 leading-relaxed">
                  This result combines three price-drop models with an
                  availability-risk layer to support a practical buy-now versus
                  wait decision.
                </p>
              </div>
            </div>
          </div>
        </div>

        <Verdict
          recommendation={data.recommendation}
          recommendationLabel={data.recommendation_label}
          confidence={data.confidence}
          reason={data.reason}
          recommended_window={data.recommended_window}
          bestHorizon={data.best_horizon}
        />

        <div className="bg-white rounded-3xl border border-gray-200 p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-sm font-semibold text-blue-600 mb-1">
              Multi-Horizon Price Outlook
            </p>

            <h3 className="text-xl font-bold text-gray-900">
              Price-drop probability by waiting window
            </h3>

            <p className="text-sm text-gray-500 mt-2">
              Each window uses its own trained model and recommendation
              thresholds.
            </p>
          </div>

          {horizonPredictions.length > 0 ? (
            <div className="grid md:grid-cols-3 gap-4">
              {horizonPredictions.map((prediction) => (
                <HorizonCard key={prediction.key} prediction={prediction} />
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-yellow-100 bg-yellow-50 p-5 text-sm text-yellow-800">
              Multi-horizon predictions were not returned by the API. Check that
              the frontend is connected to the V2.1 backend.
            </div>
          )}
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-5">
            <div>
              <p className="text-sm font-semibold text-blue-600 mb-1">
                Availability Risk
              </p>

              <h3 className="text-xl font-bold text-gray-900">
                Marketplace waiting risk
              </h3>

              <p className="text-sm text-gray-500 mt-2 max-w-2xl">
                This signal estimates whether waiting may be risky because of
                Amazon price availability, offer-count behaviour, or recent
                price-source changes.
              </p>
            </div>

            <div className="rounded-2xl bg-blue-50 border border-blue-100 p-5 min-w-[220px]">
              <p className="text-sm text-blue-700 font-medium">
                Current risk level
              </p>

              <p className="text-3xl font-bold text-blue-700 mt-1">
                {riskLevel}
              </p>

              <p className="text-sm text-gray-600 mt-2">
                Risk score: {riskScore} / 8
              </p>

              <div className="h-2 bg-white rounded-full overflow-hidden mt-3">
                <div
                  className="h-full rounded-full bg-green-500"
                  style={{
                    width: `${Math.min((riskScore / 8) * 100, 100)}%`,
                  }}
                />
              </div>
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
              The final decision combines the selected price window with the
              availability-risk signal.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {(data.explanation || []).map((item, index) => (
              <ExplanationCard key={index} text={item} index={index} />
            ))}
          </div>
        </div>

        <PriceChart data={data.price_history} />

        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-3xl border border-blue-100 p-8 text-center shadow-sm">
          <h3 className="text-lg font-bold text-gray-900">
            Want to analyze another product?
          </h3>

          <p className="text-sm text-gray-500 mt-2">
            Paste a different Amazon URL or ASIN to compare another buying
            decision.
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