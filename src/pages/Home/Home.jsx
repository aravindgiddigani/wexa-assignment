import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/useAuth'
import '../../styles/pages/Home.css'

const sections = [
  {
    number: '01',
    title: 'Foundations',
    text: 'Start with the concepts that make every connected idea easier to understand.',
    topic: 'Python',
    image: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?auto=format&fit=crop&w=900&q=85'
  },
  {
    number: '02',
    title: 'Intelligence',
    text: 'Follow the paths from machine learning to models, language, and vision.',
    topic: 'Machine Learning',
    image: 'https://images.unsplash.com/photo-1555255707-c07966088b7b?auto=format&fit=crop&w=900&q=85'
  },
  {
    number: '03',
    title: 'Data & systems',
    text: 'See how data, databases, and infrastructure become useful together.',
    topic: 'Graph Database',
    image: 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=900&q=85'
  },
  {
    number: '04',
    title: 'Build & ship',
    text: 'Connect software practices to the tools that move an idea into the world.',
    topic: 'DevOps',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=85'
  }
]

const Home = () => {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()

  const openExplorer = () => {
    if (isAuthenticated) {
      navigate('/explore')
      return
    }

    navigate('/login', { state: { from: '/explore' } })
  }

  return (
    <div className="home-page">
      <section className="home-hero">
        <div className="hero-copy">
          <p className="eyebrow">A living map of connected knowledge</p>
          <h1>Think in connections.</h1>
          <p className="hero-text">
            NexusKnowledge turns a library of concepts into a landscape you can explore,
            trace, and return to with a little more clarity each time.
          </p>
          <button className="hero-action" onClick={openExplorer}>Explore the graph <span>{'->'}</span></button>
        </div>
        <div className="hero-image" role="img" aria-label="A network of connected points representing the knowledge graph" />
      </section>

      <section className="home-intro">
        <p className="section-kicker">Inside the graph</p>
        <h2>Your next idea is probably already connected.</h2>
        <p>
          The seed library brings together programming, artificial intelligence, data science,
          mathematics, networking, and the systems that support them.
        </p>
      </section>

      <section className="home-sections">
        {sections.map((section) => (
          <article className="knowledge-section" key={section.number}>
            <span className="section-number">{section.number}</span>
            <div className="section-copy">
              <h3>{section.title}</h3>
              <p>{section.text}</p>
              <button onClick={openExplorer}>More <span>{'->'}</span></button>
            </div>
            <div className="section-media">
              <img src={section.image} alt={section.topic} />
              <span className="section-topic">{section.topic}</span>
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}

export default Home
