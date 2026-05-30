import Verdict from "../components/Verdict"
import PriceChart from "../components/PriceChart"

function Results({ data, onReset }) {
  return (
    <div className="min-h-screen bg-gray-50 px-4 py-12">
      <div className="max-w-xl mx-auto space-y-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">{data.title}</h2>
          <p className="text-gray-500 text-sm mt-1">
            Current price: <span className="font-medium text-gray-800">${data.current_price}</span>
          </p>
        </div>

        <Verdict
          prediction={data.prediction}
          confidence={data.confidence}
          reason={data.reason}
          recommended_buy_date={data.recommended_buy_date}
        />

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