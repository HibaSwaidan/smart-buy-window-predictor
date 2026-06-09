function TrackedProductsModal({ items, loading, error, onClose, onStopTracking }) {
  const activeItems = items.filter((item) => item.status === "active")
  const cancelledItems = items.filter((item) => item.status !== "active")
  const sortedItems = [...activeItems, ...cancelledItems]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm px-4">
      <div className="w-full max-w-3xl max-h-[85vh] overflow-hidden rounded-3xl bg-white border border-gray-200 shadow-2xl">
        <div className="p-6 border-b border-gray-100 flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-blue-600">
              Tracking Center
            </p>

            <h2 className="text-2xl font-bold text-gray-900 mt-1">
              My Tracked Products
            </h2>

            <p className="text-sm text-gray-500 mt-2">
              View products saved for price monitoring and cancel tracking items
              you no longer need.
            </p>
          </div>

          <button
            onClick={onClose}
            className="h-9 w-9 rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200"
          >
            ×
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[65vh]">
          {loading && (
            <div className="rounded-2xl border border-blue-100 bg-blue-50 p-5 text-sm text-blue-700">
              Loading tracked products...
            </div>
          )}

          {error && (
            <div className="rounded-2xl border border-red-100 bg-red-50 p-5 text-sm text-red-700">
              {error}
            </div>
          )}

          {!loading && !error && sortedItems.length === 0 && (
            <div className="rounded-2xl border border-gray-200 bg-gray-50 p-8 text-center">
              <p className="font-bold text-gray-900">
                No tracked products yet
              </p>

              <p className="text-sm text-gray-500 mt-2">
                Analyze a product and click Track This Product to start
                monitoring it.
              </p>
            </div>
          )}

          {!loading && !error && sortedItems.length > 0 && (
            <div className="space-y-4">
              {sortedItems.map((item) => {
                const isActive = item.status === "active"
                const statusLabel = isActive ? "Active" : "Cancelled"

                return (
                  <div
                    key={item.id}
                    className="rounded-2xl border border-gray-200 bg-gray-50 p-4"
                  >
                    <div className="flex flex-col md:flex-row gap-4">
                      <div className="h-24 w-24 shrink-0 rounded-xl bg-white border border-gray-100 overflow-hidden flex items-center justify-center">
                        {item.image_url ? (
                          <img
                            src={item.image_url}
                            alt={item.product_title || item.asin}
                            className="h-full w-full object-contain p-2"
                          />
                        ) : (
                          <span className="text-xs text-gray-400">
                            No image
                          </span>
                        )}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-2">
                          <span
                            className={`rounded-full px-3 py-1 text-xs font-bold ${
                              isActive
                                ? "bg-green-100 text-green-700"
                                : "bg-gray-200 text-gray-600"
                            }`}
                          >
                            {statusLabel}
                          </span>

                          <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700">
                            {item.tracking_horizon} days
                          </span>
                        </div>

                        <p className="font-bold text-gray-900 line-clamp-2">
                          {item.product_title || item.asin}
                        </p>

                        <p className="text-xs text-gray-500 mt-1">
                          ASIN: {item.asin}
                        </p>

                        <div className="grid sm:grid-cols-3 gap-3 mt-4">
                          <div className="rounded-xl bg-white border border-gray-100 p-3">
                            <p className="text-xs text-gray-500">
                              Current price
                            </p>
                            <p className="text-sm font-bold text-gray-900">
                              {item.current_price
                                ? `$${item.current_price}`
                                : "N/A"}
                            </p>
                          </div>

                          <div className="rounded-xl bg-white border border-gray-100 p-3">
                            <p className="text-xs text-gray-500">
                              Target price
                            </p>
                            <p className="text-sm font-bold text-gray-900">
                              {item.target_price
                                ? `$${item.target_price}`
                                : "Meaningful drop"}
                            </p>
                          </div>

                          <div className="rounded-xl bg-white border border-gray-100 p-3">
                            <p className="text-xs text-gray-500">
                              Last seen price
                            </p>
                            <p className="text-sm font-bold text-gray-900">
                              {item.last_seen_price
                                ? `$${item.last_seen_price}`
                                : "N/A"}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="md:w-36 flex md:flex-col gap-2">
                        <button
                          onClick={() => onStopTracking(item.id)}
                          disabled={!isActive}
                          className="w-full rounded-xl bg-red-600 px-4 py-3 text-sm font-semibold text-white hover:bg-red-700 disabled:bg-gray-300 disabled:text-gray-500"
                        >
                          {isActive ? "Stop Tracking" : "Cancelled"}
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TrackedProductsModal