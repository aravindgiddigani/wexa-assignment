"""
Seed Data Loading Script for NexusKnowledge
Populates the knowledge graph with comprehensive sample data

Usage: python seed_data.py
Prerequisites: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD must be set in .env file
"""
import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RelationshipType:
    RELATED_TO = "RELATED_TO"
    BUILDS_ON = "BUILDS_ON"
    CONTRADICTS = "CONTRADICTS"
    PART_OF = "PART_OF"
    APPLIES_TO = "APPLIES_TO"


RELATIONSHIP_QUERIES = {
    RelationshipType.RELATED_TO: """MATCH (from:Topic {name: $from_name}) MATCH (to:Topic {name: $to_name}) MERGE (from)-[r:RELATED_TO]->(to) SET r.created_at = datetime()""",
    RelationshipType.BUILDS_ON: """MATCH (from:Topic {name: $from_name}) MATCH (to:Topic {name: $to_name}) MERGE (from)-[r:BUILDS_ON]->(to) SET r.created_at = datetime()""",
    RelationshipType.CONTRADICTS: """MATCH (from:Topic {name: $from_name}) MATCH (to:Topic {name: $to_name}) MERGE (from)-[r:CONTRADICTS]->(to) SET r.created_at = datetime()""",
    RelationshipType.PART_OF: """MATCH (from:Topic {name: $from_name}) MATCH (to:Topic {name: $to_name}) MERGE (from)-[r:PART_OF]->(to) SET r.created_at = datetime()""",
    RelationshipType.APPLIES_TO: """MATCH (from:Topic {name: $from_name}) MATCH (to:Topic {name: $to_name}) MERGE (from)-[r:APPLIES_TO]->(to) SET r.created_at = datetime()""",
}


class SeedDataConnection:
    def __init__(self):
        self._driver = None
    
    def connect(self):
        if self._driver is None:
            try:
                uri = os.getenv('NEO4J_URI')
                user = os.getenv('NEO4J_USER')
                password = os.getenv('NEO4J_PASSWORD')
                
                if not uri:
                    raise ValueError("NEO4J_URI environment variable is required. Please set it in your .env file.")
                if not user:
                    raise ValueError("NEO4J_USER environment variable is required. Please set it in your .env file.")
                if not password:
                    raise ValueError("NEO4J_PASSWORD environment variable is required. Please set it in your .env file.")
                
                self._driver = GraphDatabase.driver(uri, auth=(user, password))
                self._driver.verify_connectivity()
                logger.info("Successfully connected to CognoDB")
            except AuthError as e:
                logger.error(f"Authentication failed: {e}")
                raise ConnectionError("Invalid CognoDB credentials. Please check NEO4J_USER and NEO4J_PASSWORD.")
            except ServiceUnavailable as e:
                logger.error(f"Service unavailable: {e}")
                raise ConnectionError("Unable to connect to CognoDB. Please check NEO4J_URI and network connectivity.")
            except Exception as e:
                logger.error(f"Unexpected error connecting to CognoDB: {e}")
                raise ConnectionError(f"Connection error: {str(e)}")
        return self._driver
    
    def close(self):
        if self._driver is not None:
            try:
                self._driver.close()
                self._driver = None
                logger.info("Closed CognoDB connection")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
    
    def get_session(self):
        try:
            return self.connect().session()
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise


seed_connection = SeedDataConnection()


def clear_database():
    try:
        session = seed_connection.get_session()
        session.run("""
            MATCH (n)
            WHERE n:Topic OR n:KnowledgeCategory OR n:KnowledgeSection OR n:RelationshipType
            DETACH DELETE n
        """)
        session.close()
        logger.info("Cleared seeded knowledge graph data while preserving users and tokens")
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise RuntimeError(f"Failed to clear database: {str(e)}")


def create_constraints():
    try:
        session = seed_connection.get_session()
        session.run("CREATE CONSTRAINT topic_name_unique IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE")
        session.run("CREATE CONSTRAINT relationship_type_name_unique IF NOT EXISTS FOR (r:RelationshipType) REQUIRE r.name IS UNIQUE")
        session.run("CREATE CONSTRAINT knowledge_section_name_unique IF NOT EXISTS FOR (s:KnowledgeSection) REQUIRE s.name IS UNIQUE")
        session.run("CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE")
        session.run("CREATE CONSTRAINT user_phone_unique IF NOT EXISTS FOR (u:User) REQUIRE u.phone_number IS UNIQUE")
        session.run("CREATE CONSTRAINT token_key_unique IF NOT EXISTS FOR (t:Token) REQUIRE t.key IS UNIQUE")
        session.close()
        logger.info("Created database constraints")
    except Exception as e:
        logger.error(f"Error creating constraints: {e}")
        raise RuntimeError(f"Failed to create constraints: {str(e)}")


def load_knowledge_sections():
    sections = [
        {
            'name': 'Foundations',
            'display_order': 1,
            'objective': 'Teach users how NexusKnowledge represents concepts, categories, nodes, properties, and relationships.',
            'introduction': 'A topic is a node in the knowledge graph. Its description, category, and importance are properties that give the node meaning.',
            'graph_database_context': 'Unlike a flat list or many joined tables, a graph keeps the connections between topics visible and queryable.',
            'cognodb_context': 'CognoDB stores topics as nodes and lets the application follow relationships such as BUILDS_ON, PART_OF, RELATED_TO, and APPLIES_TO.',
            'example_path': ['Python', 'Data Science', 'Machine Learning'],
            'categories': ['Programming Languages', 'Web Development', 'Backend Frameworks', 'Mathematics', 'Networking'],
            'topics': ['Python', 'JavaScript', 'HTML', 'CSS', 'Django', 'HTTP', 'Statistics'],
        },
        {
            'name': 'Intelligence',
            'display_order': 2,
            'objective': 'Show how graph traversal reveals learning paths, prerequisites, and related artificial intelligence techniques.',
            'introduction': 'Artificial intelligence becomes easier to understand when its models, methods, and prerequisites are connected instead of isolated.',
            'graph_database_context': 'A graph can answer multi-hop questions such as what leads to Deep Learning or which techniques are related to Natural Language Processing.',
            'cognodb_context': 'CognoDB follows relationship paths to return connected concepts, making prerequisite discovery and related-topic exploration natural.',
            'example_path': ['Mathematics', 'Statistics', 'Machine Learning', 'Deep Learning', 'Neural Networks', 'Generative AI'],
            'categories': ['Artificial Intelligence', 'Data Science', 'Mathematics'],
            'topics': ['Machine Learning', 'Deep Learning', 'Neural Networks', 'Natural Language Processing', 'Computer Vision', 'Generative AI', 'Large Language Models', 'Transformer Architecture'],
        },
        {
            'name': 'Data & Systems',
            'display_order': 3,
            'objective': 'Explain when connected data makes a graph database more useful than a relational or document-oriented model.',
            'introduction': 'Data is more than records. It has lineage, dependencies, sources, and outcomes that can be explored as a connected system.',
            'graph_database_context': 'Relational databases organize data in tables and rely on JOINs. Graph databases store relationships directly, which helps with dependency, recommendation, and lineage questions.',
            'cognodb_context': 'CognoDB uses a Neo4j-compatible graph model and Cypher queries to traverse connected data without building a new join for every relationship.',
            'example_path': ['Data Science', 'Data Analysis', 'Data Visualization', 'Graph Database'],
            'categories': ['Databases', 'Data Science', 'Networking'],
            'topics': ['SQL', 'PostgreSQL', 'MongoDB', 'Graph Database', 'Database Indexing', 'Data Science', 'Data Analysis', 'Data Visualization'],
        },
        {
            'name': 'Build & Ship',
            'display_order': 4,
            'objective': 'Connect graph concepts to practical software engineering, delivery, cloud infrastructure, and operations.',
            'introduction': 'Modern products depend on chains of code, tests, services, infrastructure, monitoring, and security controls.',
            'graph_database_context': 'A graph makes service dependencies and blast radius visible, helping teams trace what a deployment or failure could affect.',
            'cognodb_context': 'CognoDB can connect repositories, pipelines, services, resources, and controls so operational questions become graph traversals.',
            'example_path': ['Git', 'Testing', 'CI/CD', 'Docker', 'Kubernetes', 'Monitoring'],
            'categories': ['Software Engineering', 'Cloud Computing', 'DevOps', 'Security'],
            'topics': ['Version Control', 'Git', 'GitHub', 'Testing', 'CI/CD', 'Docker', 'Kubernetes', 'Monitoring', 'Logging', 'Cybersecurity'],
        },
    ]

    try:
        session = seed_connection.get_session()
        for section in sections:
            session.run("""
                MERGE (s:KnowledgeSection {name: $name})
                SET s.display_order = $display_order,
                    s.objective = $objective,
                    s.introduction = $introduction,
                    s.graph_database_context = $graph_database_context,
                    s.cognodb_context = $cognodb_context,
                    s.example_path = $example_path,
                    s.created_at = datetime()
            """, section)

            for category in section['categories']:
                session.run("""
                    MATCH (s:KnowledgeSection {name: $section})
                    MATCH (c:KnowledgeCategory {name: $category})
                    MERGE (s)-[:COVERS_CATEGORY]->(c)
                """, {'section': section['name'], 'category': category})

            for topic in section['topics']:
                session.run("""
                    MATCH (s:KnowledgeSection {name: $section})
                    MATCH (t:Topic {name: $topic})
                    MERGE (s)-[:INCLUDES_TOPIC]->(t)
                """, {'section': section['name'], 'topic': topic})

        session.close()
        logger.info(f"Loaded {len(sections)} knowledge sections")
    except Exception as e:
        logger.error(f"Error loading knowledge sections: {e}")
        raise RuntimeError(f"Failed to load knowledge sections: {str(e)}")


def load_category_guidance():
    categories = {
        "Programming Languages": "A graph database connects languages to frameworks, libraries, and use cases without joining many separate tables.",
        "Web Development": "Graph relationships make it easier to trace how browsers, frameworks, APIs, and frontend tools depend on one another.",
        "Backend Frameworks": "A graph database can map frameworks to languages, services, integrations, and deployment patterns as those connections evolve.",
        "Artificial Intelligence": "Graph traversal reveals model prerequisites, related techniques, and the path from foundational mathematics to applied AI.",
        "Data Science": "Graphs connect datasets, tools, methods, and outcomes, making lineage and related analytical approaches easier to explore.",
        "Mathematics": "A graph database represents prerequisite chains between mathematical ideas without requiring a rigid hierarchy.",
        "Networking": "Graphs model devices, protocols, layers, and dependencies directly, which is useful for tracing routes and impact.",
        "Databases": "Graph databases are especially useful here when the important question is how data stores, indexes, and systems relate to each other.",
        "Software Engineering": "Graphs connect repositories, tests, delivery practices, and teams to show dependencies that are difficult to see in flat records.",
        "Cloud Computing": "A graph can map cloud services to architectures, regions, resources, and operational dependencies for impact analysis.",
        "DevOps": "Graph relationships help trace how code, infrastructure, monitoring, and deployment workflows affect one another.",
        "Security": "Graphs expose relationships between identities, permissions, threats, controls, and protected resources for faster investigation.",
        "Mobile Development": "A graph connects platforms, languages, frameworks, devices, and release concerns across a changing ecosystem.",
        "Blockchain": "Graph structures naturally represent wallets, transactions, contracts, assets, and their paths across a network.",
        "UI/UX Design": "Graphs connect user needs, interface patterns, components, and accessibility decisions so design systems remain discoverable.",
    }

    try:
        session = seed_connection.get_session()
        for name, explanation in categories.items():
            session.run("""
                MERGE (c:KnowledgeCategory {name: $name})
                SET c.graph_database_comparison = $explanation,
                    c.created_at = datetime()
            """, {'name': name, 'explanation': explanation})
        session.close()
        logger.info(f"Loaded guidance for {len(categories)} categories")
    except Exception as e:
        logger.error(f"Error loading category guidance: {e}")
        raise RuntimeError(f"Failed to load category guidance: {str(e)}")


def load_relationship_guidance():
    relationships = {
        "BUILDS_ON": "The source topic depends on, extends, or provides a foundation for the target topic.",
        "RELATED_TO": "The two topics share a meaningful association without a strict dependency.",
        "PART_OF": "The source topic belongs to or is a component of the target concept.",
        "APPLIES_TO": "The source concept is used in or applied to the target area.",
        "CONTRADICTS": "The source and target represent opposing approaches, claims, or choices.",
    }

    try:
        session = seed_connection.get_session()
        for name, description in relationships.items():
            session.run("""
                MERGE (r:RelationshipType {name: $name})
                SET r.description = $description,
                    r.created_at = datetime()
            """, {'name': name, 'description': description})
        session.close()
        logger.info(f"Loaded guidance for {len(relationships)} relationship types")
    except Exception as e:
        logger.error(f"Error loading relationship guidance: {e}")
        raise RuntimeError(f"Failed to load relationship guidance: {str(e)}")


def topic_learning_content(name, description, category):
    examples = {
        "Artificial Intelligence": ["recommendation systems", "fraud detection", "image and language understanding"],
        "Data Science": ["customer analysis", "forecasting", "data quality investigation"],
        "Databases": ["dependency mapping", "recommendation queries", "data lineage"],
        "Software Engineering": ["code review", "testing workflows", "release impact analysis"],
        "Cloud Computing": ["service dependency mapping", "resource inventory", "incident impact analysis"],
        "DevOps": ["deployment tracking", "service ownership", "observability workflows"],
        "Security": ["identity investigation", "permission analysis", "threat detection"],
    }
    snippets = {
        "Programming Languages": ("python", f"print('{name} is ready to explore')"),
        "Web Development": ("javascript", f"const topic = '{name}'\nconsole.log(topic)"),
        "Artificial Intelligence": ("python", "features = [[0.2, 0.8], [0.7, 0.3]]\npredictions = model.predict(features)"),
        "Data Science": ("python", "summary = data.groupby('category').size()\nprint(summary)"),
        "Databases": ("cypher", "MATCH (topic:Topic {name: $topic_name})-[r]-(related)\nRETURN topic, r, related"),
        "Networking": ("python", "response = requests.get('https://example.com')\nprint(response.status_code)"),
        "Software Engineering": ("bash", "git add .\ngit commit -m 'Trace connected change'"),
        "Cloud Computing": ("yaml", "services:\n  api:\n    deploy: rolling"),
        "DevOps": ("yaml", "pipeline:\n  stages: [test, build, deploy]"),
        "Security": ("python", "if user.has_permission('read'):\n    allow_request()"),
    }
    resources = {
        "Programming Languages": ["https://www.python.org/about/", "https://dev.java/learn/", "https://isocpp.org/get-started"],
        "Web Development": ["https://react.dev/learn", "https://vite.dev/guide/", "https://developer.mozilla.org/en-US/docs/Learn"],
        "Backend Frameworks": ["https://www.djangoproject.com/start/", "https://fastapi.tiangolo.com/", "https://expressjs.com/"],
        "Artificial Intelligence": ["https://developers.google.com/machine-learning/crash-course", "https://huggingface.co/learn", "https://pytorch.org/tutorials/"],
        "Data Science": ["https://pandas.pydata.org/docs/getting_started/intro_tutorials/", "https://numpy.org/learn/", "https://jupyter.org/try"],
        "Mathematics": ["https://www.khanacademy.org/math", "https://www.3blue1brown.com/topics/linear-algebra"],
        "Networking": ["https://developer.mozilla.org/en-US/docs/Web/HTTP", "https://www.cloudflare.com/learning/network-layer/what-is-a-protocol/"],
        "Databases": ["https://neo4j.com/docs/getting-started/", "https://console.cognodb.com/", "https://www.postgresql.org/docs/"],
        "Software Engineering": ["https://git-scm.com/book/en/v2", "https://docs.github.com/en/get-started", "https://martinfowler.com/"],
        "Cloud Computing": ["https://aws.amazon.com/getting-started/", "https://learn.microsoft.com/en-us/azure/"],
        "DevOps": ["https://docs.docker.com/get-started/", "https://kubernetes.io/docs/tutorials/", "https://opentelemetry.io/docs/"],
        "Security": ["https://owasp.org/www-project-top-ten/", "https://developer.mozilla.org/en-US/docs/Web/Security"],
        "Mobile Development": ["https://developer.android.com/", "https://developer.apple.com/tutorials/"],
        "Blockchain": ["https://ethereum.org/en/learn/", "https://developer.bitcoin.org/"],
        "UI/UX Design": ["https://www.figma.com/resources/learn-design/", "https://www.w3.org/WAI/fundamentals/accessibility-intro/"],
    }
    topic_resources = {
        "CognoDB": ["https://console.cognodb.com/", "https://cognodb.com/"],
        "Graph Database": ["https://console.cognodb.com/", "https://neo4j.com/docs/getting-started/"],
        "Python": ["https://docs.python.org/3/tutorial/", "https://realpython.com/"],
        "React": ["https://react.dev/learn", "https://vite.dev/guide/"],
        "Vite": ["https://vite.dev/guide/", "https://vite.dev/guide/features.html"],
        "Java": ["https://dev.java/learn/", "https://docs.oracle.com/en/java/"],
        "C++": ["https://isocpp.org/get-started", "https://en.cppreference.com/w/"],
        "JavaScript": ["https://developer.mozilla.org/en-US/docs/Web/JavaScript", "https://javascript.info/"],
    }
    topic_images = {
        "Python": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?auto=format&fit=crop&w=1200&q=85",
        "React": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=1200&q=85",
        "Java": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=1200&q=85",
        "C++": "https://images.unsplash.com/photo-1516116216624-53e697fedbea?auto=format&fit=crop&w=1200&q=85",
        "Graph Database": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=85",
        "Machine Learning": "https://images.unsplash.com/photo-1555255707-c07966088b7b?auto=format&fit=crop&w=1200&q=85",
    }
    code_images = {
        "python": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=900&q=85",
        "javascript": "https://images.unsplash.com/photo-1627398242454-45a1465c2479?auto=format&fit=crop&w=900&q=85",
        "jsx": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=900&q=85",
        "java": "https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?auto=format&fit=crop&w=900&q=85",
        "cpp": "https://images.unsplash.com/photo-1516116216624-53e697fedbea?auto=format&fit=crop&w=900&q=85",
        "cypher": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=900&q=85",
    }
    language, snippet = snippets.get(category, ("text", f"# Explore {name}\n{name}"))
    language_overrides = {
        "Python": ("python", "topics = ['graphs', 'relationships']\nprint(topics)"),
        "Java": ("java", "var topic = \"Java\";\nSystem.out.println(topic);"),
        "C++": ("cpp", "#include <iostream>\nint main() { std::cout << \"C++\"; }"),
        "React": ("jsx", "export default function Topic() {\n  return <h1>React</h1>\n}"),
        "Vite": ("bash", "npm create vite@latest nexus-ui\nnpm run dev"),
        "Graph Database": ("cypher", "MATCH (topic:Topic)-[relationship]->(related:Topic)\nRETURN topic, relationship, related"),
    }
    language, snippet = language_overrides.get(name, (language, snippet))
    use_cases = examples.get(category, [f"learning {name}", f"connecting {name} to related concepts", f"comparing {name} with neighboring topics"])
    article = "\n\n".join([
        f"{name} belongs to the {category} domain. {description}. In NexusKnowledge, this topic is presented as part of a connected body of ideas rather than as an isolated definition.",
        f"A useful way to approach {name} is to start with its purpose, then identify the problem it solves and the constraints it introduces. This makes the topic easier to compare with nearby ideas in the {category} space.",
        f"In practice, {name} can be understood through examples such as {use_cases[0]}, {use_cases[1]}, and {use_cases[2]}. These examples show why context, dependencies, and neighboring concepts matter when people learn or make technical decisions.",
        f"When working with {name}, pay attention to the boundary between the concept and the tools built around it. The surrounding ecosystem often determines how a technique is adopted, tested, monitored, and maintained over time.",
        f"A strong learning path for {name} combines a small practical example with deliberate comparison. Try connecting the topic to one prerequisite, one related idea, and one application so that its role becomes clear beyond a single definition.",
        f"The graph model links {name} to other topics with typed relationships such as BUILDS_ON, RELATED_TO, PART_OF, and APPLIES_TO. CognoDB makes those paths queryable, allowing users to move from this topic to useful prerequisites, applications, and related technologies."
    ])
    resource_links = topic_resources.get(name, resources.get(category, ["https://cognodb.com/"]))
    topic_image = topic_images.get(name, "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85")
    code_image = code_images.get(language, code_images['python'])
    graph_image = "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=85"
    cypher = "MATCH path = (topic:Topic {name: $topic_name})-[*1..2]-(related:Topic) WHERE related.name <> $topic_name RETURN related.name, length(path) AS distance ORDER BY distance"
    return article, use_cases, resource_links, topic_image, code_image, graph_image, language, snippet, cypher


def load_topics():
    topics = [
        ("Python", "High-level, interpreted programming language known for readability and versatility", "Programming Languages", 10),
        ("JavaScript", "Dynamic programming language essential for web development", "Programming Languages", 10),
        ("Java", "Object-oriented, class-based programming language for enterprise applications", "Programming Languages", 9),
        ("C++", "General-purpose programming language with object-oriented features", "Programming Languages", 8),
        ("Go", "Statically typed, compiled language designed for simplicity and efficiency", "Programming Languages", 8),
        ("Rust", "Systems programming language focused on safety and performance", "Programming Languages", 7),
        ("TypeScript", "Typed superset of JavaScript that compiles to plain JavaScript", "Programming Languages", 9),
        ("Swift", "General-purpose, multi-paradigm, compiled programming language for iOS", "Programming Languages", 7),
        ("Kotlin", "Cross-platform, statically typed, general-purpose programming language", "Programming Languages", 7),
        ("Ruby", "Dynamic, object-oriented scripting language focused on simplicity", "Programming Languages", 6),
        ("HTML", "Standard markup language for creating web pages", "Web Development", 10),
        ("CSS", "Style sheet language used for describing the presentation of a document", "Web Development", 10),
        ("React", "JavaScript library for building user interfaces", "Web Development", 10),
        ("Vue.js", "Progressive JavaScript framework for building user interfaces", "Web Development", 8),
        ("Angular", "Platform and framework for building single-page client applications", "Web Development", 8),
        ("Node.js", "JavaScript runtime built on Chrome's V8 JavaScript engine", "Web Development", 9),
        ("Next.js", "React framework for production with server-side rendering", "Web Development", 8),
        ("Webpack", "Static module bundler for modern JavaScript applications", "Web Development", 7),
        ("Vite", "Next generation frontend tooling for fast development", "Web Development", 8),
        ("Tailwind CSS", "Utility-first CSS framework for rapid UI development", "Web Development", 8),
        ("Django", "High-level Python web framework for rapid development", "Backend Frameworks", 9),
        ("Flask", "Lightweight WSGI web application framework in Python", "Backend Frameworks", 8),
        ("FastAPI", "Modern, fast web framework for building APIs with Python", "Backend Frameworks", 9),
        ("Express.js", "Fast, unopinionated, minimalist web framework for Node.js", "Backend Frameworks", 9),
        ("Spring Boot", "Convention over configuration solution for Spring framework", "Backend Frameworks", 8),
        ("Laravel", "PHP web application framework with expressive syntax", "Backend Frameworks", 7),
        ("PHP", "Server-side scripting language commonly used for web application development", "Programming Languages", 8),
        ("Machine Learning", "Field of study that gives computers the ability to learn without explicit programming", "Artificial Intelligence", 10),
        ("Deep Learning", "Subset of machine learning using neural networks with multiple layers", "Artificial Intelligence", 10),
        ("Neural Networks", "Computing systems inspired by biological neural networks", "Artificial Intelligence", 9),
        ("Natural Language Processing", "Branch of AI that helps computers understand and interpret human language", "Artificial Intelligence", 9),
        ("Computer Vision", "Field of AI that trains computers to interpret and understand visual world", "Artificial Intelligence", 9),
        ("Reinforcement Learning", "Type of machine learning where an agent learns to make decisions", "Artificial Intelligence", 8),
        ("Generative AI", "AI that creates new content rather than analyzing existing content", "Artificial Intelligence", 10),
        ("Large Language Models", "Neural networks trained on vast amounts of text data", "Artificial Intelligence", 10),
        ("Transformer Architecture", "Deep learning architecture that uses self-attention mechanisms", "Artificial Intelligence", 8),
        ("Fine-tuning", "Process of adapting a pre-trained model to a specific task", "Artificial Intelligence", 7),
        ("Data Science", "Interdisciplinary field that uses scientific methods to extract knowledge from data", "Data Science", 10),
        ("Data Analysis", "Process of inspecting and modeling data to discover useful information", "Data Science", 9),
        ("Data Visualization", "Graphical representation of information and data", "Data Science", 8),
        ("Pandas", "Python library for data manipulation and analysis", "Data Science", 10),
        ("NumPy", "Fundamental package for scientific computing with Python", "Data Science", 9),
        ("Matplotlib", "Plotting library for creating static, animated, and interactive visualizations", "Data Science", 8),
        ("Seaborn", "Statistical data visualization library based on matplotlib", "Data Science", 8),
        ("Jupyter Notebook", "Open-source web application for creating and sharing documents with code", "Data Science", 9),
        ("Calculus", "Mathematical study of continuous change", "Mathematics", 9),
        ("Linear Algebra", "Study of vectors, vector spaces, and linear transformations", "Mathematics", 9),
        ("Statistics", "Collection, analysis, interpretation, and presentation of data", "Mathematics", 9),
        ("Probability", "Study of uncertainty and random events", "Mathematics", 8),
        ("Discrete Mathematics", "Study of mathematical structures that are fundamentally discrete", "Mathematics", 7),
        ("Optimization", "Selection of best element from set of available alternatives", "Mathematics", 8),
        ("HTTP", "Foundation of data communication for the World Wide Web", "Networking", 9),
        ("HTTPS", "Extension of HTTP for secure communication over computer network", "Networking", 9),
        ("REST", "Architectural style for distributed hypermedia systems", "Networking", 8),
        ("GraphQL", "Query language for APIs and runtime for executing queries", "Networking", 8),
        ("WebSocket", "Communication protocol providing full-duplex communication channels", "Networking", 7),
        ("TCP/IP", "Set of communication protocols used to interconnect network devices", "Networking", 8),
        ("DNS", "Hierarchical and decentralized naming system for computers", "Networking", 7),
        ("SQL", "Domain-specific language used in programming and designed for managing data", "Databases", 10),
        ("PostgreSQL", "Powerful, open source object-relational database system", "Databases", 9),
        ("MySQL", "Open-source relational database management system", "Databases", 9),
        ("MongoDB", "Document-oriented NoSQL database program", "Databases", 8),
        ("Redis", "In-memory data structure store used as database and cache", "Databases", 8),
        ("Graph Database", "Database designed for storing and querying connected data", "Databases", 8),
        ("Elasticsearch", "Search and analytics engine based on Lucene library", "Databases", 7),
        ("Database Indexing", "Data structure technique to improve data retrieval speed", "Databases", 7),
        ("Version Control", "System that records changes to files over time", "Software Engineering", 9),
        ("Git", "Distributed version control system for tracking changes in code", "Software Engineering", 10),
        ("GitHub", "Web-based platform for version control and collaboration", "Software Engineering", 9),
        ("CI/CD", "Practice of continuous integration and continuous deployment", "Software Engineering", 9),
        ("Testing", "Process of evaluating and verifying that a software application works", "Software Engineering", 9),
        ("Unit Testing", "Software testing method where individual units of source code are tested", "Software Engineering", 8),
        ("Integration Testing", "Phase in software testing where individual software modules are combined", "Software Engineering", 8),
        ("TDD", "Software development process relying on software requirements being converted to test cases", "Software Engineering", 7),
        ("Code Review", "Systematic examination of computer source code", "Software Engineering", 8),
        ("Refactoring", "Process of restructuring existing computer code without changing its external behavior", "Software Engineering", 7),
        ("AWS", "Cloud computing platform provided by Amazon", "Cloud Computing", 10),
        ("Azure", "Cloud computing platform by Microsoft", "Cloud Computing", 9),
        ("Google Cloud", "Suite of cloud computing services by Google", "Cloud Computing", 9),
        ("Docker", "Platform for developing, shipping, and running applications in containers", "Cloud Computing", 9),
        ("Kubernetes", "Container orchestration platform for automating deployment and scaling", "Cloud Computing", 9),
        ("Serverless", "Cloud computing execution model where cloud provider manages server", "Cloud Computing", 8),
        ("Microservices", "Architectural style that structures an application as a collection of services", "Cloud Computing", 8),
        ("DevOps", "Set of practices that combines software development and IT operations", "DevOps", 9),
        ("Infrastructure as Code", "Process of managing and provisioning computer data centers", "DevOps", 8),
        ("Terraform", "Infrastructure as code software tool", "DevOps", 8),
        ("Ansible", "Open-source software provisioning, configuration management, and application deployment", "DevOps", 7),
        ("Monitoring", "Process of observing the state of systems and services", "DevOps", 8),
        ("Logging", "Recording of events in a computer system", "DevOps", 7),
        ("Cybersecurity", "Practice of protecting systems, networks, and programs from digital attacks", "Security", 10),
        ("Encryption", "Process of encoding information to prevent unauthorized access", "Security", 9),
        ("Authentication", "Process of verifying the identity of a user or system", "Security", 9),
        ("Authorization", "Process of determining what resources an authenticated user can access", "Security", 8),
        ("OAuth", "Open standard for access delegation", "Security", 8),
        ("JWT", "Compact URL-safe means of representing claims to be transferred between two parties", "Security", 8),
        ("HTTPS", "Secure communication protocol over computer network", "Security", 9),
        ("Firewall", "Network security system that monitors and controls incoming and outgoing traffic", "Security", 7),
        ("iOS Development", "Process of creating mobile applications for Apple's iOS operating system", "Mobile Development", 8),
        ("Android Development", "Process of creating applications for Android operating system", "Mobile Development", 8),
        ("React Native", "Framework for building native apps using React", "Mobile Development", 8),
        ("Flutter", "UI toolkit for building natively compiled applications", "Mobile Development", 7),
        ("Swift", "Programming language for iOS and macOS development", "Mobile Development", 7),
        ("Kotlin", "Programming language for Android development", "Mobile Development", 7),
        ("Blockchain", "Distributed ledger technology that records transactions across many computers", "Blockchain", 8),
        ("Smart Contracts", "Self-executing contracts with the terms directly written into code", "Blockchain", 7),
        ("Cryptocurrency", "Digital or virtual currency secured by cryptography", "Blockchain", 7),
        ("Ethereum", "Decentralized platform that runs smart contracts", "Blockchain", 7),
        ("Bitcoin", "Decentralized digital currency without a central bank", "Blockchain", 6),
        ("UI Design", "Process of designing user interfaces for software and computerized devices", "UI/UX Design", 8),
        ("UX Design", "Process of enhancing user satisfaction by improving usability and accessibility", "UI/UX Design", 9),
        ("Figma", "Collaborative interface design tool", "UI/UX Design", 8),
        ("Design Systems", "Collection of reusable components guided by clear standards", "UI/UX Design", 7),
        ("Accessibility", "Practice of making your websites usable by as many people as possible", "UI/UX Design", 8),
        ("Responsive Design", "Approach to web design that makes web pages render well on all devices", "UI/UX Design", 9),
        ("AI", "Broad field of building systems that perform tasks associated with human intelligence", "Artificial Intelligence", 10),
        ("API", "Defined interface that allows software systems to communicate with one another", "Web Development", 9),
        ("NoSQL", "Family of non-relational databases designed for flexible or distributed data models", "Databases", 8),
        ("Software Engineering", "Disciplined practice of designing, building, testing, and maintaining software", "Software Engineering", 10),
        ("Cloud Computing", "On-demand delivery of computing resources over a network", "Cloud Computing", 10),
        ("Security", "Practice of protecting systems, data, and services from unauthorized access or disruption", "Security", 10),
        ("Web Development", "Practice of building websites and web applications from connected frontend and backend technologies", "Web Development", 10),
        ("Mobile Development", "Practice of building applications for mobile operating systems and devices", "Mobile Development", 9),
    ]
    
    try:
        session = seed_connection.get_session()
        for name, description, category, importance in topics:
            article, examples, resource_links, topic_image, code_image, graph_image, code_language, code_snippet, cypher_example = topic_learning_content(name, description, category)
            session.run("""
                MERGE (t:Topic {name: $name})
                SET t.description = $description,
                    t.category = $category,
                    t.importance = $importance,
                    t.article_content = $article_content,
                    t.real_world_examples = $real_world_examples,
                    t.resource_links = $resource_links,
                    t.topic_image = $topic_image,
                    t.code_image = $code_image,
                    t.graph_image = $graph_image,
                    t.code_language = $code_language,
                    t.code_snippet = $code_snippet,
                    t.cypher_example = $cypher_example,
                    t.created_at = datetime()
            """, {'name': name, 'description': description, 'category': category, 'importance': importance,
                  'article_content': article, 'real_world_examples': examples, 'resource_links': resource_links, 'topic_image': topic_image,
                  'code_image': code_image, 'graph_image': graph_image, 'code_language': code_language,
                  'code_snippet': code_snippet, 'cypher_example': cypher_example})
        session.close()
        logger.info(f"Loaded {len(topics)} topics")
    except Exception as e:
        logger.error(f"Error loading topics: {e}")
        raise RuntimeError(f"Failed to load topics: {str(e)}")


def load_relationships():
    relationships = [
        ("TypeScript", "JavaScript", RelationshipType.BUILDS_ON),
        ("React", "JavaScript", RelationshipType.BUILDS_ON),
        ("React", "TypeScript", RelationshipType.RELATED_TO),
        ("Vue.js", "JavaScript", RelationshipType.BUILDS_ON),
        ("Angular", "TypeScript", RelationshipType.BUILDS_ON),
        ("Next.js", "React", RelationshipType.BUILDS_ON),
        ("Node.js", "JavaScript", RelationshipType.BUILDS_ON),
        ("Express.js", "Node.js", RelationshipType.BUILDS_ON),
        ("Django", "Python", RelationshipType.BUILDS_ON),
        ("Flask", "Python", RelationshipType.BUILDS_ON),
        ("FastAPI", "Python", RelationshipType.BUILDS_ON),
        ("Laravel", "PHP", RelationshipType.RELATED_TO),
        ("Spring Boot", "Java", RelationshipType.BUILDS_ON),
        ("JavaScript", "HTML", RelationshipType.BUILDS_ON),
        ("JavaScript", "CSS", RelationshipType.BUILDS_ON),
        ("React", "HTML", RelationshipType.APPLIES_TO),
        ("React", "CSS", RelationshipType.APPLIES_TO),
        ("Vue.js", "HTML", RelationshipType.APPLIES_TO),
        ("Tailwind CSS", "CSS", RelationshipType.RELATED_TO),
        ("Webpack", "JavaScript", RelationshipType.RELATED_TO),
        ("Vite", "JavaScript", RelationshipType.RELATED_TO),
        ("Deep Learning", "Machine Learning", RelationshipType.BUILDS_ON),
        ("Deep Learning", "Neural Networks", RelationshipType.BUILDS_ON),
        ("Neural Networks", "Linear Algebra", RelationshipType.BUILDS_ON),
        ("Machine Learning", "Python", RelationshipType.BUILDS_ON),
        ("Machine Learning", "Statistics", RelationshipType.BUILDS_ON),
        ("Machine Learning", "Calculus", RelationshipType.BUILDS_ON),
        ("Natural Language Processing", "Machine Learning", RelationshipType.BUILDS_ON),
        ("Computer Vision", "Deep Learning", RelationshipType.BUILDS_ON),
        ("Reinforcement Learning", "Machine Learning", RelationshipType.BUILDS_ON),
        ("Generative AI", "Deep Learning", RelationshipType.BUILDS_ON),
        ("Generative AI", "Neural Networks", RelationshipType.BUILDS_ON),
        ("Large Language Models", "Deep Learning", RelationshipType.BUILDS_ON),
        ("Large Language Models", "Natural Language Processing", RelationshipType.BUILDS_ON),
        ("Transformer Architecture", "Neural Networks", RelationshipType.BUILDS_ON),
        ("Fine-tuning", "Large Language Models", RelationshipType.BUILDS_ON),
        ("Data Science", "Python", RelationshipType.BUILDS_ON),
        ("Data Science", "Statistics", RelationshipType.BUILDS_ON),
        ("Data Science", "Machine Learning", RelationshipType.RELATED_TO),
        ("Data Analysis", "Data Science", RelationshipType.PART_OF),
        ("Data Visualization", "Data Science", RelationshipType.PART_OF),
        ("Pandas", "Python", RelationshipType.RELATED_TO),
        ("NumPy", "Python", RelationshipType.RELATED_TO),
        ("Matplotlib", "Python", RelationshipType.RELATED_TO),
        ("Seaborn", "Matplotlib", RelationshipType.BUILDS_ON),
        ("Jupyter Notebook", "Python", RelationshipType.RELATED_TO),
        ("HTTPS", "HTTP", RelationshipType.BUILDS_ON),
        ("REST", "HTTP", RelationshipType.BUILDS_ON),
        ("GraphQL", "HTTP", RelationshipType.BUILDS_ON),
        ("WebSocket", "HTTP", RelationshipType.RELATED_TO),
        ("GraphQL", "REST", RelationshipType.CONTRADICTS),
        ("TCP/IP", "HTTP", RelationshipType.BUILDS_ON),
        ("DNS", "HTTP", RelationshipType.BUILDS_ON),
        ("PostgreSQL", "SQL", RelationshipType.RELATED_TO),
        ("MySQL", "SQL", RelationshipType.RELATED_TO),
        ("MongoDB", "NoSQL", RelationshipType.RELATED_TO),
        ("Redis", "NoSQL", RelationshipType.RELATED_TO),
        ("Graph Database", "NoSQL", RelationshipType.PART_OF),
        ("Graph Database", "SQL", RelationshipType.CONTRADICTS),
        ("Elasticsearch", "NoSQL", RelationshipType.RELATED_TO),
        ("Database Indexing", "SQL", RelationshipType.RELATED_TO),
        ("Database Indexing", "NoSQL", RelationshipType.RELATED_TO),
        ("Git", "Version Control", RelationshipType.PART_OF),
        ("GitHub", "Git", RelationshipType.RELATED_TO),
        ("CI/CD", "Git", RelationshipType.BUILDS_ON),
        ("CI/CD", "Testing", RelationshipType.BUILDS_ON),
        ("Unit Testing", "Testing", RelationshipType.PART_OF),
        ("Integration Testing", "Testing", RelationshipType.PART_OF),
        ("TDD", "Unit Testing", RelationshipType.RELATED_TO),
        ("Code Review", "Git", RelationshipType.RELATED_TO),
        ("Refactoring", "Software Engineering", RelationshipType.PART_OF),
        ("Docker", "Kubernetes", RelationshipType.BUILDS_ON),
        ("Kubernetes", "Cloud Computing", RelationshipType.PART_OF),
        ("Microservices", "Cloud Computing", RelationshipType.RELATED_TO),
        ("Serverless", "Cloud Computing", RelationshipType.RELATED_TO),
        ("AWS", "Cloud Computing", RelationshipType.PART_OF),
        ("Azure", "Cloud Computing", RelationshipType.PART_OF),
        ("Google Cloud", "Cloud Computing", RelationshipType.PART_OF),
        ("DevOps", "Cloud Computing", RelationshipType.RELATED_TO),
        ("Infrastructure as Code", "DevOps", RelationshipType.PART_OF),
        ("Terraform", "Infrastructure as Code", RelationshipType.PART_OF),
        ("Ansible", "DevOps", RelationshipType.PART_OF),
        ("Monitoring", "DevOps", RelationshipType.PART_OF),
        ("Logging", "Monitoring", RelationshipType.RELATED_TO),
        ("Authentication", "Cybersecurity", RelationshipType.PART_OF),
        ("Authorization", "Authentication", RelationshipType.BUILDS_ON),
        ("OAuth", "Authentication", RelationshipType.RELATED_TO),
        ("JWT", "Authentication", RelationshipType.RELATED_TO),
        ("Encryption", "Cybersecurity", RelationshipType.PART_OF),
        ("HTTPS", "Encryption", RelationshipType.BUILDS_ON),
        ("Firewall", "Cybersecurity", RelationshipType.PART_OF),
        ("React Native", "React", RelationshipType.BUILDS_ON),
        ("React Native", "Mobile Development", RelationshipType.PART_OF),
        ("Flutter", "Mobile Development", RelationshipType.PART_OF),
        ("Swift", "iOS Development", RelationshipType.BUILDS_ON),
        ("Kotlin", "Android Development", RelationshipType.BUILDS_ON),
        ("Smart Contracts", "Blockchain", RelationshipType.PART_OF),
        ("Cryptocurrency", "Blockchain", RelationshipType.PART_OF),
        ("Ethereum", "Blockchain", RelationshipType.PART_OF),
        ("Ethereum", "Smart Contracts", RelationshipType.BUILDS_ON),
        ("Bitcoin", "Blockchain", RelationshipType.PART_OF),
        ("Bitcoin", "Cryptocurrency", RelationshipType.PART_OF),
        ("UI Design", "UX Design", RelationshipType.RELATED_TO),
        ("Figma", "UI Design", RelationshipType.RELATED_TO),
        ("Figma", "UX Design", RelationshipType.RELATED_TO),
        ("Design Systems", "UI Design", RelationshipType.BUILDS_ON),
        ("Accessibility", "UX Design", RelationshipType.BUILDS_ON),
        ("Responsive Design", "UI Design", RelationshipType.BUILDS_ON),
        ("Responsive Design", "UX Design", RelationshipType.BUILDS_ON),
        ("Python", "Data Science", RelationshipType.APPLIES_TO),
        ("Python", "AI", RelationshipType.APPLIES_TO),
        ("Python", "Web Development", RelationshipType.APPLIES_TO),
        ("JavaScript", "Web Development", RelationshipType.APPLIES_TO),
        ("Linear Algebra", "Machine Learning", RelationshipType.BUILDS_ON),
        ("Calculus", "Machine Learning", RelationshipType.BUILDS_ON),
        ("Statistics", "Data Science", RelationshipType.BUILDS_ON),
        ("SQL", "Data Science", RelationshipType.BUILDS_ON),
        ("API", "Web Development", RelationshipType.PART_OF),
        ("REST", "API", RelationshipType.RELATED_TO),
        ("GraphQL", "API", RelationshipType.RELATED_TO),
        ("Docker", "DevOps", RelationshipType.BUILDS_ON),
        ("Kubernetes", "DevOps", RelationshipType.BUILDS_ON),
        ("Security", "DevOps", RelationshipType.BUILDS_ON),
        ("Security", "Cloud Computing", RelationshipType.BUILDS_ON),
    ]
    
    try:
        session = seed_connection.get_session()
        for from_topic, to_topic, rel_type in relationships:
            session.run(RELATIONSHIP_QUERIES[rel_type], {'from_name': from_topic, 'to_name': to_topic})
        session.close()
        logger.info(f"Loaded {len(relationships)} relationships")
    except Exception as e:
        logger.error(f"Error loading relationships: {e}")
        raise RuntimeError(f"Failed to load relationships: {str(e)}")


def load_all_data():
    try:
        logger.info("Starting NexusKnowledge data loading...")
        clear_database()
        create_constraints()
        load_topics()
        load_category_guidance()
        load_knowledge_sections()
        load_relationships()
        logger.info("NexusKnowledge data loading completed successfully")
    except Exception as e:
        logger.error(f"Data loading failed: {e}")
        sys.exit(1)
    finally:
        seed_connection.close()


if __name__ == "__main__":
    load_all_data()
