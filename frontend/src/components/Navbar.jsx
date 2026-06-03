function Navbar({ onHome }) {
  return (
    <nav className="w-full bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <button
          onClick={onHome}
          className="text-xl font-bold text-gray-900 hover:text-blue-600"
        >
          Smart Buy Window Predictor
        </button>

        <div className="hidden sm:flex items-center gap-6 text-sm text-gray-600">
          <button onClick={onHome} className="hover:text-blue-600">
            Home
          </button>
          <a href="#how-it-works" className="hover:text-blue-600">
            How It Works
          </a>
          <a href="#about" className="hover:text-blue-600">
            About
          </a>
        </div>
      </div>
    </nav>
  )
}

export default Navbar