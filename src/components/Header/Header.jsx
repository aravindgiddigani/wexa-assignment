import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import '../../styles/components/Header.css'

const Header = ({ user, onLogout }) => {
  const location = useLocation()
  const isHome = location.pathname === '/'
  const [isPastHero, setIsPastHero] = useState(false)

  useEffect(() => {
    if (!isHome) return undefined

    const handleScroll = () => {
      const hero = document.querySelector('.home-hero')
      const heroHalfway = hero ? hero.offsetTop + hero.offsetHeight / 2 : window.innerHeight / 2
      setIsPastHero(window.scrollY >= heroHalfway)
    }
    handleScroll()
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [isHome])

  return (
    <header className={`header ${isHome ? 'header-home' : ''} ${isPastHero ? 'header-scrolled' : ''}`}>
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo">
            <h1>NexusKnowledge</h1>
          </Link>
          
          <nav className="nav">
            {user ? (
              <div className="nav-items">
                <span className="user-greeting">
                  Welcome, {user.first_name}!
                </span>
                <button onClick={onLogout} className="btn btn-logout">
                  Logout
                </button>
              </div>
            ) : (
              <div className="nav-items">
                <Link to="/login" className="btn btn-login">
                  Login
                </Link>
                <Link to="/register" className="btn btn-register">
                  Register
                </Link>
              </div>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header