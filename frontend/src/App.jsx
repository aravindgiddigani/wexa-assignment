import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './context/useAuth'
import Header from './components/Header/Header'
import Footer from './components/Footer/Footer'
import Login from './pages/Login/Login'
import Register from './pages/Register/Register'
import Home from './pages/Home/Home'
import KnowledgeExplorer from './pages/KnowledgeExplorer/KnowledgeExplorer'
import './styles/App.css'

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p>Loading...</p>
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

// Main App Component with Routing
const AppContent = () => {
  const { user, logout, loading } = useAuth()
  const location = useLocation()
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'

  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p>Loading application...</p>
      </div>
    )
  }

  return (
      <div className="app">
        {!isAuthPage && <Header user={user} onLogout={logout} />}
        
        <main className={`main-content ${location.pathname === '/' ? 'home-content' : ''}`}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Home />} />
            <Route path="/explore" element={<ProtectedRoute><KnowledgeExplorer /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        
        {!isAuthPage && <Footer />}
      </div>
  )
}

// App Wrapper with AuthProvider
const App = () => {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}

export default App