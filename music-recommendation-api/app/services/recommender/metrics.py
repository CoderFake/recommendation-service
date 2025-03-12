import logging
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Set

logger = logging.getLogger(__name__)


def precision_at_k(recommended_items: List[int], relevant_items: Set[int], k: int) -> float:
    if len(recommended_items) == 0 or k <= 0:
        return 0.0

    top_k = recommended_items[:k]
    num_relevant = sum(1 for item in top_k if item in relevant_items)

    return num_relevant / min(k, len(top_k))


def recall_at_k(recommended_items: List[int], relevant_items: Set[int], k: int) -> float:
    if len(relevant_items) == 0 or len(recommended_items) == 0 or k <= 0:
        return 0.0

    top_k = recommended_items[:k]

    num_relevant = sum(1 for item in top_k if item in relevant_items)

    return num_relevant / len(relevant_items)


def ndcg_at_k(recommended_items: List[int], relevant_items: Dict[int, float], k: int) -> float:
    if len(recommended_items) == 0 or len(relevant_items) == 0 or k <= 0:
        return 0.0

    top_k = recommended_items[:k]

    dcg = 0.0
    for i, item in enumerate(top_k):
        relevance = relevant_items.get(item, 0.0)
        dcg += relevance / np.log2(i + 2)  # i+2 because i is 0-indexed

    ideal_ranking = sorted(relevant_items.values(), reverse=True)[:k]
    idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_ranking))

    if idcg == 0:
        return 0.0
    return dcg / idcg


def map_at_k(recommended_items_list: List[List[int]], relevant_items_list: List[Set[int]], k: int) -> float:
    if len(recommended_items_list) == 0 or len(relevant_items_list) == 0 or k <= 0:
        return 0.0

    ap_values = []

    for recommended_items, relevant_items in zip(recommended_items_list, relevant_items_list):
        if len(relevant_items) == 0 or len(recommended_items) == 0:
            continue

        top_k = recommended_items[:k]

        ap = 0.0
        num_relevant_found = 0

        for i, item in enumerate(top_k):
            if item in relevant_items:
                num_relevant_found += 1
                precision_at_i = num_relevant_found / (i + 1)
                ap += precision_at_i

        ap /= min(k, len(relevant_items))

        ap_values.append(ap)

    if len(ap_values) == 0:
        return 0.0
    return sum(ap_values) / len(ap_values)


def diversity(recommended_items_list: List[List[int]]) -> float:
    if len(recommended_items_list) <= 1:
        return 0.0

    recommended_sets = [set(items) for items in recommended_items_list]

    n = len(recommended_sets)
    similarities = []

    for i in range(n):
        for j in range(i + 1, n):
            set_i = recommended_sets[i]
            set_j = recommended_sets[j]

            if not set_i or not set_j:
                continue

            intersection = len(set_i.intersection(set_j))
            union = len(set_i.union(set_j))

            jaccard = intersection / union if union > 0 else 0.0
            similarities.append(jaccard)

    if not similarities:
        return 1.0

    return 1.0 - sum(similarities) / len(similarities)


def novelty(recommended_items: List[int], item_popularity: Dict[int, float]) -> float:
    if len(recommended_items) == 0 or len(item_popularity) == 0:
        return 0.0

    novelty_scores = []

    for item in recommended_items:
        popularity = item_popularity.get(item, 0.0)

        log_popularity = np.log(popularity + 1e-10)
        novelty_scores.append(-log_popularity)

    return sum(novelty_scores) / len(novelty_scores)


def coverage(recommended_items_list: List[List[int]], total_items: int) -> float:
    if len(recommended_items_list) == 0 or total_items == 0:
        return 0.0

    unique_items = set()
    for items in recommended_items_list:
        unique_items.update(items)

    return len(unique_items) / total_items


def serendipity(
        recommended_items: List[int],
        expected_items: Set[int],
        relevant_items: Set[int]
) -> float:
    if len(recommended_items) == 0:
        return 0.0

    serendipity_scores = []

    for item in recommended_items:
        unexpectedness = 1.0 if item not in expected_items else 0.0
        relevance = 1.0 if item in relevant_items else 0.0

        serendipity_scores.append(unexpectedness * relevance)

    return sum(serendipity_scores) / len(serendipity_scores)


def personalization(recommended_items_list: List[List[int]]) -> float:
    return diversity(recommended_items_list)


def evaluate_recommendations(
        recommended_items_list: List[List[int]],
        ground_truth_list: List[Set[int]],
        item_popularity: Optional[Dict[int, float]] = None,
        total_items: Optional[int] = None,
        expected_items_list: Optional[List[Set[int]]] = None,
        k_values: List[int] = [5, 10, 20]
) -> Dict[str, Any]:

    if len(recommended_items_list) != len(ground_truth_list):
        raise ValueError("Length mismatch between recommended items and ground truth")

    if expected_items_list is not None and len(expected_items_list) != len(recommended_items_list):
        raise ValueError("Length mismatch between recommended items and expected items")

    results = {}

    for k in k_values:
        ground_truth_dicts = [
            {item: 1.0 for item in items} for items in ground_truth_list
        ]

        precision_values = [
            precision_at_k(rec, rel, k)
            for rec, rel in zip(recommended_items_list, ground_truth_list)
        ]
        results[f"precision@{k}"] = np.mean(precision_values)

        recall_values = [
            recall_at_k(rec, rel, k)
            for rec, rel in zip(recommended_items_list, ground_truth_list)
        ]
        results[f"recall@{k}"] = np.mean(recall_values)

        ndcg_values = [
            ndcg_at_k(rec, rel_dict, k)
            for rec, rel_dict in zip(recommended_items_list, ground_truth_dicts)
        ]
        results[f"ndcg@{k}"] = np.mean(ndcg_values)

    results[f"map@{max(k_values)}"] = map_at_k(
        recommended_items_list, ground_truth_list, max(k_values)
    )

    results["diversity"] = diversity(recommended_items_list)

    if total_items:
        results["coverage"] = coverage(recommended_items_list, total_items)

    if item_popularity:
        novelty_values = [
            novelty(rec, item_popularity) for rec in recommended_items_list
        ]
        results["novelty"] = np.mean(novelty_values)

    if expected_items_list:
        serendipity_values = [
            serendipity(rec, exp, rel)
            for rec, exp, rel in zip(recommended_items_list, expected_items_list, ground_truth_list)
        ]
        results["serendipity"] = np.mean(serendipity_values)

    results["personalization"] = personalization(recommended_items_list)

    return results