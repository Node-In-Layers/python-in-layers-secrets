from __future__ import annotations

from typing import Any, Protocol

from in_layers.core.protocols import Config


class JsonSecretsContext(Protocol):
    config: Config
    constants: Any
