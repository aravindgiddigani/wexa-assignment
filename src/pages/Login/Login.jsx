import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'
import '../../styles/pages/Login.css'

const Login = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    login_identifier: location.state?.loginIdentifier || '',
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(formData)
    
    if (result.success) {
      navigate(location.state?.from || '/explore', { replace: true })
    } else {
      const responseError = result.error
      const message = typeof responseError === 'string'
        ? responseError
        : responseError?.error || responseError?.detail || responseError?.non_field_errors?.[0]
      setError(message || 'Login failed. Please try again.')
    }
    
    setLoading(false)
  }

  return (
    <div className="login-page">
      <div className="auth-layout login-container">
        <div className="auth-intro">
          <p className="auth-kicker">NexusKnowledge / Explore</p>
          <h1>Return to the map.</h1>
          <p>Log in to follow the relationships between ideas, tools, and the systems that bring them together.</p>
          <span className="auth-rule" />
          <p className="auth-note">A graph database makes the connections part of the story.</p>
        </div>
        <div className="login-card">
          <div className="login-header">
            <h2>Welcome back</h2>
            <p>Sign in to explore the knowledge graph</p>
          </div>

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}

          {location.state?.message && (
            <div className="alert alert-success" role="alert">
              {location.state.message}
            </div>
          )}

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="login_identifier">Email or Phone Number</label>
              <input
                type="text"
                id="login_identifier"
                name="login_identifier"
                value={formData.login_identifier}
                onChange={handleChange}
                required
                placeholder="Enter your email or phone number"
                className="form-control"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
                className="form-control"
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-block"
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="login-footer">
            <p>Don't have an account? <Link to="/register">Register here</Link></p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login