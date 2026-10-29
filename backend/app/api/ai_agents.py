from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.vector_search import vector_search_service
from app.services.crew_agent import crew_agent_service
from app.security.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["Agent & Vector Search Intelligence"])

@router.get("/vector-search")
def search_policies(
    query: str = Query(..., description="Semantic search query for compensation policies"),
    top_k: int = Query(3, ge=1, le=10),
    current_user: dict = Depends(get_current_user)
):
    """
    Pinecone/Weaviate-style Vector Search endpoint for policy & market equity benchmarks.
    """
    results = vector_search_service.semantic_search(query, top_k=top_k)
    return {
        "query": query,
        "vector_index": "compensation-equity-policies",
        "dimension": 16,
        "results_count": len(results),
        "results": results
    }

@router.get("/crew-triage/{employee_id}")
def run_crew_triage(
    employee_id: str,
    compa_ratio: float = 1.0,
    band_position: float = 50.0,
    normalized_salary: float = 120000.0,
    band_mid: Optional[float] = 125000.0,
    title: str = "Senior Engineer",
    current_user: dict = Depends(get_current_user)
):
    """
    CrewAI / LangGraph multi-agent collaborative investigation pipeline for compensation review.
    """
    emp_data = {"employee_id": employee_id, "title": title}
    metrics = {
        "compa_ratio": compa_ratio,
        "band_position": band_position,
        "normalized_fte_salary": normalized_salary,
        "band_mid": band_mid
    }
    analysis = crew_agent_service.analyze_employee(emp_data, metrics)
    return analysis
