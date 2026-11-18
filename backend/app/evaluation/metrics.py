import math
from typing import List, Set, Any

def precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = 10) -> float:
    """
    Precision@K = (Number of relevant courses in top K) / K
    """
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    hits = sum(1 for cid in top_k if cid in relevant_ids)
    return round(hits / k, 4)

def recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = 10) -> float:
    """
    Recall@K = (Number of relevant courses in top K) / (Total relevant courses)
    """
    if not relevant_ids:
        return 0.0
    top_k = retrieved_ids[:k]
    hits = sum(1 for cid in top_k if cid in relevant_ids)
    return round(hits / len(relevant_ids), 4)

def dcg_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = 10) -> float:
    """
    Discounted Cumulative Gain at K using standard logarithmic discounting:
    DCG@K = sum_{i=1}^K ( (2^rel_i - 1) / log2(i + 1) )
    Binary relevance: rel_i = 1 if retrieved_id in relevant_ids else 0.
    """
    score = 0.0
    for i, cid in enumerate(retrieved_ids[:k], start=1):
        rel = 1.0 if cid in relevant_ids else 0.0
        if rel > 0:
            score += (math.pow(2, rel) - 1.0) / math.log2(i + 1)
    return score

def ndcg_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = 10) -> float:
    """
    Normalized Discounted Cumulative Gain at K:
    NDCG@K = DCG@K / IDCG@K
    """
    actual_dcg = dcg_at_k(retrieved_ids, relevant_ids, k)
    if actual_dcg == 0.0:
        return 0.0

    # Ideal DCG puts all relevant items at the top
    ideal_hits = min(k, len(relevant_ids))
    ideal_dcg = sum((math.pow(2, 1.0) - 1.0) / math.log2(i + 1) for i in range(1, ideal_hits + 1))

    if ideal_dcg == 0.0:
        return 0.0
    return round(actual_dcg / ideal_dcg, 4)

def reciprocal_rank(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """
    Reciprocal Rank = 1 / rank_of_first_relevant_item
    """
    for rank, cid in enumerate(retrieved_ids, start=1):
        if cid in relevant_ids:
            return round(1.0 / rank, 4)
    return 0.0
