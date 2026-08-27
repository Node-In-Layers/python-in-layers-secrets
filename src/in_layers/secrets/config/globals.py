from __future__ import annotations

from typing import Any

from box import Box

from in_layers.core.protocols import CommonContext

from ..context import to_services_context_for_secrets
from ..core import services as core_services
from ..types import SecretsNamespace
from . import features, services as config_services


class ConfigSecretsGlobals:
    def __init__(self, context: CommonContext):
        self.__context = context

    def create(self) -> dict[str, Any]:
        svc_ctx = to_services_context_for_secrets(self.__context)
        core = core_services.create(svc_ctx)
        config_service = config_services.create(svc_ctx)
        services_box = Box(dict(svc_ctx.services) if svc_ctx.services else {})
        services_box[SecretsNamespace.core.value] = core
        services_box[SecretsNamespace.config.value] = config_service
        features_ctx = Box(
            {
                **dict(svc_ctx),
                "features": Box({"get_features": lambda: None}),
                "services": services_box,
            }
        )
        f = features.create(features_ctx)
        new_config = f.replace_secrets_config_objects(self.__context.config)
        return {"config": new_config}


def create(context: CommonContext) -> dict[str, Any]:
    """
    Domain globals entrypoint. NIL expects globals.create(common_context)
    to return the patch object (e.g. { config }), not a services instance.
    """
    return ConfigSecretsGlobals(context).create()
