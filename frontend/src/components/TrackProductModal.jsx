import { useState } from "react"

function TrackProductModal({ product, onClose, onSubmit }) {
  const [email, setEmail] = useState("")
  const [targetPrice, setTargetPrice] = useState("")
  const [trackingHorizon, setTrackingHorizon] = useState(product.best_horizon || 14)
  const [notifyOnMeaningfulDrop, setNotifyOnMeaningfulDrop] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [successMessage, setSuccessMessage] = useState("")

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setSuccessMessage("")
    setSaving(true)

    try {
      const payload = {
        asin: product.asin,
        email,
        product_title: product.title,
        image_url: product.image_url,
        current_price: product.current_price,
        target_price: targetPrice ? Number(targetPrice) : null,
        tracking_horizon: Number(trackingHorizon),
        notify_on_meaningful_drop: notifyOnMeaningfulDrop,
      }

      const response = await onSubmit(payload)
      setSuccessMessage(
        response?.message ||
          "Tracking request saved. You will be notified when this product matches your condition."
      )
    } catch (err) {
      setError(err.message || "Tracking request could not be saved.")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm px-4">
      <div className="w-full max-w-lg rounded-3xl bg-white border border-gray-200 shadow-2xl overflow-hidden">
        <div className="p-6 border-b border-gray-100 flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-blue-600">
              Price Tracking
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mt-1">
              Track this product
            </h2>

            <p className="text-sm text-gray-500 mt-2">
              We will save this product so it can be checked later for a meaningful price drop.
            </p>
          </div>

          <button
            onClick={onClose}
            className="h-9 w-9 rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          <div className="flex gap-4 rounded-2xl bg-gray-50 border border-gray-100 p-4 mb-5">
            <div className="h-20 w-20 rounded-xl bg-white border border-gray-100 overflow-hidden flex items-center justify-center">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.title}
                  className="h-full w-full object-contain p-2"
                />
              ) : (
                <span className="text-xs text-gray-400">No image</span>
              )}
            </div>

            <div className="min-w-0">
              <p className="text-sm font-bold text-gray-900 line-clamp-2">
                {product.title}
              </p>

              <p className="text-sm text-gray-500 mt-1">
                ASIN: {product.asin}
              </p>

              <p className="text-sm font-semibold text-blue-700 mt-1">
                Current price: ${product.current_price}
              </p>
            </div>
          </div>

          {successMessage ? (
            <div className="rounded-2xl border border-green-100 bg-green-50 p-5">
              <p className="text-sm font-bold text-green-700">
                Tracking request saved
              </p>

              <p className="text-sm text-green-700 mt-2 leading-relaxed">
                {successMessage}
              </p>

              <button
                onClick={onClose}
                className="mt-5 w-full rounded-xl bg-green-600 px-5 py-3 text-sm font-semibold text-white hover:bg-green-700"
              >
                Done
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Email address
                </label>

                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Target price optional
                </label>

                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(e.target.value)}
                  placeholder={`e.g. ${Math.max((product.current_price || 0) - 10, 1).toFixed(2)}`}
                  className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <p className="text-xs text-gray-500 mt-2">
                  Leave empty to track meaningful price drops based on the model.
                </p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Tracking window
                </label>

                <div className="grid grid-cols-3 gap-2">
                  {[7, 14, 30].map((days) => (
                    <button
                      type="button"
                      key={days}
                      onClick={() => setTrackingHorizon(days)}
                      className={`rounded-xl border px-4 py-3 text-sm font-semibold ${
                        Number(trackingHorizon) === days
                          ? "border-blue-600 bg-blue-50 text-blue-700"
                          : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50"
                      }`}
                    >
                      {days} days
                    </button>
                  ))}
                </div>
              </div>

              <label className="flex items-start gap-3 rounded-2xl border border-gray-200 bg-gray-50 p-4">
                <input
                  type="checkbox"
                  checked={notifyOnMeaningfulDrop}
                  onChange={(e) => setNotifyOnMeaningfulDrop(e.target.checked)}
                  className="mt-1"
                />

                <span>
                  <span className="block text-sm font-semibold text-gray-900">
                    Notify me on meaningful price drop
                  </span>

                  <span className="block text-xs text-gray-500 mt-1">
                    Recommended for wait and 30-day tracking decisions.
                  </span>
                </span>
              </label>

              {error && (
                <div className="rounded-xl border border-red-100 bg-red-50 p-4 text-sm text-red-700">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={saving}
                className="w-full rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? "Saving tracking request..." : "Save tracking request"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export default TrackProductModal