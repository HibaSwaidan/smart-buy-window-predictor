function Navbar({ onHome }) {
  return (
    <nav className="sticky top-0 z-50 backdrop-blur-md bg-white/80 border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        
        <button
          onClick={onHome}
          className="flex items-center gap-3 hover:opacity-90 transition"
        >
          <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold">
            SB
          </div>

          <div className="text-left">
            <h1 className="text-lg font-bold text-gray-900">
              Smart Buy Window
            </h1>

            <p className="text-xs text-gray-500">
              Purchase Timing Intelligence
            </p>
          </div>
        </button>

        <div className="hidden md:flex items-center gap-8 text-sm font-medium">
          <button
            onClick={onHome}
            className="text-gray-600 hover:text-blue-600 transition"
          >
            Home
          </button>

          <a
            href="#how-it-works"
            className="text-gray-600 hover:text-blue-600 transition"
          >
            How It Works
          </a>

          <a
            href="#about"
            className="text-gray-600 hover:text-blue-600 transition"
          >
            About
          </a>

          <button
            onClick={onHome}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Analyze Product
          </button>
        </div>
      </div>
    </nav>
  )
}

export default Navbar