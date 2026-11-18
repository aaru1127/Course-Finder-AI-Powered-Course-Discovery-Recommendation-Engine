import re
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
            self.drawString(54, 755, "CourseFinder — Deep Technical Interview & Engineering Guide")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
            
        # Footer (all pages)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 35, page_str)
        self.drawString(54, 35, "CourseFinder Architecture & Algorithmic Foundations")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 47, 558, 47)
        self.restoreState()

def build_pdf(filename="CourseFinder_Deep_Technical_Interview_Guide.pdf"):
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
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14.5,
        textColor=colors.HexColor('#1d4ed8'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'H3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    formula_style = ParagraphStyle(
        'Formula',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0f172a'),
        leftIndent=20,
        spaceBefore=4,
        spaceAfter=5
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a'),
        leftIndent=15,
        spaceBefore=4,
        spaceAfter=4
    )

    story = []

    # Title Banner
    story.append(Paragraph("CourseFinder — Deep Technical Interview Guide", title_style))
    story.append(Paragraph("Engineering Principles, Algorithmic Formulas, Trade-offs & System Design Rationale", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("This document provides a comprehensive technical breakdown of every architectural, algorithmic, and engineering decision in CourseFinder. It equips you to answer complex technical questions regarding Information Retrieval, vector similarity math, caching, database indexing, and quantitative evaluation.", body_style))
    story.append(Spacer(1, 6))

    # SECTION 1
    story.append(Paragraph("1. Information Retrieval Fundamentals", h1_style))
    
    story.append(Paragraph("Q1: What is the fundamental difference between Keyword Search and Semantic Search?", h2_style))
    story.append(Paragraph("• <b>Keyword Search (Lexical Retrieval):</b> Operates on exact character and token matches using inverted indexes and term statistics (e.g., BM25).<br/>"
                           "<i>Strengths:</i> High precision for exact terminology, library names, error codes, and versions ('Python 3.12', 'Kubernetes 1.28', 'FastAPI').<br/>"
                           "<i>Weaknesses:</i> Suffers from the <b>vocabulary mismatch problem</b> (synonyms and paraphrasing). If a user queries 'build server-side applications with JavaScript', keyword search misses courses titled 'Node.js Backend Development' if those literal terms are not present.", bullet_style))
    story.append(Paragraph("• <b>Semantic Search (Dense Vector Retrieval):</b> Projects queries and documents into a shared continuous embedding space where geometric proximity reflects semantic meaning.<br/>"
                           "<i>Strengths:</i> Understands conceptual intent and synonyms without needing word-for-word overlap.<br/>"
                           "<i>Weaknesses:</i> Vulnerable to <b>semantic drift</b> or loss of fine-grained technical specificity (e.g. treating 'React 17' and 'React 18' as nearly identical in vector space).", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Q2: How does the BM25 Okapi algorithm work, and why does it outperform TF-IDF?", h2_style))
    story.append(Paragraph("BM25 (Best Matching 25) calculates relevance score as:", body_style))
    story.append(Paragraph("Score(D, Q) = &Sigma; [ IDF(q_i) &times; ( f(q_i, D) &times; (k_1 + 1) ) / ( f(q_i, D) + k_1 &times; (1 - b + b &times; |D| / avgdl) ) ]", formula_style))
    story.append(Paragraph("Where:<br/>"
                           "• <b>f(q_i, D):</b> Term frequency of term q_i in document D.<br/>"
                           "• <b>|D| and avgdl:</b> Document length and average corpus document length.<br/>"
                           "• <b>k_1 = 1.5:</b> Controls <b>term frequency saturation</b>.<br/>"
                           "• <b>b = 0.75:</b> Controls <b>document length normalization</b>.<br/>"
                           "• <b>IDF(q_i) = ln( (N - n(q_i) + 0.5) / (n(q_i) + 0.5) + 1 ):</b> Robertson-Spärck Jones inverse document frequency formula.", bullet_style))
    story.append(Paragraph("<b>Why BM25 outperforms standard TF-IDF:</b>", h3_style))
    story.append(Paragraph("1. <b>Term Frequency Saturation (k_1):</b> In standard TF-IDF, score increases linearly (or unbounded logarithmically) with term count. In BM25, as term frequency increases, its marginal contribution asymptotically approaches (k_1 + 1). A document mentioning 'Python' 50 times is not 10 times more relevant than one mentioning it 5 times; BM25 caps this effect, preventing keyword stuffing.", bullet_style))
    story.append(Paragraph("2. <b>Document Length Normalization (b):</b> Long documents naturally contain more words. At b=0.75, BM25 penalizes excessively verbose documents while still giving fair credit to comprehensive content.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Q3: What are dense vector embeddings and how does cosine similarity work?", h2_style))
    story.append(Paragraph("• <b>Dense Embeddings:</b> Text is passed through a transformer encoder (SentenceTransformers <code>all-MiniLM-L6-v2</code>). Mean pooling over attention tokens produces a 384-dimensional dense vector capturing semantic semantics.<br/>"
                           "• <b>Cosine Similarity:</b> Measures the cosine of the angle between query vector u and document vector v:<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;Cosine Similarity(u, v) = ( u &bull; v ) / ( ||u||_2 &times; ||v||_2 )", bullet_style))
    story.append(Paragraph("• <b>Optimization in CourseFinder:</b> All embeddings are pre-normalized with L2 normalization during indexing such that ||u||_2 = 1.0. This simplifies cosine similarity to a simple dot product: Cosine Similarity(u_norm, v_norm) = &Sigma; (u_i &times; v_i). This turns an expensive O(d) square-root operation into fast vector dot products mapped directly to SIMD CPU instructions (BLAS/Accelerate).", bullet_style))

    story.append(PageBreak())

    # SECTION 2
    story.append(Paragraph("2. Retrieval Engineering & Hybrid Search", h1_style))

    story.append(Paragraph("Q4: Why use Hybrid Search with Reciprocal Rank Fusion (RRF)?", h2_style))
    story.append(Paragraph("Pure vector search misses exact technical keywords, while lexical search fails on conceptual queries. Hybrid search merges both to maximize recall and precision.", body_style))
    story.append(Paragraph("<b>The Challenge of Score Normalization:</b> BM25 produces unbounded scores (e.g. 4.5, 18.2, 32.0), while cosine similarity is bounded in [-1.0, 1.0] (typically 0.3 to 0.95 for text). Merging them via a weighted linear sum requires fragile score normalization that breaks when corpus distributions shift.", body_style))
    story.append(Paragraph("<b>The RRF Solution:</b> Reciprocal Rank Fusion is a non-parametric, score-agnostic rank aggregation algorithm:", body_style))
    story.append(Paragraph("RRF_Score(d) = &Sigma; [ w_m / ( k + rank_m(d) ) ]", formula_style))
    story.append(Paragraph("• <b>rank_m(d):</b> 1-based rank position of course d in retrieval model m's result list.<br/>"
                           "• <b>k = 60:</b> Standard smoothing constant. It dampens the penalty for lower ranks while ensuring items appearing in the top of <b>both</b> lists receive high compound scores.<br/>"
                           "• <b>Max Theoretical RRF:</b> Occurs when a document is #1 in both lists: (1/61) + (1/61) &approx; 0.032786. CourseFinder scales this deterministically to 0–100% without fabricating numbers.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Q5: How does pgvector index vector embeddings? (HNSW vs IVFFlat)", h2_style))
    story.append(Paragraph("PostgreSQL's <code>pgvector</code> extension supports two Approximate Nearest Neighbor (ANN) index types:", body_style))
    story.append(Paragraph("1. <b>HNSW (Hierarchical Navigable Small World):</b> Builds a multi-layer graph where upper layers have long skip-links and bottom layers have dense local links. Query complexity is O(log N). Offers highest query throughput and recall (>98%).<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;<code>CREATE INDEX ON courses USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);</code><br/>"
                           "2. <b>IVFFlat (Inverted File Flat):</b> Clusters vector space into K Voronoi cells using k-means. Queries search only the nearest centroids (probes). Offers faster index build time and lower memory, but lower recall if probes is set too low.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Q6: Pre-filtering vs Post-filtering in Vector Retrieval", h2_style))
    story.append(Paragraph("• <b>Post-filtering:</b> First retrieve top K vector neighbors across the entire corpus, then discard records that do not match metadata filters (e.g., difficulty='Beginner'). <i>Risk:</i> If only 2% of courses match the filter, top K search might return 0 valid courses.<br/>"
                           "• <b>Pre-filtering (Supported by pgvector):</b> The database engine applies metadata predicates during index traversal (e.g. <code>WHERE difficulty = 'Beginner' ORDER BY embedding <=> query_vector LIMIT 10</code>), guaranteeing that all returned candidates satisfy the filter.", bullet_style))

    story.append(Spacer(1, 6))

    # SECTION 3
    story.append(Paragraph("3. Redis In-Memory Caching Architecture", h1_style))

    story.append(Paragraph("Q7: Explain the Cache-Aside Pattern implemented in CourseFinder.", h2_style))
    story.append(Paragraph("1. <b>Request Ingestion:</b> Client submits query Q and filter set F.<br/>"
                           "2. <b>Deterministic Key Generation:</b> Key = 'course_search:' + SHA256( normalized(Q) + canonical_json(F) ).<br/>"
                           "3. <b>Cache Lookup:</b> Query Redis via <code>GET Key</code>.<br/>"
                           "4. <b>Cache HIT:</b> If key exists, return deserialized JSON response in <b>~1.40 ms</b>.<br/>"
                           "5. <b>Cache MISS:</b><br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;• Check Tier-2 Query Embedding Cache (<code>query_emb:{hash}</code>). Reuse if present; otherwise encode query with SentenceTransformers.<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;• Execute dual retrieval (BM25 + pgvector).<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;• Fuse via RRF and apply metadata filters.<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;• Write result to Redis with TTL = 600s (10 min).<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;• Return response in <b>~5.87 ms</b> (4.2x latency difference).", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Q8: What are the trade-offs of caching, and when is it beneficial vs detrimental?", h2_style))
    story.append(Paragraph("• <b>Beneficial when:</b> Query traffic exhibits a Zipfian / Power-law distribution (top 10% of queries make up 70% of traffic); backend involves heavy computation (embedding generation); catalog changes infrequently.<br/>"
                           "• <b>Detrimental when:</b> Queries are high-cardinality and completely unique (cache hit rate near 0%, adding unnecessary Redis network overhead); data undergoes sub-second inventory/price updates.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Q9: How is Cache Invalidation handled?", h2_style))
    story.append(Paragraph("• <b>Time-To-Live (TTL):</b> Every cache key has a 600-second TTL to guarantee eventual consistency.<br/>"
                           "• <b>Explicit Purge on Write:</b> When courses are ingested or modified, CourseFinder provides a <code>POST /api/cache/clear</code> endpoint to flush all dependent search keys.", bullet_style))

    story.append(PageBreak())

    # SECTION 4
    story.append(Paragraph("4. Quantitative Search Evaluation", h1_style))

    story.append(Paragraph("Q10: How are Precision@K, Recall@K, NDCG@K, and MRR calculated?", h2_style))
    story.append(Paragraph("1. <b>Precision@K:</b> Fraction of returned courses in top K that are relevant: Precision@K = |Retrieved@K &cap; Relevant| / K. High precision ensures users are not shown irrelevant noise.<br/>"
                           "2. <b>Recall@K:</b> Fraction of all ground-truth relevant courses retrieved in top K: Recall@K = |Retrieved@K &cap; Relevant| / |Relevant|.<br/>"
                           "3. <b>NDCG@K (Normalized Discounted Cumulative Gain):</b> Evaluates ranking position quality by logarithmically discounting items appearing lower in the list:", bullet_style))
    story.append(Paragraph("DCG@K = &Sigma; [ (2^rel_i - 1) / log2(i + 1) ]&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;NDCG@K = DCG@K / IDCG@K", formula_style))
    story.append(Paragraph("Where IDCG is the Ideal DCG achieved by placing all relevant items in perfect order. NDCG is bounded between 0.0 and 1.0, enabling fair comparison across queries with differing numbers of relevant items.<br/>"
                           "4. <b>MRR (Mean Reciprocal Rank):</b> MRR = (1 / |Q|) &times; &Sigma; (1 / rank_q), where rank_q is the position of the <i>first</i> relevant course. If the first relevant course is at Rank 1, MRR is 1.0; if at Rank 2, 0.5.", bullet_style))

    story.append(Spacer(1, 6))

    # SECTION 5: Summary Matrix Table
    story.append(Paragraph("5. Architectural Summary Matrix for Technical Interviews", h1_style))
    
    matrix_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Implementation</b>", body_style), Paragraph("<b>Engineering Rationale</b>", body_style)],
        ["Lexical Engine", "BM25 Okapi with field weighting\n(k1=1.5, b=0.75)", "Prevents keyword saturation; guarantees exact token recall for versions and acronyms."],
        ["Semantic Engine", "all-MiniLM-L6-v2 (384-dim,\nL2 normalized)", "High semantic density, fast CPU inference (<15ms), low memory footprint."],
        ["Fusion Algorithm", "Reciprocal Rank Fusion (k=60)", "Non-parametric rank aggregation; eliminates complex score distribution calibration."],
        ["Database", "PostgreSQL + pgvector (HNSW) +\nSQLite fallback", "Single ACID-compliant store for course metadata and vector embeddings with zero-config fallback."],
        ["Caching Layer", "Redis Two-Tier Cache-Aside", "4.2x latency reduction (5.87ms -> 1.40ms) for repeated queries and embedding reuse."],
        ["API Framework", "FastAPI (ASGI + Pydantic v2)", "Asynchronous request handling, fast C-based data validation, automated OpenAPI docs."],
        ["Relevance Guardrail", "min_similarity = 0.25 +\nout-of-domain rejection", "Prevents unconstrained vector k-NN from returning unrelated courses for noise queries (e.g. 'maid')."],
        ["Evaluation Suite", "Automated Benchmark (25 queries)", "Quantitatively proves Hybrid Search achieves 0.892 Precision@10 and 0.898 NDCG@10."]
    ]
    
    table_matrix = Table(matrix_data, colWidths=[110, 160, 234])
    table_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(table_matrix)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    build_pdf()
