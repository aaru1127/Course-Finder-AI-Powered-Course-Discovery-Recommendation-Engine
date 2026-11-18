import math
import re
from typing import List, Dict, Any, Optional, Tuple

class BM25Index:
    """
    BM25 Okapi lexical retrieval engine with multi-field term weighting.
    Implements standard information retrieval formula:
    Score(D, Q) = sum( IDF(q) * (f(q, D) * (k1 + 1)) / (f(q, D) + k1 * (1 - b + b * (|D| / avgdl))) )
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lens: List[int] = []
        self.doc_ids: List[str] = []
        self.courses_by_id: Dict[str, Dict[str, Any]] = {}
        
        # Inverted index: term -> list of (doc_index, term_frequency)
        self.inverted_index: Dict[str, List[Tuple[int, float]]] = {}
        self.df: Dict[str, int] = {}  # Document frequency for each term
        self.idf: Dict[str, float] = {}

    @staticmethod
    def tokenize(text: str) -> List[str]:
        if not text:
            return []
        # Lowercase and split on non-alphanumeric characters, keeping standard keywords like node.js, c++, vue.js
        text = text.lower()
        # Clean specific technical terms
        text = text.replace("node.js", "nodejs").replace("vue.js", "vuejs").replace("c++", "cpp")
        tokens = re.findall(r'\b[a-z0-9_-]+\b', text)
        return tokens

    def index_courses(self, courses: List[Dict[str, Any]]):
        """Index a list of course dictionaries."""
        self.corpus_size = len(courses)
        self.doc_ids = []
        self.doc_lens = []
        self.courses_by_id = {c["id"]: c for c in courses}
        self.inverted_index = {}
        self.df = {}
        self.idf = {}

        total_length = 0

        for idx, course in enumerate(courses):
            self.doc_ids.append(course["id"])

            # Weighted field representation:
            # Title gets 3x occurrence, skills get 2.5x occurrence, description 1x
            title_tokens = self.tokenize(course.get("title", ""))
            skills_tokens = []
            for skill in course.get("skills", []):
                skills_tokens.extend(self.tokenize(skill))
            desc_tokens = self.tokenize(course.get("description", ""))
            category_tokens = self.tokenize(course.get("category", ""))

            # Build term frequency for document
            tf: Dict[str, float] = {}
            for t in desc_tokens + category_tokens:
                tf[t] = tf.get(t, 0.0) + 1.0
            for t in title_tokens:
                tf[t] = tf.get(t, 0.0) + 3.0
            for t in skills_tokens:
                tf[t] = tf.get(t, 0.0) + 2.5

            doc_len = len(desc_tokens) + len(category_tokens) + (len(title_tokens) * 3) + int(len(skills_tokens) * 2.5)
            self.doc_lens.append(doc_len)
            total_length += doc_len

            # Update inverted index and document frequencies
            for term, count in tf.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                    self.df[term] = 0
                self.inverted_index[term].append((idx, count))
                self.df[term] += 1

        self.avg_doc_len = total_length / self.corpus_size if self.corpus_size > 0 else 0.0

        # Compute Robertson-Spärck Jones IDF for all vocabulary terms
        # IDF(q) = ln((N - n(q) + 0.5) / (n(q) + 0.5) + 1)
        for term, freq in self.df.items():
            self.idf[term] = math.log(((self.corpus_size - freq + 0.5) / (freq + 0.5)) + 1.0)

    def search(
        self,
        query: str,
        top_k: int = 10,
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
        max_duration: Optional[float] = None,
        min_duration: Optional[float] = None,
        provider: Optional[str] = None,
        free_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Execute BM25 scoring for the given query with optional metadata filtering.
        Returns ranked list of courses with scores and matched tokens.
        """
        query_tokens = self.tokenize(query)
        if not query_tokens or self.corpus_size == 0:
            return []

        # Accumulate BM25 scores for matching documents
        scores: Dict[int, float] = {}
        matched_tokens_by_doc: Dict[int, set] = {}

        for token in query_tokens:
            if token not in self.inverted_index:
                continue

            term_idf = self.idf[token]
            for doc_idx, tf in self.inverted_index[token]:
                doc_len = self.doc_lens[doc_idx]
                
                # BM25 numerator and denominator
                # numerator = tf * (k1 + 1)
                # denominator = tf + k1 * (1 - b + b * (doc_len / avg_doc_len))
                num = tf * (self.k1 + 1.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                term_score = term_idf * (num / denom)

                scores[doc_idx] = scores.get(doc_idx, 0.0) + term_score
                if doc_idx not in matched_tokens_by_doc:
                    matched_tokens_by_doc[doc_idx] = set()
                matched_tokens_by_doc[doc_idx].add(token)

        # Apply metadata filters and format results
        ranked_results = []
        # Sort documents by score descending
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for doc_idx, score in sorted_docs:
            course_id = self.doc_ids[doc_idx]
            course = self.courses_by_id[course_id]

            # Filtering
            if difficulty and difficulty.lower() != "all" and course.get("difficulty", "").lower() != difficulty.lower():
                continue
            if category and category.lower() != "all" and course.get("category", "").lower() != category.lower():
                continue
            if max_duration is not None and course.get("duration_hours", 0) > max_duration:
                continue
            if min_duration is not None and course.get("duration_hours", 0) < min_duration:
                continue
            if provider and provider.lower() != "all" and course.get("provider", "").lower() != provider.lower():
                continue
            if free_only and course.get("price", 0.0) > 0.0:
                continue

            # Identify matching skills from matched tokens
            matched_skills = []
            matched_tok_set = matched_tokens_by_doc.get(doc_idx, set())
            for skill in course.get("skills", []):
                skill_toks = set(self.tokenize(skill))
                if skill_toks and skill_toks.issubset(matched_tok_set):
                    matched_skills.append(skill)
                elif any(t in matched_tok_set for t in skill_toks):
                    matched_skills.append(skill)

            ranked_results.append({
                **course,
                "score": round(score, 4),
                "matched_skills": list(set(matched_skills)),
                "retrieval_sources": ["BM25"],
                "rank": len(ranked_results) + 1
            })

            if len(ranked_results) >= top_k:
                break

        return ranked_results
