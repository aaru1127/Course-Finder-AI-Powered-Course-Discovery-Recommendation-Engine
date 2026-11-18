# CourseFinder — Intelligent Course Discovery & Recommendation Engine

**Project Type:** AI-powered semantic search and recommendation platform  
**Goal:** Build an end-to-end course discovery system using semantic retrieval, hybrid search, ranking, personalization and caching.

**Primary Objective:** Demonstrate practical knowledge of information retrieval, embeddings, recommendation systems, Python backend engineering, SQL and Redis.

**Development Approach:** Incremental MVP — each stage builds on the previous stage.

---

# 1. Project Vision

## What are we building?

CourseFinder is an intelligent learning resource discovery platform that helps users find relevant courses using natural-language queries.

Instead of requiring users to search with exact course titles or keywords, the system understands what they want to learn and recommends relevant courses.

### Example user query

"I am a beginner who wants to learn backend development using Node.js. I prefer practical courses under 20 hours."

The system should understand:

- Subject: Backend development
- Technology: Node.js
- Experience level: Beginner
- Preferred duration: Under 20 hours
- Learning preference: Practical

It then retrieves and ranks the most relevant courses.

### Example results

| Course | Relevance |
|---|---:|
| Node.js Backend Development for Beginners | 96% |
| Complete Node.js and Express Course | 92% |
| Building REST APIs with Node.js | 89% |
| Advanced Backend Architecture | 71% |

Scores should be derived from actual retrieval and ranking signals, not fabricated by an LLM.

## Core objectives

1. Ingest and process course information.
2. Generate semantic embeddings for course descriptions.
3. Implement keyword-based search using BM25.
4. Implement vector-based semantic retrieval.
5. Combine both approaches using hybrid search.
6. Rank courses based on relevance.
7. Support difficulty, duration and technology filters.
8. Recommend similar courses.
9. Use Redis to improve response times.
10. Evaluate retrieval quality quantitatively.

---

# 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Frontend | React + Vite | User interface |
| Backend | Python + FastAPI | APIs and business logic |
| Database | PostgreSQL | Course metadata |
| Vector search | pgvector | Embedding storage and retrieval |
| Embeddings | Sentence Transformers | Semantic representation |
| Keyword search | BM25 | Keyword-based retrieval |
| Hybrid ranking | Reciprocal Rank Fusion | Merge retrieval results |
| Cache | Redis | Cache frequently requested results |
| Background processing | Python workers | Course ingestion and embedding generation |
| Deployment | Docker + Docker Compose | Containerization |

### Why these technologies?

**PostgreSQL:** Stores structured course information.

**pgvector:** Stores embeddings and enables similarity search.

**Redis:** Stores frequently requested search results, reducing repeated computation and database queries.

**FastAPI:** Provides asynchronous API support and integrates well with Python-based ML components.

**Sentence Transformers:** Generates vector embeddings without needing to train an embedding model from scratch.

---

# 3. System Architecture

The overall system follows this pipeline:

User Query → Query Processing → Cache Lookup → Retrieval → Ranking → Results

### Detailed architecture

1. User enters a natural-language search query.
2. Backend normalizes the query and extracts applicable filters.
3. Redis checks whether the same normalized search request has already been processed.
4. If cached, return the cached result.
5. Otherwise, generate the query embedding.
6. Perform BM25 keyword retrieval.
7. Perform vector similarity retrieval.
8. Combine results using Reciprocal Rank Fusion.
9. Apply metadata filters and ranking.
10. Store the result in Redis.
11. Return ranked courses through the API.

### Architecture diagram

User / React UI

↓

FastAPI Backend

↓

Query Processing

↓

Redis Cache

↙                       ↘

Cache Hit          Cache Miss

↓                         ↓

Return Result       Query Embedding

                          ↓

                BM25 + Vector Retrieval

                          ↓

                    Hybrid Ranking

                          ↓

                 PostgreSQL + pgvector

                          ↓

                   Store in Redis

                          ↓

                    Return Results

---

# 4. Incremental Development Stages

Each stage introduces one new capability.

## STAGE 0 — Understand Information Retrieval

**Objective:** Understand the fundamentals before implementing the search engine.

### Topics to learn

- What is an information retrieval system?
- What is traditional keyword search?
- What is semantic search?
- What are embeddings?
- What is vector similarity?
- What is a recommendation system?
- What is ranking?
- What is caching?

### Practical exercise

Consider these two queries:

Query A: "Node.js backend course"

Query B: "I want to learn how to build server-side applications using JavaScript."

A traditional keyword search might struggle to identify their relationship.

A semantic search engine should recognize that both queries express similar learning intent.

### Completion criteria

- [ ] Understand keyword search.
- [ ] Understand semantic search.
- [ ] Understand embeddings.
- [ ] Understand ranking.
- [ ] Understand the purpose of caching.

**Deliverable:** Conceptual understanding of the complete search pipeline.

---

## STAGE 1 — Course Dataset and Data Modeling

**Objective:** Create a structured dataset of learning resources.

We need actual course information to build a meaningful search system.

### Course data structure

Each course should contain:

- id
- title
- provider
- description
- skills
- category
- difficulty
- duration_hours
- language
- price
- rating (if available)
- course_url

### Example

{
  "id": "course_001",
  "title": "Node.js Backend Development",
  "provider": "Example Academy",
  "description": "Learn Node.js, Express, REST APIs and backend development.",
  "skills": ["Node.js", "Express", "REST APIs"],
  "category": "Backend Development",
  "difficulty": "Beginner",
  "duration_hours": 12,
  "language": "English"
}

### Implementation

1. Collect course data from legitimate sources.
2. Start with approximately 300–1,000 course records.
3. Load records using Python.
4. Clean missing and malformed fields.
5. Remove duplicate courses.
6. Design the PostgreSQL schema.
7. Store course information.

Use openly accessible datasets or permitted course catalog sources. Do not assume that a website permits unrestricted scraping.

### Concepts to learn

- JSON and CSV processing.
- Python data structures.
- SQL schema design.
- Database normalization.
- Data cleaning.
- Indexing.

### Completion criteria

- [ ] Course dataset prepared.
- [ ] Consistent schema.
- [ ] Duplicate records removed.
- [ ] PostgreSQL configured.
- [ ] Course records stored.

**Deliverable:** Structured course database.

---

## STAGE 2 — Traditional Keyword Search with BM25

**Objective:** Implement search without embeddings.

We first need a baseline search engine.

### Implementation

Build a function that searches course titles, descriptions and skills.

Example:

Input: "Node.js Express backend"

The engine should return courses containing relevant keywords.

Initially implement basic matching, then implement BM25.

### Concepts to learn

- Tokenization.
- Term frequency.
- Inverse document frequency.
- TF-IDF.
- BM25.
- Document ranking.

### Important questions

1. How does BM25 work?
2. Why does it outperform simple keyword matching?
3. What happens when a query uses different words from the course description?
4. What are the limitations of lexical retrieval?

### Completion criteria

- [ ] Keyword search implemented.
- [ ] BM25 scoring working.
- [ ] Courses returned in ranked order.
- [ ] Search limitations understood.

**Deliverable:** BM25 course search engine.

---

## STAGE 3 — Semantic Search Using Embeddings

**Objective:** Enable search based on meaning rather than exact words.

### What are embeddings?

Embeddings convert text into numerical vectors representing semantic meaning.

For example:

"Learn backend development with Node.js"

and

"Build server-side applications using JavaScript"

Should produce semantically related vector representations.

### Implementation

1. Install Sentence Transformers.
2. Select a pretrained embedding model.
3. Generate embeddings for course titles and descriptions.
4. Understand the vector dimensions.
5. Generate an embedding for incoming queries.
6. Calculate cosine similarity.
7. Retrieve the most similar courses.

### Concepts to learn

- Vector representations.
- Embedding models.
- Semantic similarity.
- Cosine similarity.
- Vector dimensions.
- Embedding normalization.

### Completion criteria

- [ ] Course embeddings generated.
- [ ] Query embeddings generated.
- [ ] Cosine similarity implemented.
- [ ] Top relevant courses retrieved.
- [ ] Semantic search tested.

**Deliverable:** Working semantic course search.

---

## STAGE 4 — PostgreSQL + pgvector

**Objective:** Move from in-memory similarity calculations to database-backed vector retrieval.

### Implementation

1. Configure PostgreSQL.
2. Install and enable pgvector.
3. Create the courses table.
4. Add a vector column.
5. Store course embeddings.
6. Generate query embeddings.
7. Retrieve nearest courses using vector similarity.
8. Return associated metadata.

### Concepts to learn

- Vector databases.
- pgvector.
- Vector distance operators.
- Cosine distance.
- Exact nearest-neighbour search.
- Approximate nearest-neighbour indexing.
- HNSW indexing.

### Completion criteria

- [ ] pgvector configured.
- [ ] Course embeddings stored.
- [ ] Similarity search implemented in SQL.
- [ ] Results include course metadata.
- [ ] Query performance measured.

**Deliverable:** Database-backed semantic retrieval engine.

---

## STAGE 5 — Hybrid Search with Reciprocal Rank Fusion

**Objective:** Combine keyword and semantic search.

This is a core engineering feature of CourseFinder.

### Why hybrid search?

BM25 is effective when users search for exact technologies and terms.

Vector search understands semantic meaning and can retrieve courses even when the wording differs.

Combining them can produce better retrieval results.

### Architecture

User Query

↙                         ↘

BM25 Search          Vector Search

↘                         ↙

Reciprocal Rank Fusion

↓

Combined Ranked Courses

### RRF formula

RRF Score(d) = Σ 1 / (k + rank(d))

Where:

- d = course/document.
- k = a constant, commonly 60.
- rank(d) = position of the course in a retrieval list.

A course appearing high in both retrieval lists receives a stronger combined score.

### Implementation

1. Retrieve top K courses using BM25.
2. Retrieve top K courses using vector search.
3. Combine both result lists.
4. Calculate RRF scores.
5. Merge duplicate course IDs.
6. Return the highest-ranked courses.

### Completion criteria

- [ ] BM25 retrieval working.
- [ ] Vector retrieval working.
- [ ] RRF implemented.
- [ ] Duplicate courses merged.
- [ ] Combined ranking tested.

**Deliverable:** Hybrid course search engine.

---

## STAGE 6 — Redis Integration and Caching

**Objective:** Improve search performance and reduce unnecessary computation.

Redis will be a core infrastructure component, not just another technology in the README.

### What problem are we solving?

Consider a user searching:

"Beginner Python courses"

The search engine:
1. Processes the query.
2. Generates its embedding.
3. Performs BM25 retrieval.
4. Performs vector retrieval.
5. Combines the rankings.
6. Returns the results.

If another user makes the same search, repeating the entire process is unnecessary when the underlying data and ranking configuration have not changed.

Redis can cache the result.

### Implementation A — Search Result Caching

Use Redis to cache search responses.

Example cache key:

course_search:hash_of_normalized_query_and_filters

Example stored value:

{
  "query": "beginner python courses",
  "results": [
    {
      "course_id": "course_001",
      "score": 0.94
    }
  ]
}

Use JSON serialization for the cached response.

Set a TTL, for example 10 minutes.

### Implementation B — Cache-Aside Pattern

Implement the following workflow:

1. User sends a search request.
2. Backend checks Redis.
3. If the cache contains the result, return it.
4. If there is a cache miss, perform retrieval.
5. Store the result in Redis.
6. Return the result.

Learn:

- Cache hit.
- Cache miss.
- Cache-aside pattern.
- TTL.
- Cache invalidation.
- Cache key design.

### Implementation C — Query Embedding Caching

Repeated queries do not necessarily need repeated embedding generation.

Cache embeddings for normalized queries.

Use a separate namespace for embedding cache keys.

### Implementation D — Cache Invalidation

When a course is added, updated or deleted:

- Invalidate affected cached results.
- Avoid serving stale course information.
- Consider versioned cache keys or targeted invalidation.

### Implementation E — Performance Benchmarking

Compare:

- Search without Redis.
- Search with Redis.
- Cache hit latency.
- Cache miss latency.

Measure actual latency rather than assuming caching always improves performance.

### Completion criteria

- [ ] Redis configured.
- [ ] Search result caching implemented.
- [ ] Cache-aside pattern working.
- [ ] TTL configured.
- [ ] Query embedding caching implemented.
- [ ] Cache invalidation handled.
- [ ] Latency comparison documented.

**Deliverable:** Redis-powered search system.

---

## STAGE 7 — Metadata Filtering and Personalized Recommendations

**Objective:** Make course discovery more useful.

Semantic similarity alone cannot satisfy every user requirement.

A user might find a course relevant but not want an advanced course lasting 50 hours.

### Filters

- Difficulty: Beginner / Intermediate / Advanced.
- Duration: Under 5 / 10 / 20 hours.
- Technology: Python / Node.js / React / Java.
- Category: Backend / Frontend / AI / Data Science.
- Provider.
- Language.
- Price, where available.

### Personalization

Allow users to specify:

- Current skill level.
- Preferred technologies.
- Learning goals.
- Available learning time.
- Preferred course duration.

Use these preferences to influence retrieval and ranking.

### Example

User profile:

- Beginner.
- Interested in backend development.
- Knows JavaScript.
- Has 5 hours per week.

The recommendation system should prioritize beginner-friendly backend courses with manageable durations.

### Similar Course Discovery

Add a feature:

"Find courses similar to this one."

Implementation:

1. Fetch the selected course embedding.
2. Search for nearest course vectors.
3. Exclude the original course.
4. Apply relevant filters.
5. Return similar courses.

### Completion criteria

- [ ] Difficulty filtering.
- [ ] Duration filtering.
- [ ] Technology filtering.
- [ ] User preference support.
- [ ] Similar course discovery.

**Deliverable:** Personalized course recommendation engine.

---

## STAGE 8 — Search Evaluation

**Objective:** Measure retrieval quality.

We need evidence that our hybrid search performs well.

### Create evaluation queries

Prepare 20–30 queries such as:

- Beginner Node.js backend development.
- Advanced React performance optimization.
- Python machine learning courses under 10 hours.
- Database design for backend developers.
- Docker and Kubernetes for beginners.

Manually label relevant courses for each query.

### Metrics

**1. Precision@K**

Relevant courses in top K / K

Measures how many returned results are relevant.

**2. Recall@K**

Relevant courses in top K / Total relevant courses

Measures how many relevant courses were retrieved.

**3. NDCG@K**

Measures how well relevant results are ordered, giving higher importance to relevant courses appearing near the top.

### Comparison

Compare:

- BM25 only.
- Vector search only.
- Hybrid search with RRF.

### Performance metrics

Also measure:

- Search latency.
- Redis cache hit rate.
- Cache hit vs miss latency.
- Embedding generation latency.

### Completion criteria

- [ ] Evaluation dataset prepared.
- [ ] Precision@K implemented.
- [ ] Recall@K implemented.
- [ ] NDCG@K implemented.
- [ ] Search strategies compared.
- [ ] Performance benchmark documented.

**Deliverable:** Search quality and performance evaluation report.

---

## STAGE 9 — FastAPI Backend

**Objective:** Expose the complete search engine through APIs.

### Required endpoints

POST /api/search

Accepts a natural-language query and returns ranked courses.

GET /api/courses/{id}

Returns detailed information about a course.

GET /api/courses/{id}/similar

Returns similar courses.

GET /api/health

Checks backend and dependency health.

### Example request

{
  "query": "Beginner backend development using Node.js",
  "difficulty": "Beginner",
  "max_duration": 20,
  "top_k": 10
}

### Example response

{
  "query": "Beginner backend development using Node.js",
  "results": [
    {
      "course_id": "course_001",
      "title": "Node.js Backend Development",
      "difficulty": "Beginner",
      "duration_hours": 12,
      "score": 0.94,
      "matched_skills": ["Node.js", "Express"]
    }
  ],
  "cache_status": "HIT"
}

The cache status is useful for demonstrating Redis integration during testing.

### Completion criteria

- [ ] FastAPI application.
- [ ] Search API.
- [ ] Course details API.
- [ ] Similar course API.
- [ ] Input validation.
- [ ] Error handling.
- [ ] Redis integration.
- [ ] API documentation.

**Deliverable:** Working backend service.

---

## STAGE 10 — React Frontend and Deployment

**Objective:** Turn the engine into a usable product.

### Frontend features

- Natural-language search bar.
- Difficulty filters.
- Duration filters.
- Technology filters.
- Course result cards.
- Course details page.
- Similar courses section.
- Search loading and error states.

### UI example

Search:

"Courses to learn backend development using Node.js for beginners."

Filters:

Difficulty: Beginner

Duration: Under 20 hours

Results:

1. Node.js Backend Development.
2. Express.js and REST APIs.
3. Building Production-Ready APIs.

### Deployment

Use Docker Compose to run:

- React frontend.
- FastAPI backend.
- PostgreSQL with pgvector.
- Redis.

Add environment variables, health checks and a reproducible setup.

### Completion criteria

- [ ] React application.
- [ ] API integration.
- [ ] Search results displayed.
- [ ] Filters working.
- [ ] Similar courses displayed.
- [ ] Docker configuration.
- [ ] Deployment.
- [ ] GitHub README.

**Deliverable:** Complete CourseFinder MVP.

---

# 5. Final Architecture

The final architecture will look like this:

React Frontend

↓

FastAPI Application

↓

Query Processing

↓

Redis Cache

↙ Cache Hit       ↘ Cache Miss

Return Results     Generate Query Embedding

                   ↓

              BM25 Retrieval

                   +

              Vector Retrieval

                   ↓

              RRF Ranking

                   ↓

         Metadata Filtering

                   ↓

          PostgreSQL + pgvector

                   ↓

             Cache Results

                   ↓

             Return Results

Additional Redis use:

- Query embedding cache.
- Search result cache.
- Cache invalidation.
- Optional rate limiting.

Optional future extension:

Use Redis Streams or a task queue for asynchronous course ingestion and embedding generation. This is not necessary for the initial MVP.

---

# 6. One-Day MVP Prioritization

The complete roadmap is larger than a one-day project. We will implement the core functionality first and expand later.

| Priority | Feature |
|---|---|
| P0 | Course dataset |
| P0 | BM25 search |
| P0 | Sentence Transformer embeddings |
| P0 | Semantic retrieval |
| P0 | Hybrid search using RRF |
| P0 | Basic metadata filters |
| P0 | FastAPI search endpoint |
| P1 | Redis search result caching |
| P1 | Redis TTL and cache hit/miss |
| P1 | Basic React interface |
| P2 | Similar course discovery |
| P2 | Personalized recommendations |
| P2 | Search evaluation dashboard |
| P2 | Advanced caching and background workers |

**Important:** P0 is the first working technical milestone. Redis is a priority addition, but we should integrate it after the basic retrieval pipeline works.

---

# 7. How We Will Learn and Implement

We will use the following learning process for every stage.

### Step 1: Understand the concept

Understand the problem and underlying algorithm.

### Step 2: Work through a small example

For example, manually understand how cosine similarity works before using Sentence Transformers.

### Step 3: Implement independently

Write the code with guidance rather than blindly copying a complete implementation.

### Step 4: Dry run

Trace inputs, intermediate values and outputs.

### Step 5: Test

Test edge cases, invalid inputs and unexpected results.

### Step 6: Interview preparation

Understand:
- Why this technology?
- How does it work internally?
- What are its alternatives?
- What are its limitations?
- What is its time and space complexity?

Only after understanding a stage should we proceed.

---

# 8. Interview Preparation Checklist

By the end, I should be able to explain:

### Information Retrieval
- Keyword search vs semantic search.
- BM25.
- TF-IDF.
- Embeddings.
- Cosine similarity.
- Vector databases.

### Retrieval Engineering
- Hybrid search.
- Reciprocal Rank Fusion.
- Nearest-neighbour search.
- HNSW indexing.
- Metadata filtering.
- Reranking.

### Recommendation Systems
- Relevance scoring.
- Similarity-based recommendations.
- User preferences.
- Personalization.

### Redis
- In-memory data stores.
- Cache-aside pattern.
- Cache hit and miss.
- TTL.
- Cache invalidation.
- Cache key design.
- Redis vs PostgreSQL.
- When caching is beneficial and when it isn't.

### Evaluation
- Precision@K.
- Recall@K.
- NDCG@K.
- Latency measurement.
- Cache hit rate.

### Backend
- FastAPI.
- PostgreSQL.
- pgvector.
- REST APIs.
- Docker.
- Background processing.

---

# 9. Definition of Done

CourseFinder is complete when:

- Users can search using natural language.
- The engine retrieves semantically relevant courses.
- BM25 and vector search work independently.
- Hybrid ranking combines both retrieval methods.
- Users can filter courses.
- Similar course discovery works.
- Redis caches repeated search requests.
- Cache hits and misses are measurable.
- Search quality is evaluated quantitatively.
- FastAPI exposes the functionality.
- React provides a working interface.
- The application can be run using Docker Compose.

**Final principle:**

We are not building another course listing website.

We are building an intelligent information retrieval and recommendation system, with Redis-powered caching and measurable search quality.

The goal is to understand every component deeply enough to explain, modify and defend the architecture in a technical interview.

**Build incrementally. Understand everything. Ship a working MVP first.**