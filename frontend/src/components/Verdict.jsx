function Verdict({ prediction, confidence, reason, recommended_buy_date }) {
  const isBuy = prediction === "buy"

  return (
    <div className={`rounded-2xl p-8 text-center ${isBuy ? "bg-green-50" : "bg-red-50"}`}>
      <div className={`text-6xl font-bold mb-2 ${isBuy ? "text-green-600" : "text-red-500"}`}>
        {isBuy ? "Buy Now" : "Wait"}
      </div>
      <div className="text-gray-500 text-lg mb-4">
        {Math.round(confidence * 100)}% confidence
      </div>
      <p className="text-gray-700">{reason}</p>
      {!isBuy && recommended_buy_date && (
        <p className="mt-3 text-sm text-gray-500">
          Recommended buy date: <span className="font-medium">{recommended_buy_date}</span>
        </p>
      )}
    </div>
  )
}

export default Verdict