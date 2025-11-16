from .candidates import router as candidates_router
from .jobs_router import router as jobs_router

__all__ = ["candidates_router", "jobs_router"]
from .job_descriptions import router as job_descriptions_router

__all__ = ["candidates_router", "job_descriptions_router"]
