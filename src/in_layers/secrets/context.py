from __future__ import annotations

from typing import Any

from box import Box

from in_layers.core.protocols import CommonContext


def to_services_context_for_secrets(ctx: CommonContext) -> Any:
    """
    Builds a minimal ServicesContext from CommonContext for secrets backends
    and for running core during globals (before full layer context exists).
    """
    return Box(
        {
            "config": ctx.config,
            "root_logger": ctx.root_logger,
            "constants": ctx.constants,
            "log": {},
            "models": {},
            "services": Box({"get_services": lambda: None}),
        }
    )
