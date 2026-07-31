"""
Report generation service.
"""
import json
import os
from datetime import datetime
from typing import List, Dict
from app.core.config import settings


def generateReport(job_data: Dict, rankings: List[Dict]) -> Dict:
    """Generate a ranking report as structured JSON."""
    report_data = {
        "report_type": "candidate_ranking",
        "generated_at": datetime.utcnow().isoformat(),
        "job": {
            "id": job_data.get("id"),
            "title": job_data.get("title"),
            "company": job_data.get("company"),
            "required_skills": job_data.get("required_skills", []),
        },
        "total_candidates": len(rankings),
        "rankings": [
            {
                "rank": r.get("rank_position"),
                "candidate_name": r.get("candidate_name"),
                "overall_score": round(r.get("overall_score", 0) * 100, 1),
                "similarity_score": round(r.get("similarity_score", 0) * 100, 1),
                "skill_match_score": round(r.get("skill_match_score", 0) * 100, 1),
                "matching_skills": r.get("matching_skills", []),
                "skill_gap": r.get("skill_gap", []),
                "explanation": r.get("explanation"),
            }
            for r in rankings
        ],
        "summary": {
            "top_candidate": rankings[0]["candidate_name"] if rankings else None,
            "average_score": round(
                sum(r.get("overall_score", 0) for r in rankings) / len(rankings) * 100, 1
            ) if rankings else 0,
        }
    }
    return report_data


def downloadReport(report_id: int, report_data: Dict) -> str:
    """Save report to file and return file path."""
    file_name = f"report_{report_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    file_path = os.path.join(settings.REPORTS_DIR, file_name)
    with open(file_path, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    return file_path
