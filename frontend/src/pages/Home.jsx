import { useState } from "react"

function Home({ onAnalyze }) {
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!input.trim()) return
    setLoading(true)
    await onAnalyze(input.trim())
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mt-24">
          <h1 className="text-5xl font-bold text-gray-900 mb-3">
            Smart Buy Window
          </h1>

          <p className="text-gray-500 mb-8 text-lg">
            Paste an Amazon product URL or ASIN to find out if you should buy now or wait.
          </p>

          <div className="flex gap-2 max-w-3xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              placeholder="e.g. B07FDJMC9Q or Amazon URL"
              className="flex-1 border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2 min-w-28"
            >
              {loading && (
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            )}

              {loading ? "Analyzing" : "Analyze"}
            </button>
          </div>

          <p className="text-sm text-gray-400 mt-3">
            Example: B07FDJMC9Q
          </p>
        </div>

        <div
          id="how-it-works"
          className="mt-28 bg-white rounded-2xl shadow-sm border border-gray-200 p-8"
        >
          <h2 className="text-2xl font-bold text-center mb-8">
            How It Works
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl mb-3">🔗</div>
              <h3 className="font-semibold mb-2">Paste Product URL</h3>
              <p className="text-gray-600 text-sm">
                Enter an Amazon product URL or ASIN.
              </p>
            </div>

            <div className="text-center">
              <div className="text-4xl mb-3">📊</div>
              <h3 className="font-semibold mb-2">Analyze History</h3>
              <p className="text-gray-600 text-sm">
                We analyze historical pricing and availability patterns.
              </p>
            </div>

            <div className="text-center">
              <div className="text-4xl mb-3">💡</div>
              <h3 className="font-semibold mb-2">Get Recommendation</h3>
              <p className="text-gray-600 text-sm">
                Receive a Buy, Wait, or Uncertain recommendation.
              </p>
            </div>
          </div>
        </div>

        <div
  id="about"
  className="mt-12 bg-gradient-to-br from-blue-50 to-white rounded-2xl shadow-sm border border-blue-100 p-8"
>
  <div className="grid md:grid-cols-2 gap-10 items-center">
    <div>
      <p className="text-sm font-semibold text-blue-600 mb-2">
        About the System
      </p>

      <h2 className="text-3xl font-bold text-gray-900 mb-4">
        Smarter timing for Amazon purchases
      </h2>

      <p className="text-gray-600 leading-relaxed">
        Smart Buy Window Predictor helps shoppers decide whether to buy now
        or wait by analyzing historical price behavior and availability risk.
      </p>

      <p className="text-gray-600 leading-relaxed mt-4">
        Instead of forecasting the exact future price, the system estimates
        whether a meaningful price drop is likely within 7, 14, or 30 days.
      </p>
    </div>

    <div className="space-y-4">
      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-1">
          Price Drop Classifier
        </h3>
        <p className="text-sm text-gray-600">
          Estimates whether a meaningful discount is likely soon.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-1">
          Availability Risk Classifier
        </h3>
        <p className="text-sm text-gray-600">
          Checks whether waiting may increase the risk of stock loss.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-1">
          Buy Window Recommendation
        </h3>
        <p className="text-sm text-gray-600">
          Combines both predictions into a practical buy-now, wait, or uncertain decision.
        </p>
      </div>
    </div>
  </div>
</div>
      </div>
    </div>
  )
}

export default Home