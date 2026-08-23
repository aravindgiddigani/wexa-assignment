# Knowledge Graph Explorer

A full-stack web application that demonstrates the power of graph databases for exploring knowledge relationships. Built with Django REST Framework, React.js, and CognoDB (Neo4j-compatible graph database).

## Use Case

This application allows users to explore knowledge domains and discover connections between concepts, technologies, and ideas. It demonstrates how graph databases naturally model complex relationships that would be awkward in traditional relational databases.

## Why a Graph Database?

**Graph databases excel at modeling relationships and connections.** In this knowledge graph:

- **Natural relationship modeling**: Topics are connected through various relationship types (BUILDS_ON, APPLIES_TO, CONTRADICTS, etc.) that represent real-world semantic relationships
- **Multi-hop traversals**: Finding related concepts through indirect connections (e.g., "What topics are related to Machine Learning through 2-3 hops?")
- **Flexible schema**: New relationship types can be added without schema migrations
- **Performance optimization**: Graph traversals are naturally optimized for relationship queries vs. expensive JOINs in relational databases

**Example:** Finding all prerequisites for "Deep Learning" requires traversing multiple relationship types and depths - a simple graph query vs. complex recursive SQL in relational databases.

## Data Model

### Graph Schema

```
Topic (Node)
├── Properties:
│   ├── name: string (unique)
│   ├── description: string
│   ├── category: string
│   ├── importance: integer (1-10)
│   └── created_at: datetime
│
└── Relationships:
    ├── RELATED_TO: General connection between topics
    ├── BUILDS_ON: Prerequisite relationship (A builds on B)
    ├── CONTRADICTS: Opposing concepts
    ├── PART_OF: Hierarchical relationship (A is part of B)
    └── APPLIES_TO: Application relationship (A applies to B)
```

### Example Graph Structure

```
┌─────────────┐
│  Python     │───BUILDS_ON──→┌─────────────┐
└─────────────┘                │Machine Learn│
       │                       └─────────────┘
       │APPLIES_TO                    │
       ↓                              │BUILDS_ON
┌─────────────┐                       ↓
│    AI       │←─────────────────┌──────────┐
└─────────────┘                    │Deep Learn│
       │BUILDS_ON                  └──────────┘
       ↓                              │
┌─────────────┐                BUILDS_ON
│Neural Netwr │←──────────────────────┘
└─────────────┘
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- CognoDB Cloud account (free tier available)

### 1. Create CognoDB Instance

1. Sign up at [https://console.cognodb.com/signup](https://console.cognodb.com/signup)
2. Create a free (c0) instance
3. Save your connection details:
   - **URI**: `bolt+s://<instance-id>.databases.cognodb.cloud`
   - **Username**: `cognodb`
   - **Password**: (shown once during creation - save it!)

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env file and add your CognoDB credentials:
# NEO4J_URI=bolt+s://your-instance-id.databases.cognodb.cloud
# NEO4J_USER=cognodb
# NEO4J_PASSWORD=your-password-here

# Load seed data
python seed_data.py

# Start Django server
python manage.py runserver
```

The backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will run on `http://localhost:5173`

## API Endpoints

### Authentication APIs

- `POST /api/auth/register/` - Register new user
  - Body: `{ email, first_name, last_name, phone_number, password }`
  - Returns: `{ message }`
- `POST /api/auth/login/` - Login with email or phone
  - Body: `{ login_identifier, password }` where `login_identifier` is the user's email or phone number
  - Returns: `{ message, access_token, refresh_token }`
- `POST /api/auth/logout/` - Logout (requires token)
  - Header: `Authorization: Token <token>`
- `POST /api/auth/profile/` - Get current user profile (requires token)
  - Header: `Authorization: Token <token>`

### Knowledge Graph APIs

- `GET /api/knowledge/health/` - Health check (no auth required)
- `POST /api/knowledge/topics/list/` - Get all topics (requires auth)
- `POST /api/knowledge/topics/detail/` - Get specific topic details (requires auth)
  - Body: `{ topic_name }`
- `POST /api/knowledge/topics/relationships/` - Get topic relationships (requires auth)
  - Body: `{ topic_name }`
- `POST /api/knowledge/search/` - Search topics (requires auth)
  - Body: `{ q }` (search term)
- `POST /api/knowledge/topics/by-category/` - Filter by category (requires auth)
  - Body: `{ category }`
- `POST /api/knowledge/categories/` - Get all categories (requires auth)
- `POST /api/knowledge/sections/` - Get curated learning sections (requires auth)
- `POST /api/knowledge/overview/` - Get graph counts and relationship definitions (requires auth)
- `POST /api/knowledge/topics/related/` - Find related topics multi-hop (requires auth)
  - Body: `{ topic_name, hops }` (hops: 1-4)
- `POST /api/knowledge/topics/prerequisites/` - Get prerequisites (requires auth)
  - Body: `{ topic_name }`
- `POST /api/knowledge/topics/applications/` - Get applications (requires auth)
  - Body: `{ topic_name }`

**Note**: All knowledge graph endpoints require authentication via `Authorization: Token <token>` header.

## Key Cypher Queries

### Multi-hop Traversal
```cypher
MATCH path = (t:Topic {name: $name})-[*1..2]-(other:Topic)
WHERE other.name <> $name
RETURN DISTINCT other.name, length(path) as distance
ORDER BY distance
```
Finds topics related to a given topic within 2 hops, demonstrating graph traversal capabilities.

### Prerequisite Chain
```cypher
MATCH (t:Topic {name: $name})-[:BUILDS_ON*]->(prereq:Topic)
RETURN DISTINCT prereq.name, prereq.description
ORDER BY prereq.importance DESC
```
Traverses prerequisite relationships to find foundational concepts.

### Relationship Query
```cypher
MATCH (from:Topic {name: $from_name})-[r:BUILDS_ON]->(to:Topic {name: $to_name})
RETURN from, r, to
```
Reads a native typed relationship between topics. The seed script creates the appropriate relationship label from its fixed relationship-type allowlist.

## Features

- **Topic Exploration**: Browse and search knowledge topics
- **Relationship Discovery**: View direct relationships between concepts
- **Multi-hop Analysis**: Find related concepts through indirect connections
- **Category Filtering**: Explore topics by domain (AI, Programming, Mathematics, etc.)
- **Importance Scoring**: Topics ranked by importance (1-10 scale)
- **Responsive Design**: Mobile-friendly interface using Bootstrap

## Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Frontend**: React 19, Vite, Bootstrap 5
- **Database**: CognoDB (Neo4j-compatible graph database)
- **Driver**: Official Neo4j Python Driver
- **Authentication**: Custom CognoDB-based authentication (no Django ORM)

## Postman Collection

A Postman collection is provided at `backend/postman_collection.json` for testing all API endpoints.

**To import:**
1. Open Postman
2. Click Import → Select `postman_collection.json`
3. Set the `base_url` variable to your backend URL (default: `http://localhost:8000`)
4. After login, copy the token and set it as the `auth_token` variable

**Collection includes:**
- Authentication endpoints (register, login, logout, profile)
- All knowledge graph endpoints with example payloads
- Pre-configured headers for token-based authentication

## Seed Data

The application includes realistic seed data covering:
- Programming languages (Python, JavaScript)
- Web technologies (HTML, CSS, React, Django)
- AI and Machine Learning concepts
- Mathematics (Calculus, Linear Algebra, Statistics)
- Software engineering practices
- Database technologies

## Deployment

### Backend Deployment (e.g., Heroku, Render)

1. Set environment variables in your hosting platform
2. Build and deploy the Django application
3. Ensure your CognoDB instance allows connections from your deployment IP

### Frontend Deployment (e.g., Vercel, Netlify)

1. Build the frontend: `npm run build`
2. Deploy the dist folder
3. Update API_BASE_URL in production build

## Screenshots

*(Add screenshots of your application here)*

- Main topic list with categories
- Topic detail view with relationships
- Multi-hop related topics
- Search functionality
- Category filtering

## Contributing

This is a demonstration project for assessment purposes. For improvements:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is created for assessment purposes.

## Acknowledgments

- CognoDB for providing the graph database platform
- Neo4j for the excellent Python driver
- Django and React communities