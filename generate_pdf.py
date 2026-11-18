import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 755, "CourseFinder — Technical Interview Master Guide")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
            
        # Footer (all pages)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 35, page_str)
        self.drawString(54, 35, "Confidential — Prepared for Technical Engineering Interviews")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 47, 558, 47)
        self.restoreState()

def build_pdf(filename="CourseFinder_Interview_Master_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569'),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )

    q_style = ParagraphStyle(
        'Question_Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1d4ed8'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    ans_style = ParagraphStyle(
        'Answer_Style',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    code_style = ParagraphStyle(
        'Code_Style',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("CourseFinder", title_style))
    story.append(Paragraph("Intelligent Course Discovery & Recommendation Engine — Technical Interview Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceBefore=2, spaceAfter=12))

    # Resume Points Section
    story.append(Paragraph("1. Resume Ready Points (Simple & Spoken Versions)", h1_style))
    story.append(Paragraph("<b>Resume Points (What to put on paper):</b>", h2_style))
    story.append(Paragraph("• <b>Engineered a Hybrid Search Engine:</b> Combined keyword search (BM25 Okapi) and semantic vector search (SentenceTransformers all-MiniLM-L6-v2, 384-dim) using Reciprocal Rank Fusion (RRF, k=60), achieving <b>0.892 Precision@10</b> and <b>0.898 NDCG@10</b> across 25 benchmark queries.", bullet_style))
    story.append(Paragraph("• <b>Built Two-Tier Redis Caching:</b> Architected a cache-aside system storing query vector embeddings and full result JSON payloads with SHA-256 deterministic keys, cutting response latency from <b>5.87 ms to 1.40 ms (4.2x speedup)</b>.", bullet_style))
    story.append(Paragraph("• <b>Full-Stack Web Platform:</b> Developed FastAPI backend and React frontend with natural language intent extraction (auto-parsing difficulty, duration, and price intent) and multi-factor personalized course recommendations.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Spoken Script (How to say them simply out loud):</b>", h2_style))
    story.append(Paragraph("<i>\"I built CourseFinder to solve the limits of regular keyword search. I combined exact keyword matching with AI semantic search so users find what they mean, not just what they type. To make it production-ready, I added Redis caching for a 4.2x speed boost and an automated evaluation suite proving 89% precision.\"</i>", callout_style))
    story.append(Spacer(1, 10))

    # Benchmark Metrics Table
    story.append(Paragraph("2. Official Benchmark Metrics (Verified Live Run)", h1_style))
    
    table_data = [
        [Paragraph("<b>Strategy</b>", body_style), Paragraph("<b>Precision@10</b>", body_style), Paragraph("<b>Recall@10</b>", body_style), Paragraph("<b>NDCG@10</b>", body_style), Paragraph("<b>MRR</b>", body_style), Paragraph("<b>Avg Latency</b>", body_style)],
        ["BM25 (Okapi Lexical)", "0.8600", "0.4427", "0.8748", "0.9600", "0.19 ms"],
        ["Vector (all-MiniLM-L6-v2)", "0.8920", "0.4505", "0.9099", "1.0000", "7.94 ms"],
        ["Hybrid RRF (Combined)", "0.8920", "0.4549", "0.8984", "0.9600", "6.59 ms"],
        ["Redis Cache Hit", "—", "—", "—", "—", "1.40 ms (4.2x faster)"]
    ]
    t = Table(table_data, colWidths=[130, 75, 70, 75, 65, 89])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#eff6ff')),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#ecfdf5')),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # End-to-End Workflow Section
    story.append(Paragraph("3. End-to-End Search Lifecycle (User Query ➔ Screen)", h1_style))
    story.append(Paragraph("When a user types <b>'free beginner machine learning under 10 hours'</b>, the following 9 steps execute:", body_style))

    steps = [
        ("Step 1: Frontend Dispatch", "React captures the query string, user filter states, and search mode ('hybrid'). It sends an HTTP POST request to /api/search."),
        ("Step 2: FastAPI Controller", "Backend receives SearchRequest. It starts a high-resolution timer (t_start = time.perf_counter()) to benchmark latency."),
        ("Step 3: Natural Language Intent Parsing", "QueryIntentParser analyzes the text with regex rules: extracts difficulty='Beginner', max_duration=10h, free_only=True, category='AI & Machine Learning'."),
        ("Step 4: Tier-1 Redis Cache Check", "Generates a deterministic SHA-256 hash of the query and all filter parameters. If found in Redis, deserializes JSON and returns in ~1.4 ms (Cache Hit)."),
        ("Step 5: Dual Retrieval Phase (Cache Miss)", "<b>Branch A (BM25):</b> Computes term frequencies, applies length normalization and metadata filters, returning top 30 candidates.<br/><b>Branch B (Vector):</b> Checks query embedding cache (Tier-2). If absent, encodes with all-MiniLM-L6-v2, runs dot product cosine similarity, and discards candidates with similarity < 0.25 (noise filter)."),
        ("Step 6: Relevance Guardrail Check", "If BM25 returns 0 matches AND top vector similarity is < 0.28 (e.g. user searched 'maid' or random words), the system rejects the query and returns 0 results."),
        ("Step 7: Reciprocal Rank Fusion (RRF, k=60)", "RRF score = 1/(60 + Rank_BM25) + 1/(60 + Rank_Vector). Candidates are sorted by fused score. Relevance percentage is calibrated: dual-source agreement scores 75-98%; single-source scores scale with true cosine similarity."),
        ("Step 8: Redis Cache Population", "Writes ranked results to Redis with a 10-minute TTL. Appends total execution time in milliseconds."),
        ("Step 9: React UI Rendering", "CourseCard components display relevance gauge (e.g. '98% Match'), matched skills highlighted in blue, and retrieval provenance ('BM25 Rank 1 + Semantic Rank 2').")
    ]

    for title, desc in steps:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", bullet_style))

    story.append(PageBreak())

    # Part 4: Top 12 Interview Q&A
    story.append(Paragraph("4. Technical Interview Questions & Answers", h1_style))

    qa_list = [
        ("Q1: Why did you use Hybrid Search instead of pure Semantic Vector Search?",
         "Dense vector search understands meaning (e.g. 'server-side' = 'backend'), but has known weaknesses: it struggles with exact technical terms, library acronyms (e.g. 'JWT', 'FastAPI'), and can suffer from semantic drift (e.g. searching 'FastAPI' returns Django/Flask courses because their vector embeddings are neighbors). BM25 anchors exact technical keywords, while Vector search handles conceptual understanding. Hybrid RRF combines both."),

        ("Q2: What is Reciprocal Rank Fusion (RRF) and why use it over Linear Weighted Sum?",
         "Linear combination (w1*BM25 + w2*Vector) requires score normalization. But BM25 scores are unbounded (0 to 30+), while cosine similarities are bounded between -1.0 and 1.0. Normalizing them is fragile and breaks when score distributions shift. RRF bypasses raw scores completely and operates purely on rank positions: RRF = 1/(60 + Rank_BM25) + 1/(60 + Rank_Vector). It gives balanced, robust rankings without hyperparameter tuning."),

        ("Q3: How does BM25 Okapi work and what do k1 and b control?",
         "BM25 improves on TF-IDF through two parameters: k1 (set to 1.5) controls term frequency saturation. Unlike TF-IDF where 10 mentions score 10x higher than 1 mention, BM25 uses an asymptote where repeated terms give diminishing returns. Parameter b (set to 0.75) controls document length normalization, preventing long descriptions from unfairly winning over concise titles."),

        ("Q4: How did you fix the bug where unrelated queries like 'maid' returned courses?",
         "Unconstrained k-NN vector search always computes cosine similarity across all vectors and returns the top k closest items, even if the top similarity is only 0.19 (pure noise). I solved this with two guardrails: (1) Added a min_similarity cutoff of 0.25 in vector search; (2) In hybrid search, if BM25 returns 0 matches AND top vector similarity is below 0.28, the system marks the query as out-of-domain and returns 0 results."),

        ("Q5: Explain your Two-Tier Redis Cache-Aside system.",
         "Generating query embeddings with SentenceTransformers takes 7-8 ms on CPU. I created Tier 1 (Search Result Cache), which stores the full serialized course list keyed by SHA-256(query + filters) with a 600s TTL. I created Tier 2 (Query Embedding Cache), which stores the raw 384-float array keyed by query string. On cache hit, latency drops from 5.87 ms to 1.40 ms (4.2x speedup)."),

        ("Q6: How do you prevent cache poisoning when users apply different filters?",
         "The cache key is not just the query text. It is a deterministic SHA-256 hash of a JSON payload containing query, difficulty, max_duration, free_only, provider, and search mode. For example, {'q': 'python', 'diff': 'Beginner'} and {'q': 'python', 'diff': 'Advanced'} generate distinct hash keys, ensuring isolated cache entries."),

        ("Q7: What Information Retrieval (IR) metrics did you use to evaluate search quality?",
         "I built a benchmark running 25 ground-truth test queries evaluating: Precision@10 (0.892: 89.2% of top 10 results are relevant), Recall@10 (0.455: proportion of all relevant catalog items captured), NDCG@10 (0.898: ranking quality discounted by position), and MRR (0.960: Mean Reciprocal Rank, proving the first relevant course appears almost always at Rank 1)."),

        ("Q8: What is the mathematical difference between DCG and NDCG?",
         "DCG (Discounted Cumulative Gain) sums relevance scores divided by log2(rank + 1) to penalize relevant items appearing lower in the list: DCG = sum(rel_i / log2(i+1)). Because DCG is unbounded and varies by query size, NDCG divides DCG by IDCG (Ideal DCG — the DCG of a perfectly sorted list). This normalizes the metric between 0.0 and 1.0 for fair comparison across all queries."),

        ("Q9: How does the personalized recommendation algorithm work?",
         "It uses a content-based multi-factor scoring model: 40% weight to Technology Match (Jaccard skill overlap), 30% weight to Semantic Goal Alignment (cosine similarity between user career statement and course embedding), 20% weight to Experience Tier match (Beginner/Intermediate/Advanced), and 10% weight to Weekly Study Feasibility."),

        ("Q10: How would you scale this system from 362 courses to 10 Million courses?",
         "At 10M courses, in-memory numpy is replaced with PostgreSQL + pgvector utilizing an HNSW index (Hierarchical Navigable Small World) for sub-10ms approximate nearest neighbors. BM25 is offloaded to a distributed Elasticsearch/OpenSearch cluster. SentenceTransformer inference is moved to a dedicated GPU microservice (e.g. Triton Inference Server) behind a Redis/Kafka task queue. Retrieval uses a two-stage pipeline: fast candidate retrieval (top 100) followed by a Cross-Encoder reranker."),

        ("Q11: Why FastAPI over Flask or Django?",
         "FastAPI provides native asynchronous I/O (async/await) which is crucial for non-blocking concurrent calls to Redis and PostgreSQL. It also provides automatic schema validation with Pydantic v2 (compiled in Rust/C), automatic OpenAPI/Swagger documentation, and high throughput on Uvicorn."),

        ("Q12: How does the project handle cold start and environment fallbacks gracefully?",
         "The backend uses an automatic fallback architecture: if PostgreSQL + pgvector is running in Docker, it connects to Postgres. If Postgres is absent, it seamlessly falls back to a local SQLite database and precomputed .npy vector embeddings. If Redis is down, it falls back to an in-memory LRU cache so the application never crashes.")
    ]

    for q, a in qa_list:
        story.append(Paragraph(q, q_style))
        story.append(Paragraph(a, ans_style))
        story.append(Spacer(1, 3))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {filename}")

if __name__ == "__main__":
    build_pdf()
