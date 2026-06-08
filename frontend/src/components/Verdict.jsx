function Verdict({ recommendation, confidence, reason, recommended_window }) {
  const rec = String(recommendation || "uncertain").toLowerCase()
  const confidencePercent = Math.round((confidence || 0) * 100)

  const explanationParts =
    typeof reason === "string"
      ? reason
          .split(/(?=Price outlook:|Availability signal:|Combined recommendation:|Suggested action:)/)
          .filter(Boolean)
      : []

  const titleMap = {
    "Price outlook": "📉 Price Outlook",
    "Availability signal": "⚠️ Availability Signal",
    "Combined recommendation": "🧠 Final Decision",
    "Suggested action": "✅ Suggested Action",
  }

  const config =
    rec === "buy"
      ? {
          label: "Buy Now",
          badge: "BUY NOW",
          headline: "Buying now is the safer choice",
          subtext: "The models do not show a strong enough price-drop signal.",
          card: "bg-green-50 border-green-100 shadow-green-100",
          text: "text-green-700",
          badgeStyle: "bg-green-100 text-green-700",
          bar: "bg-green-600",
          icon: "✓",
        }
      : rec === "wait"
      ? {
          label: "Wait",
          badge: "WAIT",
          headline: "Waiting may be worth it",
          subtext: "The model sees a stronger chance of a meaningful price drop.",
          card: "bg-blue-50 border-blue-100 shadow-blue-100",
          text: "text-blue-700",
          badgeStyle: "bg-blue-100 text-blue-700",
          bar: "bg-blue-600",
          icon: "↓",
        }
      : rec === "wait_with_caution"
      ? {
          label: "Wait With Caution",
          badge: "WAIT WITH CAUTION",
          headline: "Waiting may help, but monitor the product",
          subtext:
            "There may be a price opportunity, but availability risk is not fully low.",
          card: "bg-amber-50 border-amber-100 shadow-amber-100",
          text: "text-amber-700",
          badgeStyle: "bg-amber-100 text-amber-700",
          bar: "bg-amber-500",
          icon: "!",
        }
      : rec === "wait_and_track"
      ? {
          label: "Wait & Track",
          badge: "WAIT & TRACK",
          headline: "Track this product before buying",
          subtext:
            "A longer-window opportunity may exist, but the price should be monitored actively.",
          card: "bg-indigo-50 border-indigo-100 shadow-indigo-100",
          text: "text-indigo-700",
          badgeStyle: "bg-indigo-100 text-indigo-700",
          bar: "bg-indigo-600",
          icon: "↗",
        }
      : {
          label: "Uncertain",
          badge: "UNCERTAIN",
          headline: "No strong action signal",
          subtext:
            "The model does not have enough confidence for a clear buy or wait decision.",
          card: "bg-yellow-50 border-yellow-100 shadow-yellow-100",
          text: "text-yellow-700",
          badgeStyle: "bg-yellow-100 text-yellow-700",
          bar: "bg-yellow-500",
          icon: "?",
        }

  const confidenceLabel =
    confidencePercent >= 75
      ? "High confidence"
      : confidencePercent >= 50
      ? "Moderate confidence"
      : "Low confidence"

  return (
    <section className={`rounded-3xl border shadow-lg p-6 md:p-8 ${config.card}`}>
      <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-8">
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <span
              className={`inline-flex rounded-full px-4 py-2 text-sm font-bold tracking-wide ${config.badgeStyle}`}
            >
              {config.badge}
            </span>

            {recommended_window && (
              <span className="inline-flex rounded-full bg-white/80 px-4 py-2 text-sm font-semibold text-gray-700 border border-white">
                {recommended_window}
              </span>
            )}
          </div>

          <div className="mt-6 flex items-start gap-5">
            <div
              className={`hidden sm:flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-white text-3xl font-black ${config.text}`}
            >
              {config.icon}
            </div>

            <div>
              <h2 className={`text-4xl md:text-5xl font-extrabold ${config.text}`}>
                {config.label}
              </h2>

              <p className="text-xl font-semibold text-gray-900 mt-3">
                {config.headline}
              </p>

              <p className="text-gray-600 mt-2 leading-relaxed">
                {config.subtext}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white/95 rounded-3xl border border-white p-6 w-full xl:w-80">
          <p className="text-sm font-semibold text-gray-500">
            Chance of lower price
          </p>

          <div className="flex items-end justify-between mt-2">
            <p className="text-4xl font-extrabold text-gray-900">
              {confidencePercent}%
            </p>

            <p className={`text-sm font-bold ${config.text}`}>
              {confidenceLabel}
            </p>
          </div>

          {recommended_window && (
            <p className="text-xs font-medium text-gray-500 mt-3">
              Selected window: {recommended_window}
            </p>
          )}

          <div className="mt-5">
            <div className="flex justify-between text-xs text-gray-500 mb-2">
              <span>Model probability</span>
              <span>{confidencePercent}%</span>
            </div>

            <div className="bg-gray-100 rounded-full h-2.5 overflow-hidden">
              <div
                className={`h-full rounded-full ${config.bar}`}
                style={{ width: `${Math.min(confidencePercent, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {explanationParts.length > 0 && (
        <div className="mt-8 grid md:grid-cols-2 gap-4">
          {explanationParts.map((part, index) => {
            const [title, ...rest] = part.split(":")
            const cleanTitle = title.trim()
            const body = rest.join(":").trim()

            return (
              <div
                key={index}
                className="rounded-2xl bg-white/75 border border-white p-4 h-fit"
              >
                <p className={`text-sm font-bold mb-2 ${config.text}`}>
                  {titleMap[cleanTitle] || cleanTitle}
                </p>

                <p className="text-gray-700 leading-relaxed">
                  {body || part}
                </p>
              </div>
            )
          })}
        </div>
      )}

      {explanationParts.length === 0 && reason && (
        <div className="mt-7 rounded-2xl bg-white/75 border border-white p-4">
          <p className="text-gray-700 leading-relaxed">{reason}</p>
        </div>
      )}
    </section>
  )
}

export default Verdict