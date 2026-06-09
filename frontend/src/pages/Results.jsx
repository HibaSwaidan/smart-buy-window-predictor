import { useRef, useState } from "react"
import Verdict from "../components/Verdict"
import PriceChart from "../components/PriceChart"
import TrackProductModal from "../components/TrackProductModal"
import TrackedProductsModal from "../components/TrackedProductsModal"
import { trackProduct, getTrackedProducts, stopTracking } from "../services/api"

function getRecommendationTheme(recommendation) {
  if (recommendation === "buy") {
    return {
      selectedCard: "border-green-200 bg-green-50 ring-2 ring-green-100",
      badge: "bg-green-100 text-green-700",
      bar: "bg-green-600",
      text: "text-green-700",
      label: "Low chance",
    }
  }

  if (
    recommendation === "wait" ||
    recommendation === "wait_track" ||
    recommendation === "wait_caution"
  ) {
    return {
      selectedCard: "border-blue-200 bg-blue-50 ring-2 ring-blue-100",
      badge: "bg-blue-100 text-blue-700",
      bar: "bg-blue-600",
      text: "text-blue-700",
      label:
        recommendation === "wait_caution"
          ? "Monitor availability"
          : recommendation === "wait_track"
          ? "Track actively"
          : "Good opportunity",
    }
  }

  return {
    selectedCard: "border-yellow-200 bg-yellow-50 ring-2 ring-yellow-100",
    badge: "bg-yellow-100 text-yellow-700",
    bar: "bg-yellow-500",
    text: "text-yellow-700",
    label: "Unclear signal",
  }
}

function formatRiskFlag(key) {
  const labels = {
    risk_amazon_missing_recent: "Recent Amazon price is missing",
    risk_not_amazon_source: "Current price is not from Amazon",
    risk_price_source_changed: "Price source recently changed",
    risk_offer_count_missing: "Offer count data is missing",
    risk_low_offer_count: "Low number of active offers",
    risk_offer_count_declining: "Offer count is declining",
  }

  return (
    labels[key] ||
    key
      .replace("risk_", "")
      .replaceAll("_", " ")
      .replace(/\b\w/g, (c) => c.toUpperCase())
  )
}

function HorizonCard({ prediction, isSelected }) {
  const probabilityPercent = Math.round((prediction.probability || 0) * 100)
  const theme = getRecommendationTheme(prediction.recommendation)

  return (
    <div
      className={`rounded-2xl border p-5 shadow-sm transition min-h-[270px] flex flex-col justify-between ${
        isSelected ? theme.selectedCard : "border-gray-200 bg-white"
      }`}
    >
      <div>
        <div className="flex items-start justify-between gap-3 min-h-[42px]">
          <p className="text-base font-extrabold text-gray-900">
            {prediction.horizon} days
          </p>

          <div className="flex flex-col items-end gap-2">
            {isSelected && (
              <span className="rounded-full bg-blue-600 px-3 py-1 text-[11px] font-bold text-white">
                Selected
              </span>
            )}

            <span
              className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${theme.badge}`}
            >
              {prediction.recommendation_label}
            </span>
          </div>
        </div>

        <p className={`text-4xl font-extrabold mt-4 ${theme.text}`}>
          {probabilityPercent}%
        </p>

        <p className="text-sm font-medium text-gray-500 mt-1">
          chance of a lower price
        </p>
      </div>

      <div className="mt-5">
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${theme.bar}`}
            style={{ width: `${Math.min(probabilityPercent, 100)}%` }}
          />
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <div className="rounded-xl bg-white/80 border border-gray-100 px-3 py-2">
            <p className="text-gray-500">Buy zone</p>

            <p className="font-bold text-gray-900">
              ≤ {Math.round(prediction.buy_threshold * 100)}%
            </p>
          </div>

          <div className="rounded-xl bg-white/80 border border-gray-100 px-3 py-2">
            <p className="text-gray-500">Wait zone</p>

            <p className="font-bold text-gray-900">
              ≥ {Math.round(prediction.wait_threshold * 100)}%
            </p>
          </div>
        </div>

        <p className={`text-sm font-bold mt-4 ${theme.text}`}>
          {theme.label}
        </p>
      </div>
    </div>
  )
}

function Results({ data, onReset }) {
  const [showTrackModal, setShowTrackModal] = useState(false)
  const trackingEmailRef = useRef("")
  const [showTrackedProductsModal, setShowTrackedProductsModal] = useState(false)
  const [trackedProducts, setTrackedProducts] = useState([])
  const [trackedProductsLoading, setTrackedProductsLoading] = useState(false)
  const [trackedProductsError, setTrackedProductsError] = useState("")

  const riskScore = data.availability_risk?.score ?? 0
  const riskLevel = data.availability_risk?.level || "UNKNOWN"
  const riskFlags = data.availability_risk?.flags || {}
  const activeRiskFlags = Object.entries(riskFlags).filter(
    ([, value]) => value === 1
  )
  const warningCount = activeRiskFlags.length
  const horizonPredictions = data.horizon_predictions || []

  const selectedWindow =
    data.best_horizon &&
    data.recommendation !== "buy" &&
    data.recommendation !== "uncertain"
      ? `${data.best_horizon} days`
      : data.recommendation === "buy"
      ? "Buy now"
      : "Not selected"

  const handleTrackSubmit = async (payload) => {
    return await trackProduct(payload)
  }

  const handleOpenTrackedProducts = async () => {
    const email = window.prompt("Enter the email you used for tracking:")
    if (!email) return

    trackingEmailRef.current = email
    setShowTrackedProductsModal(true)
    setTrackedProductsLoading(true)
    setTrackedProductsError("")

    try {
      const response = await getTrackedProducts(email)
      setTrackedProducts(response.items || [])
    } catch (err) {
      setTrackedProductsError(err.message || "Could not load tracked products.")
    } finally {
      setTrackedProductsLoading(false)
    }
  }

  const handleStopTracking = async (trackingId) => {
    try {
      const updated = await stopTracking(trackingId, trackingEmailRef.current)

      setTrackedProducts((currentItems) =>
        currentItems.map((item) => (item.id === trackingId ? updated : item))
      )
    } catch (err) {
      setTrackedProductsError(
        err.message || "Could not stop tracking this product."
      )
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="bg-white rounded-3xl border border-gray-200 shadow-sm p-5 md:p-6">
          <div className="grid md:grid-cols-[180px_1fr] gap-6 items-start">
            <div className="w-full h-56 md:h-48 bg-gradient-to-br from-gray-100 to-gray-50 rounded-2xl overflow-hidden flex items-center justify-center border border-gray-100">
              {data.image_url ? (
                <img
                  src={data.image_url}
                  alt={data.title}
                  className="w-full h-full object-contain p-3"
                />
              ) : (
                <span className="text-gray-400 text-sm">No image</span>
              )}
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-600">
                  {data.category}
                </span>

                <span className="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                  Smart price check
                </span>
              </div>

              <h2 className="text-2xl md:text-3xl font-extrabold text-gray-900 mt-4 leading-tight max-w-4xl">
                {data.title}
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-5">
                <div className="rounded-2xl bg-blue-50 border border-blue-100 p-4">
                  <p className="text-xs font-semibold text-blue-700">
                    Current Price
                  </p>

                  <p className="text-2xl font-extrabold text-gray-900 mt-1">
                    ${data.current_price}
                  </p>
                </div>

                <div className="rounded-2xl bg-gray-50 border border-gray-100 p-4">
                  <p className="text-xs font-semibold text-gray-500">
                    Product ASIN
                  </p>

                  <p className="text-sm font-bold text-gray-900 mt-2">
                    {data.asin}
                  </p>
                </div>

                <div className="rounded-2xl bg-indigo-50 border border-indigo-100 p-4">
                  <p className="text-xs font-semibold text-indigo-700">
                    Recommended Window
                  </p>

                  <p className="text-sm font-bold text-gray-900 mt-2">
                    {selectedWindow}
                  </p>
                </div>
              </div>

              <div className="mt-5 rounded-2xl border border-gray-200 bg-gray-50 p-4">
                <p className="text-sm text-gray-600 leading-relaxed">
                  We compare the product’s price history with current marketplace
                  signals to suggest whether buying now or waiting looks more
                  reasonable.
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

        <div className="bg-white rounded-3xl border border-gray-200 p-5 md:p-6 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h3 className="text-lg font-bold text-gray-900">
                Track this product
              </h3>

              <p className="text-sm text-gray-500 mt-1">
                Save the product and monitor it for your target price or a
                meaningful drop.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => setShowTrackModal(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-xl text-sm font-semibold hover:bg-blue-700 transition"
              >
                Start Tracking
              </button>

              <button
                onClick={handleOpenTrackedProducts}
                className="bg-white text-blue-700 border border-blue-100 px-6 py-3 rounded-xl text-sm font-semibold hover:bg-blue-50 transition"
              >
                View Tracked
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-3xl border border-gray-200 p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-sm font-semibold text-blue-600 mb-1">
              Price Outlook
            </p>

            <h3 className="text-xl font-bold text-gray-900">
              Chance of a better price
            </h3>

            <p className="text-sm text-gray-500 mt-2">
              We compare short, medium, and longer waiting windows.
            </p>
          </div>

          {horizonPredictions.length > 0 ? (
            <div className="grid md:grid-cols-3 gap-4">
              {horizonPredictions.map((prediction) => (
                <HorizonCard
                  key={prediction.key}
                  prediction={prediction}
                  isSelected={prediction.horizon === data.best_horizon}
                />
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-yellow-100 bg-yellow-50 p-5 text-sm text-yellow-800">
              Price outlook details are unavailable for this product.
            </div>
          )}
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
            <div className="flex-1">
              <p className="text-sm font-semibold text-blue-600 mb-1">
                Availability Check
              </p>

              <h3 className="text-xl font-bold text-gray-900">
                Is it safe to wait?
              </h3>

              <p className="text-sm text-gray-500 mt-2 max-w-2xl">
                We check whether waiting may be risky because of missing Amazon
                pricing, non-Amazon pricing, or weaker offer availability.
              </p>

              <div className="mt-5 grid sm:grid-cols-2 gap-3">
                {activeRiskFlags.length > 0 ? (
                  activeRiskFlags.map(([key]) => (
                    <div
                      key={key}
                      className="rounded-xl border border-blue-100 bg-blue-50 px-4 py-3"
                    >
                      <p className="text-xs font-semibold text-blue-700">
                        Warning signal
                      </p>

                      <p className="text-sm font-medium text-gray-800 mt-1">
                        {formatRiskFlag(key)}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-green-100 bg-green-50 px-4 py-3">
                    <p className="text-xs font-semibold text-green-700">
                      Looks stable
                    </p>

                    <p className="text-sm font-medium text-gray-800 mt-1">
                      No major availability warning signals were found.
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="rounded-2xl bg-blue-50 border border-blue-100 p-5 w-full lg:w-64">
              <p className="text-sm text-blue-700 font-medium">
                Availability status
              </p>

              <p className="text-3xl font-bold text-blue-700 mt-1">
                {riskLevel}
              </p>

              <p className="text-sm text-gray-600 mt-2">
                Risk score:{" "}
                <span className="font-bold text-gray-900">
                  {riskScore} / 8
                </span>
              </p>

              <p className="text-xs text-gray-500 mt-1">
                {warningCount === 0
                  ? "No warning signals detected."
                  : `${warningCount} warning signal${
                      warningCount > 1 ? "s" : ""
                    } detected. Some signals carry more weight than others.`}
              </p>

              <div className="h-2 bg-white rounded-full overflow-hidden mt-3">
                <div
                  className="h-full rounded-full bg-blue-600"
                  style={{
                    width: `${Math.min((riskScore / 8) * 100, 100)}%`,
                  }}
                />
              </div>
            </div>
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
            className="mt-5 bg-blue-600 text-white px-8 py-3 rounded-xl text-sm font-medium hover:bg-blue-700 transition"
          >
            Analyze Another Product
          </button>
        </div>

        <footer className="text-center text-xs text-gray-400 pb-4">
          <p>Smart Buy Window · Purchase Timing Intelligence</p>
        </footer>
      </div>

      {showTrackModal && (
        <TrackProductModal
          product={data}
          onClose={() => setShowTrackModal(false)}
          onSubmit={handleTrackSubmit}
        />
      )}

      {showTrackedProductsModal && (
        <TrackedProductsModal
          items={trackedProducts}
          loading={trackedProductsLoading}
          error={trackedProductsError}
          onClose={() => setShowTrackedProductsModal(false)}
          onStopTracking={handleStopTracking}
        />
      )}
    </div>
  )
}

export default Results