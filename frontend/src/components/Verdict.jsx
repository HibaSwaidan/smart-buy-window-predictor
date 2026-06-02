function Verdict({ recommendation, confidence, reason, recommended_window }) {
  const isBuy = recommendation === "buy"
  const isWait = recommendation === "wait"

  const confidencePercent = Math.round(confidence * 100)

  const bgColor = isBuy
    ? "bg-green-50"
    : isWait
    ? "bg-blue-50"
    : "bg-yellow-50"

  const textColor = isBuy
    ? "text-green-600"
    : isWait
    ? "text-blue-600"
    : "text-yellow-600"

  const barColor = isBuy
    ? "bg-green-600"
    : isWait
    ? "bg-blue-600"
    : "bg-yellow-500"

  const label = isBuy ? "Buy Now" : isWait ? "Wait" : "Uncertain"

  return (
    <div className={`rounded-2xl p-8 text-center border border-gray-200 ${bgColor}`}>
      <div className={`text-5xl font-bold mb-2 ${textColor}`}>
        {label}
      </div>

      <div className="text-gray-500 text-lg mb-3">
        {confidencePercent}% confidence
      </div>

      <div className="max-w-md mx-auto bg-white rounded-full h-3 mb-5 overflow-hidden border border-gray-200">
        <div
          className={`h-full rounded-full ${barColor}`}
          style={{ width: `${confidencePercent}%` }}
        />
      </div>

      {recommended_window && (
        <p className="text-gray-900 font-medium mb-3">
          {recommended_window}
        </p>
      )}

      <p className="text-gray-700">{reason}</p>
    </div>
  )
}

export default Verdict