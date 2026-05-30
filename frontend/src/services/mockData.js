export const mockAnalyze = (asin) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        asin: asin,
        title: "Instant Pot Duo 7-in-1 Electric Pressure Cooker",
        current_price: 89.99,
        prediction: "wait",
        confidence: 0.82,
        reason: "Price likely to drop within 14 days based on historical patterns",
        price_history: [
          { date: "2026-01-01", price: 99.99 },
          { date: "2026-02-01", price: 94.99 },
          { date: "2026-03-01", price: 89.99 },
          { date: "2026-04-01", price: 99.99 },
          { date: "2026-05-01", price: 89.99 },
        ],
        recommended_buy_date: "2026-06-10"
      })
    }, 1000)
  })
}