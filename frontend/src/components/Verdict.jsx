function Verdict({ recommendation, confidence, reason, recommended_window }) {
  const isBuy = recommendation === "buy"
  const isWait = recommendation === "wait"

  const confidencePercent = Math.round(confidence * 100)

  const label = isBuy ? "Buy Now" : isWait ? "Wait" : "Uncertain"

  const theme = isBuy
    ? {
        card: "bg-green-50 border-green-100 shadow-green-100",
        text: "text-green-700",
        badge: "bg-green-100 text-green-700",
        bar: "bg-green-600",
        glow: "shadow-green-100",
      }
    : isWait
    ? {
        card: "bg-blue-50 border-blue-100 shadow-blue-100",
        text: "text-blue-700",
        badge: "bg-blue-100 text-blue-700",
        bar: "bg-blue-600",
        glow: "shadow-blue-100",
      }
    : {
        card: "bg-yellow-50 border-yellow-100 shadow-yellow-100",
        text: "text-yellow-700",
        badge: "bg-yellow-100 text-yellow-700",
        bar: "bg-yellow-500",
        glow: "shadow-yellow-100",
      }

  const confidenceLabel =
    confidencePercent >= 75
      ? "High Confidence"
      : confidencePercent >= 50
      ? "Moderate Confidence"
      : "Low Confidence"

  return (
    <div
      className={`rounded-3xl p-8 border shadow-lg ${theme.card} ${theme.glow}`}
    >
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
        <div>
          <span
            className={`inline-flex rounded-full px-4 py-2 text-sm font-semibold ${theme.badge}`}
          >
            {label.toUpperCase()}
          </span>

          <h2 className={`text-5xl font-bold mt-5 ${theme.text}`}>
            {label}
          </h2>

          {recommended_window && (
            <p className="text-gray-900 font-semibold mt-4">
              {recommended_window}
            </p>
          )}
        </div>

        <div className="bg-white/80 rounded-2xl border border-white p-5 min-w-[220px]">
          <p className="text-sm text-gray-500">
            Model Confidence
          </p>

          <p className="text-3xl font-bold text-gray-900 mt-1">
            {confidencePercent}%
          </p>

          <p className={`text-sm font-medium mt-1 ${theme.text}`}>
            {confidenceLabel}
          </p>
        </div>
      </div>

      <div className="mt-8">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>Confidence level</span>
          <span>{confidencePercent}%</span>
        </div>

        <div className="bg-white rounded-full h-3 overflow-hidden border border-gray-100">
          <div
            className={`h-full rounded-full ${theme.bar} transition-all duration-700 ease-out`}
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
      </div>

      <p className="text-gray-700 leading-relaxed mt-6">
        {reason}
      </p>
    </div>
  )
}

export default Verdict