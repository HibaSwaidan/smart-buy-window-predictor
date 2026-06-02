export const mockAnalyze = (asin) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        asin: asin,

        title: "Instant Pot Duo 7-in-1 Electric Pressure Cooker",

        category: "Home & Kitchen",

        current_price: 89.99,
        image_url: "/src/assets/hero.png",

        recommendation: "wait",

        recommended_window: "Wait up to 14 days",

        confidence: 0.82,

        price_drop_probability: {
          days_7: 0.41,
          days_14: 0.76,
          days_30: 0.69,
        },

        availability_risk: {
          days_7: 0.08,
          days_14: 0.15,
          days_30: 0.27,
        },

        reason:
        "A meaningful price drop is likely within 14 days while availability risk remains low.",

        top_factors: [
          {
            feature: "30-day rolling average",
            effect: "Current price is above its recent average",
          },
          {
            feature: "Seasonality",
            effect: "Similar products often drop before seasonal events",
          },
          {
            feature: "Offer count trend",
            effect: "Availability risk is currently low",
          },
        ],

        price_history: [
          { date: "2026-01-01", price: 99.99 },
          { date: "2026-02-01", price: 94.99 },
          { date: "2026-03-01", price: 89.99 },
          { date: "2026-04-01", price: 99.99 },
          { date: "2026-05-01", price: 89.99 },
        ],

        status: "confident_wait",
      });
    }, 1000);
  });
};