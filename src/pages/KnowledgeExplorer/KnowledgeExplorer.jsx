import { useEffect, useState } from 'react'
import knowledgeService from '../../services/knowledgeService'
import '../../styles/pages/KnowledgeExplorer.css'

const sectionImages = {
  Foundations: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?auto=format&fit=crop&w=1200&q=85',
  Intelligence: 'https://images.unsplash.com/photo-1555255707-c07966088b7b?auto=format&fit=crop&w=1200&q=85',
  'Data & Systems': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=85',
  'Build & Ship': 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85'
}

const getErrorMessage = (error, fallback) => {
  if (error.response) return `${error.response.status} - ${error.response.data.error || fallback}`
  if (error.request) return 'Could not reach the knowledge graph. Check that the backend is running.'
  return error.message || fallback
}

const KnowledgeExplorer = () => {
  const [sections, setSections] = useState([])
  const [overview, setOverview] = useState(null)
  const [topics, setTopics] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedSection, setSelectedSection] = useState(null)
  const [selectedTopic, setSelectedTopic] = useState(null)
  const [selectedTopicData, setSelectedTopicData] = useState(null)
  const [relatedTopics, setRelatedTopics] = useState([])
  const [relationships, setRelationships] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [activeTab, setActiveTab] = useState('related')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchTopics = async () => {
    const nextTopics = await knowledgeService.getAllTopics()
    setTopics(nextTopics)
  }

  const fetchCategories = async () => {
    const nextCategories = await knowledgeService.getAllCategories()
    setCategories(nextCategories)
  }

  const handleTopicClick = async (topicName) => {
    try {
      setLoading(true)
      setSelectedTopic(topicName)
      const [nextTopic, nextRelated, nextRelationships] = await Promise.all([
        knowledgeService.getTopic(topicName),
        knowledgeService.findRelatedTopics(topicName),
        knowledgeService.getTopicRelationships(topicName)
      ])
      setRelatedTopics(nextRelated)
      setRelationships(nextRelationships)
      setSelectedTopicData(nextTopic)
      setActiveTab('related')
      setError(null)
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Could not load topic connections.'))
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (event) => {
    event.preventDefault()
    if (!searchTerm.trim()) return
    try {
      setLoading(true)
      setTopics(await knowledgeService.searchTopics(searchTerm.trim()))
      setError(null)
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Could not search the knowledge graph.'))
    } finally {
      setLoading(false)
    }
  }

  const handleCategoryFilter = async (category) => {
    setSelectedCategory(category)
    try {
      setLoading(true)
      setTopics(category ? await knowledgeService.getTopicsByCategory(category) : await knowledgeService.getAllTopics())
      setError(null)
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Could not filter the knowledge graph.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true)
        const [nextSections, nextOverview] = await Promise.all([
          knowledgeService.getSections(),
          knowledgeService.getOverview(),
          fetchTopics(),
          fetchCategories()
        ])
        setSections(nextSections)
        setOverview(nextOverview)
        setSelectedSection(nextSections[0] || null)
      } catch (requestError) {
        setError(getErrorMessage(requestError, 'Could not load the knowledge graph.'))
      } finally {
        setLoading(false)
      }
    }

    void loadInitialData()
  }, [])

  const visibleTopics = selectedSection && !searchTerm && !selectedCategory
    ? topics.filter((topic) => selectedSection.topics.includes(topic.name))
    : topics

  return (
    <div className="knowledge-explorer">
      <div className="explorer-shell">
        <div className="explorer-heading">
          <div>
            <p className="explorer-kicker">NexusKnowledge / Explorer</p>
            <h1>Follow the connections.</h1>
          </div>
          <p className="explorer-description">Move through curated ideas, then open the relationships beneath them. This is the graph in motion.</p>
        </div>

        {error && <div className="explorer-alert" role="alert">{error}</div>}

        <nav className="section-nav" aria-label="Knowledge sections">
          {sections.map((section) => (
            <button className={selectedSection?.name === section.name ? 'section-nav-item active' : 'section-nav-item'} key={section.name} onClick={() => setSelectedSection(section)}>
              <span>0{section.display_order}</span>{section.name}
            </button>
          ))}
        </nav>

        {overview && <div className="graph-stats">
          {Object.entries(overview.counts).map(([label, count]) => <div className="graph-stat" key={label}><strong>{count}</strong><span>{label}</span></div>)}
        </div>}

        {selectedSection && (
          <section className="section-feature">
            <div className="section-feature-image" style={{ backgroundImage: `url(${sectionImages[selectedSection.name]})` }} />
            <div className="section-feature-copy">
              <p className="explorer-kicker">Section 0{selectedSection.display_order}</p>
              <h2>{selectedSection.name}</h2>
              <p className="section-objective">{selectedSection.objective}</p>
              <p>{selectedSection.introduction}</p>
              <div className="section-context-grid">
                <div><span>Why a graph</span><p>{selectedSection.graph_database_context}</p></div>
                <div><span>CognoDB in practice</span><p>{selectedSection.cognodb_context}</p></div>
              </div>
              <div className="path-line"><span>Example path</span>{selectedSection.example_path.map((step, index) => <strong key={`${step}-${index}`}>{step}{index < selectedSection.example_path.length - 1 && '  ->  '}</strong>)}</div>
            </div>
          </section>
        )}

        <div className="discovery-controls">
          <div><p className="explorer-kicker">Find a path</p><span>Search the topics inside this graph.</span></div>
          <form onSubmit={handleSearch} className="explorer-search"><input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search topics" aria-label="Search topics" /><button type="submit">Search</button></form>
          <select value={selectedCategory} onChange={(event) => handleCategoryFilter(event.target.value)} aria-label="Filter by category"><option value="">All categories</option>{categories.map((category) => <option key={category} value={category}>{category}</option>)}</select>
        </div>

        {selectedTopicData && <section className="topic-reading">
          <div className="topic-reading-heading"><div><p className="explorer-kicker">Topic article</p><h2>{selectedTopicData.name}</h2><p>{selectedTopicData.description}</p></div><span>{selectedTopicData.category}</span></div>
          <div className="topic-visuals"><img src={selectedTopicData.topic_image} alt={`${selectedTopicData.name} concept`} /><div><img src={selectedTopicData.code_image} alt="Code illustration" /><img src={selectedTopicData.graph_image} alt="Graph database illustration" /></div></div>
          <div className="topic-article">{selectedTopicData.article_content?.split('\n\n').map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
          <div className="topic-learning-grid">
            <div><span>Real-world uses</span><ul>{selectedTopicData.real_world_examples?.map((example) => <li key={example}>{example}</li>)}</ul></div>
            <div><span>{selectedTopicData.code_language} example</span><pre><code>{selectedTopicData.code_snippet}</code></pre></div>
            <div><span>Cypher traversal</span><pre><code>{selectedTopicData.cypher_example}</code></pre></div>
          </div>
          <div className="topic-resources"><span>Real-world resources</span><div>{selectedTopicData.resource_links?.map((link) => <a href={link} key={link} target="_blank" rel="noreferrer">{new URL(link).hostname.replace('www.', '')} <b>↗</b></a>)}</div></div>
        </section>}

        <section className="graph-workbench">
          <div className="workbench-grid">
            <aside className="topic-rail"><div className="rail-label">{visibleTopics.length} topics in view</div>{loading && !topics.length ? <p className="empty-state">Loading graph...</p> : visibleTopics.map((topic) => <button key={topic.name} className={selectedTopic === topic.name ? 'topic-item active' : 'topic-item'} onClick={() => handleTopicClick(topic.name)}><span>{topic.name}</span><small>{topic.category}</small><b>{topic.importance}</b></button>)}{!loading && !visibleTopics.length && <p className="empty-state">No topics found.</p>}</aside>
            <div className="connection-panel">{selectedTopic ? <><div className="connection-heading"><div><p className="explorer-kicker">Selected topic</p><h3>{selectedTopic}</h3></div><button className="clear-button" onClick={() => setSelectedTopic(null)}>Clear</button></div><div className="graph-tabs"><button className={activeTab === 'related' ? 'active' : ''} onClick={() => setActiveTab('related')}>Related topics</button><button className={activeTab === 'relationships' ? 'active' : ''} onClick={() => setActiveTab('relationships')}>Relationships</button></div>{activeTab === 'related' ? <div className="connection-list">{relatedTopics.map((topic) => <button key={topic.name} className="connection-item" onClick={() => handleTopicClick(topic.name)}><span><strong>{topic.name}</strong><small>{topic.category}</small></span><b>{topic.distance} hops</b></button>)}{!relatedTopics.length && <p className="empty-state">No related topics found.</p>}</div> : <div className="relationship-list">{relationships.map((relationship, index) => <div className="relationship-item" key={`${relationship.from_topic}-${relationship.to_topic}-${index}`}><strong>{relationship.from_topic}</strong><span>{relationship.relationship_type.replace('_', ' ')}</span><strong>{relationship.to_topic}</strong></div>)}{!relationships.length && <p className="empty-state">No direct relationships found.</p>}</div>}</> : <div className="workbench-empty"><span>+</span><h3>Select a topic</h3><p>Choose a node from the left to reveal its neighboring ideas and paths.</p></div>}</div>
          </div>
        </section>

        {overview?.relationship_types?.length > 0 && <section className="relationship-guide">
          <div><p className="explorer-kicker">Reading the graph</p><h2>Relationships have meaning.</h2></div>
          <div className="relationship-guide-list">{overview.relationship_types.map((relationship) => <div key={relationship.name}><strong>{relationship.name}</strong><p>{relationship.description}</p></div>)}</div>
        </section>}
      </div>
    </div>
  )
}

export default KnowledgeExplorer
