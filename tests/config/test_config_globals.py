from __future__ import annotations

from types import SimpleNamespace

from box import Box

from in_layers.core.entries import SystemProps, load_system
from in_layers.core.protocols import Domain, LogFormat, LogLevelNames
from in_layers.secrets import SecretsNamespace
import in_layers.secrets.config as secrets_config


def test_globals_replace_with_factory():
    class DemoServices:
        def __init__(self, ctx):
            self._ctx = ctx

        def read_secret(self):
            return self._ctx.config.your_domain.my_secret_key

        def read_json(self):
            return self._ctx.config.another.nested.another_secret_key

    class DemoDomain(Domain):
        name = "demo"
        services = SimpleNamespace(create=lambda ctx: DemoServices(ctx))

    class StubBackend:
        def get_stored_secret(self, props):
            return "resolved-secret"

        def get_stored_json_secret(self, props):
            return {"ok": True}

        def store_secret(self, props):
            raise NotImplementedError("Not implemented")

    config = Box(
        system_name="test",
        environment="test",
        in_layers_core=Box(
            logging=Box(
                log_level=LogLevelNames.info,
                log_format=LogFormat.simple,
            ),
            layer_order=["services"],
            domains=[secrets_config, DemoDomain],
        ),
        in_layers_secrets=Box(
            secret_service_factory=lambda _ctx: StubBackend(),
        ),
        your_domain=Box(
            my_secret_key={
                "type": "nil-secret",
                "format": "string",
                "key": "/path",
            }
        ),
        another=Box(
            nested=Box(
                another_secret_key={
                    "type": "nil-secret",
                    "format": "json",
                    "key": "/json-path",
                }
            )
        ),
    )

    system = load_system(SystemProps(environment="test", config=config))
    assert system.services.demo.read_secret() == "resolved-secret"
    assert system.services.demo.read_json() == {"ok": True}


def test_config_domain_name():
    assert secrets_config.name == SecretsNamespace.config.value
