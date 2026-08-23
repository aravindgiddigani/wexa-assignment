import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'
import '../../styles/pages/Register.css'

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    password: '',
    confirm_password: ''
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    // Clear error for this field when user starts typing
    setErrors({
      ...errors,
      [e.target.name]: ''
    })
  }

  const validateForm = () => {
    const newErrors = {}
    
    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }
    
    // Name validations
    if (!formData.first_name) {
      newErrors.first_name = 'First name is required'
    }
    if (!formData.last_name) {
      newErrors.last_name = 'Last name is required'
    }
    
    // Phone number validation
    if (!formData.phone_number) {
      newErrors.phone_number = 'Phone number is required'
    } else if (!/^\d{10}$/.test(formData.phone_number)) {
      newErrors.phone_number = 'Phone number must contain exactly 10 digits'
    }
    
    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }
    
    // Confirm password validation
    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your password'
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    setLoading(true)
    
    const result = await register(formData)
    
    if (result.success) {
      navigate('/login', {
        state: {
          message: 'Successfully registered, log in to continue.',
          loginIdentifier: formData.email.trim().toLowerCase()
        }
      })
    } else {
      // Handle server-side validation errors
      if (result.error) {
        setErrors(result.error)
      }
    }
    
    setLoading(false)
  }

  return (
    <div className="register-page">
      <div className="auth-layout register-container">
        <div className="auth-intro">
          <p className="auth-kicker">NexusKnowledge / Begin</p>
          <h1>Make the connections visible.</h1>
          <p>Create an account to move from a single concept into the wider graph around it.</p>
          <span className="auth-rule" />
          <p className="auth-note">Start with one topic. Discover where it leads.</p>
        </div>
        <div className="register-card">
          <div className="register-header">
            <h2>Create an account</h2>
            <p>Join us to explore the knowledge graph</p>
          </div>

          <form onSubmit={handleSubmit} className="register-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">First Name *</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  placeholder="John"
                  className={`form-control ${errors.first_name ? 'is-invalid' : ''}`}
                />
                {errors.first_name && <div className="invalid-feedback">{errors.first_name}</div>}
              </div>

              <div className="form-group">
                <label htmlFor="last_name">Last Name *</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  placeholder="Doe"
                  className={`form-control ${errors.last_name ? 'is-invalid' : ''}`}
                />
                {errors.last_name && <div className="invalid-feedback">{errors.last_name}</div>}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="john@example.com"
                className={`form-control ${errors.email ? 'is-invalid' : ''}`}
              />
              {errors.email && <div className="invalid-feedback">{errors.email}</div>}
            </div>

            <div className="form-group">
              <label htmlFor="phone_number">Phone Number *</label>
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleChange}
                required
                  placeholder="1234567890"
                className={`form-control ${errors.phone_number ? 'is-invalid' : ''}`}
              />
              {errors.phone_number && <div className="invalid-feedback">{errors.phone_number}</div>}
              <small className="form-text">Enter exactly 10 digits</small>
            </div>

            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Min. 6 characters"
                className={`form-control ${errors.password ? 'is-invalid' : ''}`}
              />
              {errors.password && <div className="invalid-feedback">{errors.password}</div>}
            </div>

            <div className="form-group">
              <label htmlFor="confirm_password">Confirm Password *</label>
              <input
                type="password"
                id="confirm_password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                required
                placeholder="Re-enter your password"
                className={`form-control ${errors.confirm_password ? 'is-invalid' : ''}`}
              />
              {errors.confirm_password && <div className="invalid-feedback">{errors.confirm_password}</div>}
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-block"
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          <div className="register-footer">
            <p>Already have an account? <Link to="/login">Sign in here</Link></p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register