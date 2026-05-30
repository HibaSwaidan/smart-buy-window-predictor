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
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="max-w-xl w-full text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Smart Buy Window
        </h1>
        <p className="text-gray-500 mb-8">
          Paste an Amazon product URL or ASIN to find out if you should buy now or wait.
        </p>
        <div className="flex gap-2">
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
            className="bg-blue-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Home