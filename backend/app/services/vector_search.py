import math
from typing import List, Dict, Any

class VectorSearchService:
    """
    In-memory vector database and embedding engine for semantic pay equity policies,
    disparity precedents, and market compensation benchmarks.
    Simulates vector index behavior (compatible with Pinecone / Weaviate architecture).
    """

    def __init__(self):
        # Seeded knowledge base of compensation policies, regulatory frameworks, and market precedents
        self.documents = [
            {
                "id": "DOC-POL-001",
                "category": "Policy",
                "title": "Global FTE Normalization Policy",
                "text": "All base compensation for part-time employees must be normalized to a standard 1.0 full-time equivalent basis (Annualized Base divided by recorded FTE) prior to comparing against role and level salary bands.",
                "keywords": ["fte", "part-time", "normalization", "annualized", "hours", "ratio"]
            },
            {
                "id": "DOC-POL-002",
                "category": "Regulatory",
                "title": "Equal Pay Act & Title VII Non-Adverse Audit Guardrails",
                "text": "Protected demographic attributes including gender, race, ethnicity, age, and marital status must never be included as input features in individual compensation determinations or regression models.",
                "keywords": ["equal pay", "discrimination", "protected", "non-adverse", "guardrail", "title vii", "gender", "race"]
            },
            {
                "id": "DOC-POL-003",
                "category": "Precedent",
                "title": "Dual-Custody Proposal Governance Protocol",
                "text": "Compensation adjustment proposals require independent HR partner review. Creators are strictly barred from approving their own proposals to prevent conflicts of interest and unauthorized salary escalation.",
                "keywords": ["separation of duties", "approval", "dual custody", "proposal", "workflow", "self-approval", "conflict"]
            },
            {
                "id": "DOC-POL-004",
                "category": "Market Benchmark",
                "title": "Compa-Ratio Band Positioning Thresholds",
                "text": "Compa-ratio between 0.85 and 1.15 represents healthy target alignment. Ratios below 0.80 indicate critical pay compression requiring mandatory parity investigation and evidence-based adjustment proposals.",
                "keywords": ["compa-ratio", "midpoint", "compression", "outlier", "parity", "threshold", "below band"]
            },
            {
                "id": "DOC-POL-005",
                "category": "Data Integrity",
                "title": "Effective-Dated Compensation Band Temporal Integrity",
                "text": "Salary records must only be compared against compensation bands where effective start date precedes the salary effective date and effective end date is null or in the future. Expired bands trigger immediate data quality exceptions.",
                "keywords": ["effective date", "expired band", "temporal", "data quality", "integrity", "currency", "fx"]
            },
            {
                "id": "DOC-POL-006",
                "category": "Methodology",
                "title": "Small-Sample Cohort Suppression Guideline",
                "text": "Comparable role-level groups with fewer than 5 members are automatically suppressed from distribution statistics (interquartile range and median) to safeguard employee privacy and avoid statistical volatility.",
                "keywords": ["suppression", "small sample", "comparable groups", "privacy", "iqr", "median", "sample size"]
            }
        ]

    def _simple_embedding(self, text: str) -> List[float]:
        """Deterministic pseudo-embedding vector of 16 dimensions based on character hash distributions."""
        words = text.lower().split()
        vector = [0.0] * 16
        for i, word in enumerate(words):
            val = sum(ord(c) for c in word)
            idx = val % 16
            vector[idx] += 1.0 + (i * 0.05)
        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [round(x / norm, 4) for x in vector]

    def semantic_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Cosine similarity vector search across policy vector index."""
        query_lower = query.lower()
        q_words = set(query_lower.split())
        query_vec = self._simple_embedding(query)

        results = []
        for doc in self.documents:
            doc_vec = self._simple_embedding(doc["title"] + " " + doc["text"])
            
            # Cosine similarity
            dot_product = sum(q * d for q, d in zip(query_vec, doc_vec))
            
            # Keyword overlap boost for precision
            doc_keywords = set(doc["keywords"])
            overlap = len(q_words.intersection(doc_keywords))
            score = dot_product * 0.6 + (min(overlap, 4) * 0.1)

            results.append({
                "id": doc["id"],
                "category": doc["category"],
                "title": doc["title"],
                "content": doc["text"],
                "similarity_score": round(min(score, 0.99), 3),
                "vector_dimension": len(doc_vec)
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

vector_search_service = VectorSearchService()
