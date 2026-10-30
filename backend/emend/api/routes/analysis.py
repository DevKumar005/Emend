import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from contracts.schemas import AnalysisRequest, ImpactReport, FinalReport, TestRun
from ..store import DatabaseStore
from ..orchestrator import orchestrator

router = APIRouter(prefix="/api/analysis", tags=["analysis"])
store = DatabaseStore()

@router.post("")
async def create_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    analysis_id = str(uuid.uuid4())[:8]
    job = store.create_job(
        job_id=analysis_id,
        repo_source=req.repo_source,
        failing_test=req.failing_test,
        mode=req.mode
    )

    background_tasks.add_task(
        orchestrator.run_pipeline,
        job_id=analysis_id,
        repo_source=req.repo_source,
        failing_test=req.failing_test,
        mode=req.mode,
        auto_repair=True
    )

    return {
        "job_id": analysis_id,
        "analysis_id": analysis_id,
        "status": job.status
    }

@router.get("/{id}/impact", response_model=ImpactReport)
async def get_impact(id: str):
    report = store.get_impact_report(id)
    if not report:
        raise HTTPException(status_code=404, detail="Impact report not ready or not found.")
    return report

@router.post("/{id}/repair")
async def trigger_repair(id: str, background_tasks: BackgroundTasks):
    job = store.get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    # Re-trigger pipeline repair stage if needed
    impact = store.get_impact_report(id)
    if not impact:
        raise HTTPException(status_code=400, detail="Cannot repair before impact analysis finishes.")

    return {"status": "repair_in_progress", "job_id": id}

@router.get("/{id}/tests")
async def get_test_runs(id: str):
    runs = store.get_test_runs(id)
    return runs

@router.get("/{id}/report", response_model=FinalReport)
async def get_final_report(id: str):
    report = store.get_final_report(id)
    if not report:
        raise HTTPException(status_code=404, detail="Final report not ready or not found.")
    return report

@router.get("/{id}/patch")
async def download_patch(id: str):
    report = store.get_final_report(id)
    if not report or not report.patch:
        raise HTTPException(status_code=404, detail="No patch generated for this analysis.")
    
    headers = {
        "Content-Disposition": f"attachment; filename=emend_repair_{id}.patch"
    }
    return Response(content=report.patch, media_type="text/x-diff", headers=headers)
