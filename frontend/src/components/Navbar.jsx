import { Link, useLocation } from 'react-router-dom'
import { Sparkles, Settings, Home } from 'lucide-react'

export default function Navbar() {
  const location = useLocation()
  
  return (
    <>
      {/* Marquee Banner */}
      <div className="bg-brutal-lime border-b-3 border-brutal-black overflow-hidden py-2">
        <div className="animate-marquee whitespace-nowrap">
          <span className="mx-8 font-mono text-sm font-bold">
            ✦ GRAD STUDENT SURVIVAL AGENT ✦ POWERED BY ARA ✦ AUTOMATE YOUR ACADEMIC LIFE ✦ GRAD STUDENT SURVIVAL AGENT ✦ POWERED BY ARA ✦ AUTOMATE YOUR ACADEMIC LIFE ✦
          </span>
        </div>
      </div>
      
      {/* Main Nav */}
      <nav className="bg-brutal-white border-b-3 border-brutal-black">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-brutal-pink border-3 border-brutal-black flex items-center justify-center">
                <Sparkles className="w-6 h-6" />
              </div>
              <span className="font-bold text-xl tracking-tight">SURVIVAL.AI</span>
            </Link>
            
            {/* Nav Links */}
            <div className="flex items-center gap-4">
              <Link 
                to="/"
                className={`flex items-center gap-2 px-4 py-2 font-bold border-3 border-brutal-black transition-all
                  ${location.pathname === '/' 
                    ? 'bg-brutal-yellow shadow-brutal' 
                    : 'bg-brutal-white hover:bg-brutal-mint'}`}
              >
                <Home className="w-4 h-4" />
                Dashboard
              </Link>
              <Link 
                to="/settings"
                className={`flex items-center gap-2 px-4 py-2 font-bold border-3 border-brutal-black transition-all
                  ${location.pathname === '/settings' 
                    ? 'bg-brutal-yellow shadow-brutal' 
                    : 'bg-brutal-white hover:bg-brutal-mint'}`}
              >
                <Settings className="w-4 h-4" />
                Settings
              </Link>
            </div>
          </div>
        </div>
      </nav>
    </>
  )
}