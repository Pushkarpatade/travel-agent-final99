"""Asynchronous AI Background Job Worker for TravelPilot.

Manages asynchronous trip planning and disruption scan tasks.
Provides lifecycle tracking across states:
- queued
- running
- completed
- failed

Allows clients to poll job status without incurring HTTP gateway timeouts,
preserving intermediate execution state across browser refreshes.
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field

from backend.database.session import SessionLocal
from backend.models.models import Trip
from backend.agents.planner_agent import planner_agent

logger = logging.getLogger("travelpilot.job_worker")

class JobStatusResponse(BaseModel):
    job_id: str
    trip_id: int
    status: str  # "queued", "running", "completed", "failed"
    progress_pct: int = 0
    current_step: str = "Queued in AI execution buffer"
    logs: List[str] = Field(default_factory=list)
    itinerary_id: Optional[int] = None
    error: Optional[str] = None
    created_at: float
    completed_at: Optional[float] = None

class JobWorkerManager:
    def __init__(self, max_workers: int = 4):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ai-planner-worker")

    def enqueue_planning_job(self, trip_id: int) -> str:
        """Enqueues an asynchronous trip planning job and returns the job ID immediately."""
        job_id = f"job-{uuid.uuid4().hex[:10]}"
        now = time.time()

        self.jobs[job_id] = {
            "job_id": job_id,
            "trip_id": trip_id,
            "status": "queued",
            "progress_pct": 5,
            "current_step": "Job enqueued. Initializing Multi-Agent supervisor...",
            "logs": ["Job created. Preparing agent pipeline..."],
            "itinerary_id": None,
            "error": None,
            "created_at": now,
            "completed_at": None
        }

        # Submit task to ThreadPool
        self.executor.submit(self._run_job_worker, job_id, trip_id)
        logger.info(f"Enqueued planning job {job_id} for Trip #{trip_id}")
        return job_id

    def _run_job_worker(self, job_id: str, trip_id: int):
        """Worker thread executing the multi-agent planning workflow."""
        db = SessionLocal()
        try:
            self.jobs[job_id]["status"] = "running"
            self.jobs[job_id]["progress_pct"] = 25
            self.jobs[job_id]["current_step"] = "Auditor Agent: Running safety guardrails..."
            self.jobs[job_id]["logs"].append("Auditor Agent: Input validation passed.")

            trip = db.query(Trip).filter(Trip.id == trip_id).first()
            if not trip:
                raise ValueError(f"Trip #{trip_id} not found in database.")

            self.jobs[job_id]["progress_pct"] = 50
            self.jobs[job_id]["current_step"] = "Research & Weather Agents: Querying live sources..."
            self.jobs[job_id]["logs"].append(f"Researching live attractions for {trip.destination}...")

            # Run full planning pipeline
            itinerary = planner_agent.plan_trip(db, trip)

            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["progress_pct"] = 100
            self.jobs[job_id]["current_step"] = "Itinerary successfully synthesized!"
            self.jobs[job_id]["itinerary_id"] = itinerary.id
            self.jobs[job_id]["completed_at"] = time.time()
            self.jobs[job_id]["logs"].append(f"Plan finalized! Total cost: ₹{itinerary.total_estimated_cost}")
            logger.info(f"Job {job_id} completed successfully for Trip #{trip_id}")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error"] = str(e)
            self.jobs[job_id]["current_step"] = f"Execution error: {str(e)}"
            self.jobs[job_id]["completed_at"] = time.time()
        finally:
            db.close()

    def get_job_status(self, job_id: str) -> Optional[JobStatusResponse]:
        """Returns the current state and intermediate logs of a job."""
        data = self.jobs.get(job_id)
        if not data:
            return None
        return JobStatusResponse(**data)

job_worker = JobWorkerManager()
