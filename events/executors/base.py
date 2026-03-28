#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExecutionContext:
    task_id: str
    capability: str
    operation: str
    worker_id: str


@dataclass
class ExecutionResult:
    status: str
    summary: dict
    structured_result: dict
    artifacts: list[dict] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    error: dict | None = None
    executor_type: str = ""
    tool_name: str | None = None

