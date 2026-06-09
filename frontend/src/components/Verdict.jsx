function Verdict({ recommendation, confidence, reason, recommended_window }) {
  const rec = String(recommendation || "uncertain").trim().toLowerCase()
  const confidencePercent = Math.round((confidence || 0) * 100)

  const explanationParts =
    typeof reason === "string"
      ? reason
          .split(
            /(?=Price outlook:|Availability signal:|Combined recommendation:|Suggested action:)/
          )
          .filter(Boolean)
      : []

  const titleMap = {
    "Price outlook": "Price outlook",
    "Availability signal": "Availability check",
    "Combined recommendation": "Final recommendation",
    "Suggested action": "What to do next",
  }

  const config =
    rec === "buy"
      ? {
          label: "Buy Now",
          badge: "BUY NOW",
          headline: "This looks like a reasonable time to buy",
          subtext: "The chance of a better price soon appears low.",
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
          headline: "Waiting may get you a better price",
          subtext: "The price history suggests a stronger chance of a lower price.",
          card: "bg-blue-50 border-blue-100 shadow-blue-100",
          text: "text-blue-700",
          badgeStyle: "bg-blue-100 text-blue-700",
          bar: "bg-blue-600",
          icon: "↓",
        }
      : rec === "wait_caution"
      ? {
          label: "Wait with Caution",
          badge: "WAIT WITH CAUTION",
          headline: "Waiting may help, but keep an eye on availability",
          subtext:
            "The price opportunity is promising, but the product shows some availability warning signs.",
          card: "bg-blue-50 border-blue-100 shadow-blue-100",
          text: "text-blue-700",
          badgeStyle: "bg-blue-100 text-blue-700",
          bar: "bg-blue-600",
          icon: "!",
        }
      : rec === "wait_track"
      ? {
          label: "Wait and Track",
          badge: "WAIT AND TRACK",
          headline: "Track the product before buying",
          subtext:
            "A better price may appear in the longer window, so active monitoring is recommended.",
          card: "bg-blue-50 border-blue-100 shadow-blue-100",
          text: "text-blue-700",
          badgeStyle: "bg-blue-100 text-blue-700",
          bar: "bg-blue-600",
          icon: "↗",
        }
      : {
          label: "Uncertain",
          badge: "UNCERTAIN",
          headline: "There is no clear buy-or-wait signal",
          subtext:
            "The product does not show enough evidence for a strong recommendation right now.",
          card: "bg-yellow-50 border-yellow-100 shadow-yellow-100",
          text: "text-yellow-700",
          badgeStyle: "bg-yellow-100 text-yellow-700",
          bar: "bg-yellow-500",
          icon: "?",
        }

  const confidenceLabel =
    confidencePercent >= 75
      ? "Strong signal"
      : confidencePercent >= 50
      ? "Moderate signal"
      : "Weak signal"

  return (
    <section className={`rounded-3xl border shadow-md p-6 md:p-8 ${config.card}`}>
      <div className="grid lg:grid-cols-[1fr_260px] gap-8 items-center">
        <div>
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

        <div className="bg-white/95 rounded-3xl border border-white p-6">
          <p className="text-sm font-semibold text-gray-500">
            Chance of a lower price
          </p>

          <div className="flex items-end justify-between mt-2">
            <p className="text-4xl font-extrabold text-gray-900">
              {confidencePercent}%
            </p>

            <p className={`text-sm font-bold ${config.text}`}>
              {confidenceLabel}
            </p>
          </div>

          <div className="mt-5">
            <div className="flex justify-between text-xs text-gray-500 mb-2">
              <span>Price signal</span>
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