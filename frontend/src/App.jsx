import { useState } from "react"
import Home from "./pages/Home"
import Results from "./pages/Results"
import Navbar from "./components/Navbar"
import { mockAnalyze } from "./services/mockData"

function App() {
  const [result, setResult] = useState(null)

  const handleAnalyze = async (input) => {
    const data = await mockAnalyze(input)
    setResult(data)
  }

  const handleReset = () => setResult(null)

  return (
  <>
    <Navbar onHome={handleReset} />

    {result ? (
      <Results data={result} onReset={handleReset} />
    ) : (
      <Home onAnalyze={handleAnalyze} />
    )}
  </>
)
}

export default App