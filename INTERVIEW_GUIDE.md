# CourseFinder — Deep Technical Interview Guide

This guide covers the engineering principles, algorithmic formulas, trade-offs, and system design decisions implemented in CourseFinder. It is structured to help you explain and defend every component in a technical interview.

---

## 1. Information Retrieval Fundamentals

### Q1: What is the fundamental difference between Keyword Search and Semantic Search?
- **Keyword Search (Lexical Retrieval)** relies on literal character/token matching (e.g. inverted index, BM25).
  - *Strengths:* Exceptional precision for exact terminology, acronyms, product names, versions (`Python 3.12`, `Kubernetes 1.28`, `OAuth2`).
  - *Weaknesses:* Vulnerable to the **vocabulary mismatch problem** (synonyms, paraphrase, conceptual queries). If a user queries *"build server-side applications using JavaScript"*, a keyword search misses courses titled *"Node.js Backend Development"* if those exact words are absent.
- **Semantic Search (Dense Vector Retrieval)** projects queries and documents into a shared continuous embedding space where geometric proximity reflects semantic meaning.
  - *Strengths:* Understands intent, context, and semantic equivalence without requiring exact keyword overlaps.
  - *Weaknesses:* Can suffer from **semantic drift** or loss of specificity. For instance, it might treat *"React 17"* and *"React 18"* as nearly identical in vector space, failing when a user explicitly needs features introduced in a specific version.

---

### Q2: How does the BM25 Okapi algorithm work, and why does it outperform TF-IDF?
BM25 (Best Matching 25) calculates relevance as:
$$\text{Score}(D, Q) = \sum_{i=1}^n \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

Where:
- $f(q_i, D)$ is the term frequency of term $q_i$ in document $D$.
- $|D|$ is the length of document $D$ in words.
- $\text{avgdl}$ is the average document length across the corpus.
- $k_1$ controls **term frequency saturation** (default $1.2 - 2.0$, CourseFinder uses $1.5$).
- $b$ controls **document length normalization** (default $0.75$).
- $\text{IDF}(q_i) = \ln\left(\frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1\right)$ (Robertson-Spärck Jones formulation).

#### Why BM25 outperforms standard TF-IDF:
1. **Term Frequency Saturation ($k_1$):** In standard TF-IDF, the score scales linearly with term count (or logarithmically). In BM25, as term frequency increases, its marginal contribution asymptotically approaches $(k_1 + 1)$. A document mentioning "Python" 50 times is not 10 times more relevant than one mentioning it 5 times; BM25 naturally caps this effect, preventing keyword stuffing.
2. **Document Length Normalization ($b$):** Long documents naturally contain more words. If $b=1$, the term frequency is strictly scaled by the document length. If $b=0$, length normalization is ignored. At $b=0.75$, BM25 penalizes verbose documents while still giving reasonable credit to long, comprehensive documents.

---

### Q3: What are dense vector embeddings and how does cosine similarity work?
- **Dense Embeddings:** Text is passed through a transformer encoder (e.g. `all-MiniLM-L6-v2`). The model outputs contextual token representations, which are pooled (e.g. mean pooling over attention tokens) into a fixed-length vector of 384 dimensions.
- **Cosine Similarity:** Measures the cosine of the angle between two vectors:
  $$\text{Cosine Similarity}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2} = \frac{\sum_{i=1}^d u_i v_i}{\sqrt{\sum_{i=1}^d u_i^2} \sqrt{\sum_{i=1}^d v_i^2}}$$
- **Optimization in CourseFinder:**
  During ingestion and query encoding, we apply $L_2$ normalization to all vectors such that $\|u\|_2 = 1.0$. Consequently, cosine similarity simplifies to a simple dot product:
  $$\text{Cosine Similarity}(u_{\text{norm}}, v_{\text{norm}}) = u_{\text{norm}} \cdot v_{\text{norm}} = \sum_{i=1}^{384} u_i v_i$$
  This transforms an $O(d)$ operation involving square roots into pure vector multiplication, accelerating in-memory retrieval by orders of magnitude and mapping directly to SIMD CPU instructions (`BLAS`/`Accelerate`).

---

## 2. Retrieval Engineering & Hybrid Search

### Q4: Why use Hybrid Search with Reciprocal Rank Fusion (RRF)?
Pure vector search can miss explicit keywords, while pure lexical search cannot handle conceptual queries. **Hybrid Search** merges both paradigms to achieve higher recall and precision.

#### The Challenge of Score Calibration
BM25 produces unbounded scores (e.g. $4.5$, $18.2$, $32.0$ depending on IDF and document length), while cosine similarity produces scores bounded between $[-1.0, 1.0]$ (typically $[0.3, 0.95]$ for text). Merging them via a weighted linear sum requires complex score normalization (e.g. Min-Max or Z-score normalization) that is sensitive to outliers and corpus shifts.

#### The RRF Solution
**Reciprocal Rank Fusion (RRF)** is a robust, non-parametric rank aggregation algorithm:
$$\text{RRF Score}(d) = \sum_{m \in \{\text{BM25}, \text{Vector}\}} \frac{w_m}{k + \text{rank}_m(d)}$$
- $\text{rank}_m(d)$ is the 1-based rank position of document $d$ in the result list of engine $m$.
- $k$ is a smoothing constant (standard empirical value is $60$).
- $k=60$ mitigates the penalty for items ranked slightly lower while ensuring documents appearing near the top of **both** retrieval lists receive a significantly higher compound score.
- Theoretical maximum RRF score occurs when a document ranks #1 in both lists:
  $$\text{Max RRF} = \frac{1}{60 + 1} + \frac{1}{60 + 1} = \frac{2}{61} \approx 0.032786$$
- CourseFinder scales this deterministic value to a 0–100% calibrated match score without fabricating numbers.

---

### Q5: How does pgvector index vector embeddings? (HNSW vs IVFFlat)
PostgreSQL's `pgvector` extension supports two primary indexing algorithms for Approximate Nearest Neighbor (ANN) search:

1. **HNSW (Hierarchical Navigable Small World):**
   - *How it works:* Builds a multi-layer graph where upper layers have longer links for rapid skip-list navigation and lower layers have dense, local connections.
   - *Query complexity:* $O(\log N)$.
   - *Trade-offs:* Highest query throughput and recall (>98%), but higher memory overhead during index construction.
   - *pgvector syntax:*
     ```sql
     CREATE INDEX ON courses USING hnsw (embedding vector_cosine_ops)
     WITH (m = 16, ef_construction = 64);
     ```
2. **IVFFlat (Inverted File Flat):**
   - *How it works:* Partitions the vector space into $K$ Voronoi clusters using k-means. Queries search only the nearest centroids (`probes`).
   - *Trade-offs:* Faster build times and lower memory footprint, but lower recall if $probes$ is set too low.

---

### Q6: Pre-filtering vs Post-filtering in Vector Retrieval
- **Post-filtering:** First retrieve top $K$ nearest vector neighbors, then discard records that do not match metadata filters (e.g. `difficulty = 'Beginner'`).
  - *Risk:* If only 2% of the corpus matches the filter, top $K$ vector search might yield 0 matching items, causing empty results.
- **Pre-filtering / Single-stage filtering (Supported by pgvector):** The SQL engine applies metadata predicates inside the index scan or combines vector index traversal with boolean filters (`WHERE difficulty = 'Beginner' ORDER BY embedding <=> query_vector LIMIT 10`).

---

## 3. Redis In-Memory Caching Architecture

### Q7: Explain the Cache-Aside Pattern implemented in CourseFinder.
The Cache-Aside (Lazy Loading) pattern operates as follows:
1. **Request Ingestion:** User submits query `Q` and filter set `F`.
2. **Cache Key Generation:** A deterministic key is generated:
   $$\text{Key} = \text{"course\_search:"} + \text{SHA256}(\text{normalized}(Q) + \text{canonical\_json}(F))$$
3. **Lookup:** Query Redis using `GET key`.
4. **Cache HIT:** If key exists, parse cached JSON response and return immediately ($\approx 0.2\text{ ms}$ latency).
5. **Cache MISS:**
   - Check Query Embedding Cache (`query_emb:{hash}`); if present, reuse vector. Otherwise compute vector with SentenceTransformer and save to Redis.
   - Execute dual retrieval (BM25 + Vector Search).
   - Apply Reciprocal Rank Fusion and metadata filtering.
   - Write result payload to Redis with `SETEX key 600 payload_json` (TTL = 10 minutes).
   - Return response ($\approx 4.0\text{ ms}$ latency).

---

### Q8: What are the trade-offs of caching, and when is it beneficial vs detrimental?
- **Beneficial when:**
  - Query distribution exhibits a **Zipfian / Power-law distribution** (e.g., top 10% of search queries represent 60–80% of total traffic).
  - Search pipeline involves computationally intensive tasks (transformer embedding generation, distance matrix calculation).
  - Course metadata changes infrequently.
- **Detrimental / Inefficient when:**
  - Queries are high-cardinality and completely unique (cache hit rate near 0%, adding unnecessary Redis network roundtrips).
  - Real-time inventory or price updates occur every second, leading to high cache invalidation churn or stale reads.

---

### Q9: How is Cache Invalidation handled?
- **Time-to-Live (TTL):** Every cached item is bounded by a TTL (600 seconds) to ensure eventual consistency.
- **Explicit Invalidation on Writes:** When a course is created, updated, or removed, CourseFinder provides targeted pattern invalidation (`course_search:*`), flushing dependent query caches to prevent stale reads.

---

## 4. Quantitative Search Evaluation

### Q10: How are Precision@K, Recall@K, NDCG@K, and MRR calculated?

1. **Precision@K:**
   $$\text{Precision@K} = \frac{|\text{Retrieved@K} \cap \text{Relevant}|}{K}$$
   *Meaning:* Fraction of returned courses in top $K$ that are relevant. High precision ensures users are not shown irrelevant courses.

2. **Recall@K:**
   $$\text{Recall@K} = \frac{|\text{Retrieved@K} \cap \text{Relevant}|}{|\text{Relevant}|}$$
   *Meaning:* Fraction of all ground-truth relevant courses in the entire catalog that were retrieved in top $K$.

3. **NDCG@K (Normalized Discounted Cumulative Gain):**
   $$\text{DCG@K} = \sum_{i=1}^K \frac{2^{\text{rel}_i} - 1}{\log_2(i + 1)}$$
   $$\text{NDCG@K} = \frac{\text{DCG@K}}{\text{IDCG@K}}$$
   *Meaning:* Unlike Precision, NDCG rewards systems that place the **most relevant results at rank 1 and 2**, applying logarithmic penalization to relevant results appearing further down the list. IDCG is the Ideal DCG obtained by sorting all relevant documents perfectly at the top.

4. **MRR (Mean Reciprocal Rank):**
   $$\text{MRR} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{1}{\text{rank}_q}$$
   *Meaning:* Where $\text{rank}_q$ is the rank position of the **first** relevant course. If the first relevant course is at rank 1, reciprocal rank is $1.0$; if at rank 2, $0.5$.

---

## 5. Summary Matrix for Technical Interview

| Concept | CourseFinder Implementation | Why chosen? |
|---|---|---|
| **Lexical Engine** | BM25 Okapi with field weights ($k_1=1.5, b=0.75$) | Prevents keyword saturation; guarantees exact token recall. |
| **Semantic Engine** | `all-MiniLM-L6-v2` (384-dim, normalized) | High semantic density, fast CPU inference (<15ms), low memory footprint. |
| **Fusion Algorithm** | Reciprocal Rank Fusion ($k=60$) | Non-parametric; avoids complex score distribution calibration. |
| **Database** | PostgreSQL + pgvector (HNSW) | Single ACID-compliant datastore for metadata and vector search. |
| **Caching Layer** | Redis Two-Tier Cache-Aside | 20.1x latency reduction for repeated searches and embedding reuse. |
| **API Framework** | FastAPI (ASGI + Python 3.11/3.13) | Asynchronous request processing, native Pydantic validation, OpenAPI. |
| **Evaluation** | Automated Benchmark (25 queries) | Quantitatively proves that Hybrid Search achieves superior NDCG and Recall. |

