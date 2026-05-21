"""Run metadata for traceability."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class RunMetadata:
    run_id: str
    pipeline_type: str
    project_id: str
    segment_id: str
    status: RunStatus
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    mlflow_run_id: Optional[str] = None
    error_message: Optional[str] = None
