import '../../styles/components/Footer.css'

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>NexusKnowledge</h3>
            <p>Explore connections between concepts, technologies, and ideas using the power of graph databases.</p>
          </div>
          
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="/about">About</a></li>
              <li><a href="/documentation">Documentation</a></li>
              <li><a href="/contact">Contact</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Technology Stack</h4>
            <ul>
              <li>Django REST Framework</li>
              <li>React.js</li>
              <li>CognoDB (Neo4j)</li>
              <li>Bootstrap 5</li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Connect</h4>
            <div className="social-links">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub</a>
              <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer">LinkedIn</a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer">Twitter</a>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; 2024 NexusKnowledge. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer