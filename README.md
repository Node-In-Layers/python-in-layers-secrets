# In Layers Secrets

The official library for handling secrets with In Layers (Python).

## How to Use

### 1. Install Library

```bash
pip install in-layers-secrets
# or
poetry add in-layers-secrets
```

### 2. Add To Configuration

```python
# config_base.py
from box import Box
from in_layers.core import CoreNamespace, LogFormat, LogLevelNames
import in_layers.secrets.config as secrets_config
from in_layers.secrets import SecretsNamespace


def get_config():
    return Box(
        environment="base",
        system_name="your-system-name",
        in_layers_core=Box(
            logging=Box(
                log_level=LogLevelNames.info,
                log_format=LogFormat.simple,
            ),
            layer_order=["services", "features"],
            domains=[
                # If using the configuration approach (recommended for most applications)
                # put the secrets configuration here.
                secrets_config,
                # your domains
            ],
        ),
        # Optional: omit or use {} to use the built-in default backend chain.
        in_layers_secrets=Box({}),
    )
```

To use the built-in defaults, omit `secret_service_factory` (or pass `in_layers_secrets={}`). Secrets are looked up in the JSON/JSON5 backend first, then `os.environ`, then the `.env` backend.

## Main Capabilities

1. Ability to retrieve system-level secrets from a secrets manager through a unified interface.
2. Ability to seamlessly replace secrets placeholders in a system's config via a secrets manager.

## Domains

### SecretsNamespace.core (`in_layers_secrets`)

Provides the basic capabilities of storing and retrieving secrets.

Core exposes the full string + JSON API (JSON is synthesized from strings when a backend omits JSON methods). When no custom factory is configured, the built-in read chain is used.

#### SecretsConfig

`SecretsConfig` (under `in_layers_secrets` in system config) resolves secrets in this order:

1. **`secret_service_factory`** — `(ctx: CommonContext) -> SecretsService`. Use during globals when full services context is not available yet (for example a future AWS secrets factory).
2. **Default JSON backend** — tries `secrets.{ENVIRONMENT}.json` and `.json5`.
3. **Default environment backend** — if JSON does not contain the key, tries the exact key in `os.environ`.
4. **Default dotenv backend** — if neither JSON nor `os.environ` contains the key, tries the exact key in `.env`.

The fallback happens per lookup. A configured `secret_service_factory` replaces this built-in chain entirely. The `.env` path defaults to `.env` in the system working directory and can be changed with `dotenv_file_path`.

The ordered step ids are exported as **`SECRETS_CONFIG_RESOLUTION`** from this package (for docs and tooling).

#### Interface Description

Any domain can provide the ability to retrieve and store secrets by providing a services layer that implements the `SecretsService` protocol. **`get_stored_secret` and `store_secret` are required.** **`get_stored_json_secret` and `store_secret_json` are optional** on the implementation: if you omit them, **this library automatically implements them** by delegating to `get_stored_secret` / `store_secret` with `json.loads` and `json.dumps`.

Provide your own `get_stored_json_secret` / `store_secret_json` only when the backend can handle JSON more efficiently or differently than string round-tripping.

NOTE: If a domain does not want to provide a `store_secret()` function, then the system should throw an exception.

#### Types

```python
from typing import Any, Mapping, Protocol, TypedDict


class GetSecretProps(TypedDict, total=False):
    """The key path to the stored secret, plus optional metadata."""

    key: str


class StoreSecretProps(TypedDict, total=False):
    """The key path and string value to store, plus optional metadata."""

    key: str
    value: str


class StoreSecretJsonProps(TypedDict, total=False):
    """The key path and JSON value to store, plus optional metadata."""

    key: str
    value: Mapping[str, Any]


class SecretsService(Protocol):
    """
    What a secrets manager *implements*.
    JSON methods are optional; the library fills them in when missing.
    """

    def get_stored_secret(self, props: GetSecretProps) -> str: ...

    def store_secret(self, props: StoreSecretProps) -> None: ...

    def get_stored_json_secret(self, props: GetSecretProps) -> Mapping[str, Any]: ...

    def store_secret_json(self, props: StoreSecretJsonProps) -> None: ...
```

Call sites receive `SecretsCoreServices` from `in_layers.secrets.core.services.create`, which always exposes all four methods (native or library-wrapped).

#### Example:

Most managers only implement the string APIs. **Do not** implement `get_stored_json_secret` / `store_secret_json` unless the backend needs native JSON behavior—the library supplies those by wrapping `get_stored_secret` / `store_secret` with `json.loads` / `json.dumps`, so **callers always use the full API and never add their own JSON fallbacks**.

```python
# your_system/src/your_domain/services.py
from in_layers.secrets import GetSecretProps, StoreSecretProps


class MyDomainServices:
    def __init__(self, context):
        self.__context = context

    def get_stored_secret(self, props: GetSecretProps) -> str:
        # read stored secret using props["key"] (and optional metadata).
        return "stored-secret"

    def store_secret(self, props: StoreSecretProps) -> None:
        raise NotImplementedError("Not implemented")


def create(context) -> MyDomainServices:
    return MyDomainServices(context)
```

### SecretsNamespace.config (`in_layers_secrets_config`)

This domain provides the most common capability of loading secrets at runtime, by replacing structured secret placeholders, via a secrets manager.
Instead of calling stored secrets each time they're used, the path to secrets can be configured in the config, and then at load time, all secrets are pulled down and set in the config. These secrets can then be seamlessly used throughout the application.

#### How To Use

1. Define and create a placeholder for your secret inside your configuration file.

```python
# config_base.py
from box import Box
from in_layers.core import LogFormat, LogLevelNames
import in_layers.secrets.config as secrets_config


def get_config():
    return Box(
        environment="base",
        system_name="your-system-name",
        in_layers_core=Box(
            logging=Box(
                log_level=LogLevelNames.info,
                log_format=LogFormat.simple,
            ),
            layer_order=["services", "features"],
            domains=[
                # Place this close to the top. Above anything that needs a
                # clean config with secrets replaced.
                secrets_config,
                # your domains
            ],
        ),
        in_layers_secrets=Box({}),
        your_domain=Box(
            # This entire structure will collapse down to a string.
            # Example: my_secret_key: "the stored secret"
            my_secret_key={
                "type": "nil-secret",
                "format": "string",
                "key": "/your-system-name/dev/my-secret-key",
            },
        ),
        another_domain=Box(
            nested=Box(
                # This structure is replaced with a json object.
                # Example: another_secret_key: {}
                another_secret_key={
                    "type": "nil-secret",
                    "format": "json",
                    "key": "/your-system-name/dev/another-secret-as-a-json",
                },
            ),
        ),
    )
```

#### Another Example Using A Custom Secrets Factory (e.g. AWS-shaped)

A Python AWS secrets package is separate (same idea as `@node-in-layers/aws` in TypeScript). Wire it with `secret_service_factory` and pass backend metadata on placeholders:

```python
# config_base.py
from box import Box
from in_layers.core import LogFormat, LogLevelNames
import in_layers.secrets.config as secrets_config


def get_config():
    # from in_layers.aws import secrets_service  # when available
    def secrets_service(ctx):
        # return a SecretsService implementation for AWS SM / SSM / etc.
        raise NotImplementedError("Provide your AWS (or other) secrets backend")

    return Box(
        environment="base",
        system_name="your-system-name",
        in_layers_core=Box(
            logging=Box(
                log_level=LogLevelNames.info,
                log_format=LogFormat.simple,
            ),
            layer_order=["services", "features"],
            domains=[
                secrets_config,
                # your domains
            ],
        ),
        in_layers_secrets=Box(
            secret_service_factory=secrets_service,
        ),
        your_domain=Box(
            # This entire structure will collapse down to a string.
            my_secret_key={
                "aws_service": "secretsManager",
                "type": "nil-secret",
                "format": "string",
                "key": "/your-system-name/dev/my-secret-key",
            },
        ),
        another_domain=Box(
            nested=Box(
                # A property that is stored in parameter store
                # (not a secret, but rides on the backbone)
                an_aws_property={
                    "aws_service": "parameterStore",
                    "type": "nil-secret",
                    "format": "json",
                    "key": "/your-system-name/dev/not-a-secret-a-config",
                },
            ),
        ),
    )
```

```python
from enum import Enum
from typing import Any, TypedDict


class SecretFormat(str, Enum):
    string = "string"
    json = "json"


class StructuredSecretEntry(TypedDict, total=False):
    """
    This tells the system that this is an in-layers secret that should be replaced.
    """

    type: str  # "nil-secret"
    # The format for replacing the SecretEntry. If string, it sets a string value.
    # If json, it uses the JSON secret path (resolved via the same automatic JSON
    # wrapping as get_stored_json_secret when the manager only implements string APIs).
    format: str
    # The key path to the secret.
    key: str
    # Optional information passed into the storage system (extra keys allowed).
```

### SecretsNamespace.json (`in_layers_secrets_json`)

The default file-based backend: secrets are read from JSON or JSON5 files under the working directory, using the same `SecretsService` contract as other backends.

#### File Pathing

These files are automatically found at the base of the system directory (working directory) using the environment name.

`secrets.{ENVIRONMENT}.json`

`secrets.{ENVIRONMENT}.json5`

### SecretsNamespace.env (`in_layers_secrets_env`)

The environment backend reads an exact `GetSecretProps["key"]` from `os.environ`. It does not interpret dots as paths and does not modify the environment.

### SecretsNamespace.dotenv (`in_layers_secrets_dotenv`)

The dotenv backend parses `.env` without loading it into `os.environ`:

```python
in_layers_secrets=Box(
    dotenv_file_path="config/local.env",
)
```

Both local backends are read-only. Missing keys raise an error, and `store_secret`/`store_secret_json` are not implemented. Keep `.env` files out of source control.
