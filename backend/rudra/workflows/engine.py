"""Workflow layer — human-in-the-loop task orchestration."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    AWAITING_APPROVAL = "awaiting_approval"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    agent_type: str | None = None
    status: StepStatus = StepStatus.PENDING
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = False
    approved: bool | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class Workflow:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    user_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    steps: list[WorkflowStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """Executes multi-step workflows with human-in-the-loop checkpoints."""

    def __init__(self):
        self._workflows: dict[str, Workflow] = {}

    def create(
        self,
        name: str,
        user_id: str,
        steps: list[dict[str, Any]],
        *,
        description: str = "",
    ) -> Workflow:
        workflow = Workflow(
            name=name,
            description=description,
            user_id=user_id,
            steps=[
                WorkflowStep(
                    name=s.get("name", f"Step {i + 1}"),
                    agent_type=s.get("agent_type"),
                    requires_approval=s.get("requires_approval", False),
                    input_data=s.get("input", {}),
                )
                for i, s in enumerate(steps)
            ],
        )
        self._workflows[workflow.id] = workflow
        return workflow

    def get(self, workflow_id: str) -> Workflow | None:
        return self._workflows.get(workflow_id)

    def approve_step(self, workflow_id: str, step_id: str) -> bool:
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return False
        for step in workflow.steps:
            if step.id == step_id:
                step.approved = True
                if workflow.status == WorkflowStatus.AWAITING_APPROVAL:
                    workflow.status = WorkflowStatus.RUNNING
                return True
        return False

    def list_pending_approvals(self, user_id: str) -> list[Workflow]:
        return [
            w
            for w in self._workflows.values()
            if w.user_id == user_id and w.status == WorkflowStatus.AWAITING_APPROVAL
        ]
