"""
URL configuration for knowledge app
"""
from django.urls import path
from knowledge.views import (
    HealthCheckView, TopicListView, TopicDetailView, TopicRelationshipsView,
    SearchTopicsView, TopicsByCategoryView, RelatedTopicsView,
    PrerequisitesView, ApplicationsView, CategoriesView, KnowledgeSectionsView,
    KnowledgeOverviewView
)

urlpatterns = [
    # Health check
    path('health/', HealthCheckView.as_view(), name='health_check'),
    
    # Topic endpoints
    path('topics/list/', TopicListView.as_view(), name='get_all_topics'),
    path('topics/detail/', TopicDetailView.as_view(), name='get_topic'),
    path('topics/relationships/', TopicRelationshipsView.as_view(), name='get_topic_relationships'),
    
    # Search and categorization
    path('search/', SearchTopicsView.as_view(), name='search_topics'),
    path('topics/by-category/', TopicsByCategoryView.as_view(), name='get_topics_by_category'),
    path('categories/', CategoriesView.as_view(), name='get_all_categories'),
    path('sections/', KnowledgeSectionsView.as_view(), name='get_knowledge_sections'),
    path('overview/', KnowledgeOverviewView.as_view(), name='get_knowledge_overview'),
    
    # Graph traversal endpoints
    path('topics/related/', RelatedTopicsView.as_view(), name='find_related_topics'),
    path('topics/prerequisites/', PrerequisitesView.as_view(), name='get_prerequisites'),
    path('topics/applications/', ApplicationsView.as_view(), name='get_applications'),
]