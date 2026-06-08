import { useState } from "react"
import Home from "./pages/Home"
import Results from "./pages/Results"
import Navbar from "./components/Navbar"
import { analyzeProduct } from "./services/api"

function buildErrorState(error) {
  const message = error?.message || "We could not analyze this product."
  const lowerMessage = message.toLowerCase()
  const status = error?.status

  if (status === 0) {
    return {
      title: "Prediction service unavailable",
      message,
      suggestion:
        "Check that the backend is running, or try again after a moment.",
    }
  }

  if (
    lowerMessage.includes("not enough price history") ||
    lowerMessage.includes("at least 365 days")
  ) {
    return {
      title: "Not enough price history",
      message,
      suggestion:
        "Try a product that has been listed for longer or has more historical price data.",
    }
  }

  if (
    lowerMessage.includes("invalid asin") ||
    lowerMessage.includes("could not extract asin") ||
    lowerMessage.includes("10-character asin")
  ) {
    return {
      title: "Invalid product identifier",
      message,
      suggestion:
        "Check the Amazon URL or paste a valid 10-character ASIN.",
    }
  }

  if (
    lowerMessage.includes("not found") ||
    lowerMessage.includes("no product") ||
    lowerMessage.includes("unable to fetch")
  ) {
    return {
      title: "Product could not be found",
      message,
      suggestion:
        "Try another ASIN or make sure the product exists on Amazon.",
    }
  }

  if (status >= 500) {
    return {
      title: "Prediction failed",
      message,
      suggestion:
        "The backend could not complete the analysis. Please try another product or retry later.",
    }
  }

  return {
    title: "We couldn't analyze this product",
    message,
    suggestion:
      "Try another ASIN or choose a product with more complete historical data.",
  }
}

function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async (input) => {
    setLoading(true)
    setError(null)

    try {
      const data = await analyzeProduct(input)
      setResult(data)
    } catch (err) {
      setError(buildErrorState(err))
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
  }

  return (
    <>
      <Navbar onHome={handleReset} />

      {result ? (
        <Results data={result} onReset={handleReset} />
      ) : (
        <Home onAnalyze={handleAnalyze} loading={loading} error={error} />
      )}
    </>
  )
}

export default App