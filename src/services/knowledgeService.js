import api from './api'

const API_BASE_URL = '/knowledge'

const knowledgeService = {
  getOverview: async () => {
    const response = await api.post(`${API_BASE_URL}/overview/`)
    return response.data
  },

  getSections: async () => {
    const response = await api.post(`${API_BASE_URL}/sections/`)
    return response.data.sections
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get(`${API_BASE_URL}/health/`)
    return response.data
  },

  // Get all topics
  getAllTopics: async () => {
    const response = await api.post(`${API_BASE_URL}/topics/list/`)
    return response.data.topics
  },

  // Get specific topic
  getTopic: async (topicName) => {
    const response = await api.post(`${API_BASE_URL}/topics/detail/`, { topic_name: topicName })
    return response.data.topic
  },

  // Get topic relationships
  getTopicRelationships: async (topicName) => {
    const response = await api.post(`${API_BASE_URL}/topics/relationships/`, { topic_name: topicName })
    return response.data.relationships
  },

  // Search topics
  searchTopics: async (query) => {
    const response = await api.post(`${API_BASE_URL}/search/`, { q: query })
    return response.data.topics
  },

  // Get topics by category
  getTopicsByCategory: async (category) => {
    const response = await api.post(`${API_BASE_URL}/topics/by-category/`, { category })
    return response.data.topics
  },

  // Get all categories
  getAllCategories: async () => {
    const response = await api.post(`${API_BASE_URL}/categories/`)
    return response.data.categories
  },

  // Find related topics
  findRelatedTopics: async (topicName, hops = 2) => {
    const response = await api.post(`${API_BASE_URL}/topics/related/`, { topic_name: topicName, hops })
    return response.data.related_topics
  },

  // Get prerequisites
  getPrerequisites: async (topicName) => {
    const response = await api.post(`${API_BASE_URL}/topics/prerequisites/`, { topic_name: topicName })
    return response.data.prerequisites
  },

  // Get applications
  getApplications: async (topicName) => {
    const response = await api.post(`${API_BASE_URL}/topics/applications/`, { topic_name: topicName })
    return response.data.applications
  }
}

export default knowledgeService