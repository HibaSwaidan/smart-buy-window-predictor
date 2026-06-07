import { useState } from "react"

function Home({ onAnalyze }) {
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (value = input) => {
    if (!value.trim()) return
    setLoading(true)
    await onAnalyze(value.trim())
    setLoading(false)
  }

  const handleDemoClick = () => {
    const demoAsin = "B07FDJMC9Q"
    setInput(demoAsin)
    handleSubmit(demoAsin)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 px-4 py-12">
      <div className="max-w-6xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center mt-16">
          <div>
            <div className="inline-flex items-center rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-700 mb-6">
              ML-Powered Amazon Price Timing Assistant
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-5">
              Smart shopping starts with better timing.
            </h1>

            <p className="text-lg text-gray-600 leading-relaxed mb-8">
              Paste an Amazon product URL or ASIN and get a data-driven recommendation
              on whether to buy now, wait, or stay uncertain based on price-drop
              probability and availability risk.
            </p>

            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                  placeholder="e.g. B07FDJMC9Q or Amazon product URL"
                  className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <button
                  onClick={() => handleSubmit()}
                  disabled={loading}
                  className="bg-blue-600 text-white px-6 py-3 rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2 min-w-32"
                >
                  {loading && (
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  )}

                  {loading ? "Analyzing" : "Analyze"}
                </button>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-4">
                <p className="text-sm text-gray-400">
                  Example: B07FDJMC9Q
                </p>

                <button
                  onClick={handleDemoClick}
                  disabled={loading}
                  className="text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  Try demo product →
                </button>
              </div>
            </div>

            {loading && (
  <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50">

    <div className="bg-white rounded-3xl shadow-xl border border-gray-200 p-8 w-[350px]">

      <div className="flex justify-center mb-5">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <h3 className="text-lg font-bold text-center text-gray-900 mb-4">
        Analyzing Product
      </h3>

      <div className="space-y-2 text-sm text-gray-600">
        <p>✓ Reading product identifier</p>
        <p>✓ Analyzing price history</p>
        <p>✓ Evaluating availability risk</p>
        <p>✓ Generating recommendation</p>
      </div>

    </div>

  </div>
)}

            <div className="grid sm:grid-cols-3 gap-3 mt-6">
              <div className="bg-white/70 border border-blue-100 rounded-xl px-4 py-3 text-sm text-gray-700">
                ✓ Price history analysis
              </div>

              <div className="bg-white/70 border border-blue-100 rounded-xl px-4 py-3 text-sm text-gray-700">
                ✓ Availability risk
              </div>

              <div className="bg-white/70 border border-blue-100 rounded-xl px-4 py-3 text-sm text-gray-700">
                ✓ ML recommendation
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-gray-200 shadow-xl p-6">
            <div className="flex items-start justify-between mb-6">
              <div>
                <p className="text-sm text-gray-500">Demo Product</p>
                <h2 className="text-xl font-bold text-gray-900 mt-1">
                  Instant Pot Duo 7-in-1
                </h2>
              </div>

              <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-700">
                WAIT
              </span>
            </div>

            <div className="rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 p-5 mb-5">
              <div className="text-center">
                <p className="text-sm text-gray-500 mb-2">
                  Recommended Window
                </p>

                <p className="text-3xl font-bold text-blue-600">
                  Wait up to 14 days
                </p>

                <p className="text-sm text-gray-600 mt-3">
                  82% confidence based on historical pricing and availability signals.
                </p>
              </div>

              <div className="mt-5 h-3 bg-white rounded-full overflow-hidden">
                <div className="h-full w-[82%] bg-blue-600 rounded-full"></div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-2xl border border-gray-200 p-4">
                <p className="text-sm text-gray-500">Price Drop</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">76%</p>
                <p className="text-xs text-gray-500 mt-1">within 14 days</p>
              </div>

              <div className="rounded-2xl border border-gray-200 p-4">
                <p className="text-sm text-gray-500">Availability Risk</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">15%</p>
                <p className="text-xs text-gray-500 mt-1">within 14 days</p>
              </div>
            </div>

            <div className="mt-5 rounded-2xl border border-gray-200 p-4">
              <p className="font-semibold text-gray-900 mb-2">
                Top signal
              </p>

              <p className="text-sm text-gray-600">
                Current price is above its recent 30-day average, while availability risk remains low.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-20 bg-white rounded-3xl border border-gray-200 shadow-sm p-10">
          <div className="text-center mb-10">
            <p className="text-sm font-semibold text-blue-600 mb-2">
              Why Smart Buy Window?
            </p>

            <h2 className="text-3xl font-bold text-gray-900">
              Built to support smarter purchase decisions
            </h2>

            <p className="text-gray-500 mt-3 max-w-2xl mx-auto">
              The system combines price behavior, availability signals, and confidence
              scoring to help shoppers decide whether to buy now or wait.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-gray-50 rounded-2xl border border-gray-200 p-6 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-blue-100 flex items-center justify-center text-2xl mb-5">
                📉
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Predict Discounts
              </h3>

              <p className="text-gray-600 leading-relaxed">
                Estimate whether a meaningful price drop is likely within the next
                7, 14, or 30 days.
              </p>
            </div>

            <div className="bg-gray-50 rounded-2xl border border-gray-200 p-6 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-green-100 flex items-center justify-center text-2xl mb-5">
                📦
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Track Availability
              </h3>

              <p className="text-gray-600 leading-relaxed">
                Estimate the risk of waiting too long and missing a product due to
                availability changes.
              </p>
            </div>

            <div className="bg-gray-50 rounded-2xl border border-gray-200 p-6 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-indigo-100 flex items-center justify-center text-2xl mb-5">
                🤖
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Explain Decisions
              </h3>

              <p className="text-gray-600 leading-relaxed">
                Show confidence levels and key model signals so users understand why
                the recommendation is Buy, Wait, or Uncertain.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-16 bg-white rounded-3xl border border-gray-200 shadow-sm p-10">
          <div className="text-center mb-10">
            <p className="text-sm font-semibold text-blue-600 mb-2">
              Who Benefits Most?
            </p>

            <h2 className="text-3xl font-bold text-gray-900">
              Designed for smarter online shoppers
            </h2>

            <p className="text-gray-500 mt-3 max-w-2xl mx-auto">
              Smart Buy Window helps different types of shoppers make more confident,
              data-informed purchase timing decisions.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-gray-50 rounded-2xl border border-gray-200 p-6 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-blue-100 flex items-center justify-center text-2xl mb-5">
                🛒
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Everyday Shoppers
              </h3>

              <p className="text-gray-600 leading-relaxed">
                Decide whether to buy now or wait without manually tracking product
                prices across time.
              </p>
            </div>

            <div className="bg-gray-50 rounded-2xl border border-gray-200 p-6 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-pink-100 flex items-center justify-center text-2xl mb-5">
                🎯
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Deal Seekers
              </h3>

              <p className="text-gray-600 leading-relaxed">
                Identify products that may receive meaningful discounts within the
                next 7, 14, or 30 days.
              </p>
            </div>

            <div className="bg-gray-50 rounded-2xl border border-gray-200 p-6 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-14 h-14 rounded-2xl bg-amber-100 flex items-center justify-center text-2xl mb-5">
                📦
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Frequent Online Buyers
              </h3>

              <p className="text-gray-600 leading-relaxed">
                Balance possible savings with the risk that a product may become
                unavailable if they wait too long.
              </p>
            </div>
          </div>
        </div>

        <div
          id="how-it-works"
          className="mt-16 bg-white rounded-3xl shadow-sm border border-gray-200 p-8"
        >
          <div className="text-center mb-10">
            <p className="text-sm font-semibold text-blue-600 mb-2">
              Simple Workflow
            </p>

            <h2 className="text-3xl font-bold text-gray-900">
              How It Works
            </h2>

            <p className="text-gray-500 mt-3">
              From product link to recommendation in four steps.
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-5">
            <div className="relative bg-blue-50 rounded-2xl border border-blue-100 p-5 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold mb-4">
                1
              </div>

              <h3 className="font-semibold text-gray-900 mb-2">
                Input Product
              </h3>

              <p className="text-sm text-gray-600">
                Paste an Amazon product URL or ASIN.
              </p>
            </div>

            <div className="relative bg-white rounded-2xl border border-gray-200 p-5 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold mb-4">
                2
              </div>

              <h3 className="font-semibold text-gray-900 mb-2">
                Analyze History
              </h3>

              <p className="text-sm text-gray-600">
                Review price movement, offer count, and availability signals.
              </p>
            </div>

            <div className="relative bg-white rounded-2xl border border-gray-200 p-5 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold mb-4">
                3
              </div>

              <h3 className="font-semibold text-gray-900 mb-2">
                Run ML Models
              </h3>

              <p className="text-sm text-gray-600">
                Estimate price-drop probability and availability risk.
              </p>
            </div>

            <div className="relative bg-indigo-50 rounded-2xl border border-indigo-100 p-5 hover:-translate-y-1 hover:shadow-md transition-all duration-300">
              <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold mb-4">
                4
              </div>

              <h3 className="font-semibold text-gray-900 mb-2">
                Get Recommendation
              </h3>

              <p className="text-sm text-gray-600">
                Receive a Buy, Wait, or Uncertain decision with confidence.
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

        <footer className="mt-12">
          <div className="grid lg:grid-cols-3 gap-4">
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
              <div className="border-b border-gray-100 h-14 mb-4 flex items-center">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center text-base font-bold">
                    SB
                  </div>

                  <div>
                    <h3 className="text-base font-semibold text-gray-900">
                      Smart Buy Window
                    </h3>

                    <p className="text-[11px] text-gray-500">
                      Purchase Timing Intelligence
                    </p>
                  </div>
                </div>
              </div>

              <p className="text-xs text-gray-600 leading-6">
                Helping shoppers make smarter buying decisions through
                price-history analysis, availability forecasting, and
                confidence-based recommendations.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
              <div className="border-b border-gray-100 h-14 mb-4 flex items-center">
                <h3 className="text-base font-semibold text-gray-900">
                  Explore
                </h3>
              </div>

              <div className="space-y-2">
                <a
                  href="#how-it-works"
                  className="block text-xs text-gray-600 hover:text-blue-600 transition"
                >
                  How It Works
                </a>

                <a
                  href="#about"
                  className="block text-xs text-gray-600 hover:text-blue-600 transition"
                >
                  About
                </a>

                <button
                  onClick={handleDemoClick}
                  className="text-left text-xs text-gray-600 hover:text-blue-600 transition"
                >
                  Try Demo Product
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4">
              <div className="border-b border-gray-100 h-14 mb-4 flex items-center">
                <h3 className="text-base font-semibold text-gray-900">
                  Recommendations
                </h3>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-3 text-xs text-gray-600">
                  <span className="w-2.5 h-2.5 rounded-full bg-green-500"></span>
                  Buy Now
                </div>

                <div className="flex items-center gap-3 text-xs text-gray-600">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                  Wait
                </div>

                <div className="flex items-center gap-3 text-xs text-gray-600">
                  <span className="w-2.5 h-2.5 rounded-full bg-yellow-500"></span>
                  Uncertain
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-200 mt-6 pt-4 text-center">
            <p className="text-xs text-gray-400">
              © 2026 Smart Buy Window Predictor. All rights reserved.
            </p>
          </div>
        </footer>
        <button
  onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
  className="fixed bottom-6 right-6 w-12 h-12 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 hover:scale-105 transition-all duration-300"
>
  ↑
</button>
      </div>
    </div>
  )
}

export default Home