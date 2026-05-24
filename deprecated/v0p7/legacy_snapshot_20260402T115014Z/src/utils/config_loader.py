"""Configuration loading and validation utilities.

This module is intentionally small and explicit. It loads the local `.env` file,
reads YAML configs from `configs/`, validates required runtime settings, and
returns one typed object that can be passed into data clients and future CLI
commands.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError
import yaml

from src.utils.paths import ProjectPaths, build_project_paths, find_project_root


EXPECTED_CONFIG_NAMES = frozenset(
    {
        "project",
        "data_sources",
        "dataset_build",
        "features",
        "labels",
        "model_market_baseline",
        "model_multimodal",
        "training",
        "evaluation",
    }
)


class ConfigError(RuntimeError):
    """Raised when configuration files or environment variables are invalid."""


class EnvironmentSettings(BaseModel):
    """Environment-derived settings validated from the local runtime."""

    model_config = ConfigDict(extra="forbid")

    twelve_data_api_key: SecretStr
    finnhub_api_key: SecretStr
    sec_user_agent: str

    split_events_api_key: SecretStr | None = None
    hf_token: SecretStr | None = None
    wandb_api_key: SecretStr | None = None

    project_root: Path = Path(".")
    data_dir: Path = Path("data")
    data_raw_dir: Path = Path("data/raw")
    data_interim_dir: Path = Path("data/interim")
    data_final_dir: Path = Path("data/final")
    data_embeddings_dir: Path = Path("data/embeddings")
    data_kb_dir: Path = Path("data/kb")
    data_manifests_dir: Path = Path("data/manifests")

    artifacts_dir: Path = Path("artifacts")
    checkpoints_dir: Path = Path("artifacts/checkpoints")
    figures_dir: Path = Path("artifacts/figures")
    tables_dir: Path = Path("artifacts/tables")
    runs_dir: Path = Path("runs")
    reports_dir: Path = Path("reports")
    notebooks_dir: Path = Path("notebooks")
    logs_dir: Path = Path("runs/logs")

    default_device: str = "cuda"
    default_random_seed: int = 42
    default_num_workers: int = 4
    default_log_level: str = "INFO"

    default_timezone: str = "UTC"
    market_timezone: str = "America/New_York"
    exchange_calendar: str = "XNYS"
    market_close_hour: int = 16
    market_close_minute: int = 0

    market_start_date: str = "2006-01-01"
    market_end_date: str | None = None
    twelve_data_interval: str = "1day"
    twelve_data_outputsize: int = 5000
    twelve_data_credits_per_minute: int = 8
    twelve_data_credits_per_day: int = 800

    finnhub_news_chunk_days: int = 30
    news_lookback_days: int = 20
    news_decay_half_life_days: int = 5
    news_use_summary: bool = True

    news_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    hf_home: Path = Path(".cache/huggingface")
    transformers_cache: Path = Path(".cache/huggingface/transformers")
    torch_home: Path = Path(".cache/torch")

    train_batch_size: int = 256
    eval_batch_size: int = 512
    use_mixed_precision: bool = True
    use_pin_memory: bool = True

    enable_wandb: bool = False
    wandb_project: str = "event-state-forecasting"
    wandb_entity: str | None = None


class ResolvedSettings(BaseModel):
    """Fully resolved settings object used throughout the application."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    environment: EnvironmentSettings
    project_paths: ProjectPaths
    config_dir: Path
    env_file: Path | None = None
    configs: dict[str, dict[str, Any]] = Field(default_factory=dict)

    def get_config(self, name: str) -> dict[str, Any]:
        """Return a named YAML config, raising a readable error if missing."""

        if name not in self.configs:
            raise ConfigError(f"Config '{name}' is not loaded.")
        return self.configs[name]

    @property
    def project_config(self) -> dict[str, Any]:
        return self.get_config("project")

    @property
    def data_sources_config(self) -> dict[str, Any]:
        return self.get_config("data_sources")

    @property
    def runtime_config(self) -> dict[str, Any]:
        return self.project_config.get("runtime", {})

    @property
    def environment_config(self) -> dict[str, Any]:
        return self.project_config.get("environment", {})

    def to_safe_dict(self) -> dict[str, Any]:
        """Return a serializable representation without exposing secret values."""

        environment_dump = self.environment.model_dump(mode="json", exclude_none=True)
        for secret_field in (
            "twelve_data_api_key",
            "finnhub_api_key",
            "sec_user_agent",
            "split_events_api_key",
            "hf_token",
            "wandb_api_key",
        ):
            if secret_field in environment_dump:
                environment_dump[secret_field] = "***masked***"

        return {
            "environment": environment_dump,
            "project_paths": self.project_paths.as_dict(),
            "config_dir": str(self.config_dir),
            "env_file": str(self.env_file) if self.env_file else None,
            "configs": self.configs,
        }


def require_env(name: str) -> str:
    """Return a required environment variable or raise a readable error."""

    value = os.getenv(name)
    if value is None or value == "":
        raise ConfigError(
            f"Missing required environment variable '{name}'. Create a local '.env' file or "
            f"export the variable before running the project."
        )
    return value


def optional_env(name: str) -> str | None:
    """Return an optional environment variable if it exists and is non-empty."""

    value = os.getenv(name)
    return value if value not in (None, "") else None


def load_yaml(file_path: str | Path) -> dict[str, Any]:
    """Load a YAML file into a dictionary."""

    path = Path(file_path)
    if not path.exists():
        raise ConfigError(f"YAML config not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}

    if not isinstance(loaded, dict):
        raise ConfigError(f"YAML config must load into a mapping: {path}")

    return _expand_env_placeholders(loaded)


def load_all_yaml_configs(config_dir: str | Path) -> dict[str, dict[str, Any]]:
    """Load all YAML files in a config directory keyed by file stem."""

    directory = Path(config_dir)
    if not directory.exists():
        raise ConfigError(f"Config directory not found: {directory}")

    loaded: dict[str, dict[str, Any]] = {}
    for path in sorted(directory.glob("*.yaml")):
        loaded[path.stem] = load_yaml(path)
    return loaded


def validate_loaded_configs(
    configs: Mapping[str, Mapping[str, Any]],
    required_config_names: set[str] | frozenset[str] | None = None,
) -> None:
    """Validate that the expected configuration files are present and shaped as mappings."""

    required_names = set(required_config_names or EXPECTED_CONFIG_NAMES)
    missing = sorted(required_names.difference(configs.keys()))
    if missing:
        raise ConfigError(
            "Missing required YAML config files: " + ", ".join(f"{name}.yaml" for name in missing)
        )

    for name, config in configs.items():
        if not isinstance(config, Mapping):
            raise ConfigError(f"Loaded config '{name}' must be a mapping, got {type(config).__name__}.")


def load_environment(env_file: str | Path | None = None, project_root: str | Path | None = None) -> tuple[EnvironmentSettings, Path | None]:
    """Load and validate environment settings from a local `.env` file.

    The loader uses the local `.env` file by default when present. It does not
    inspect, print, or persist the secret values; it only validates that the
    required variables exist and can be used at runtime.
    """

    root = find_project_root(project_root)
    if env_file is not None:
        env_path = Path(env_file)
        resolved_env_file = env_path if env_path.is_absolute() else root / env_path
    else:
        resolved_env_file = root / ".env"
    resolved_env_file = resolved_env_file.resolve()

    if resolved_env_file.exists():
        load_dotenv(dotenv_path=resolved_env_file, override=False)
        env_file_result: Path | None = resolved_env_file
    else:
        env_file_result = None

    payload = {
        "twelve_data_api_key": require_env("TWELVE_DATA_API_KEY"),
        "finnhub_api_key": require_env("FINNHUB_API_KEY"),
        "sec_user_agent": require_env("SEC_USER_AGENT"),
        "split_events_api_key": optional_env("SPLIT_EVENTS_API_KEY"),
        "hf_token": optional_env("HF_TOKEN"),
        "wandb_api_key": optional_env("WANDB_API_KEY"),
        "project_root": os.getenv("PROJECT_ROOT", "."),
        "data_dir": os.getenv("DATA_DIR", "data"),
        "data_raw_dir": os.getenv("DATA_RAW_DIR", "data/raw"),
        "data_interim_dir": os.getenv("DATA_INTERIM_DIR", "data/interim"),
        "data_final_dir": os.getenv("DATA_FINAL_DIR", "data/final"),
        "data_embeddings_dir": os.getenv("DATA_EMBEDDINGS_DIR", "data/embeddings"),
        "data_kb_dir": os.getenv("DATA_KB_DIR", "data/kb"),
        "data_manifests_dir": os.getenv("DATA_MANIFESTS_DIR", "data/manifests"),
        "artifacts_dir": os.getenv("ARTIFACTS_DIR", "artifacts"),
        "checkpoints_dir": os.getenv("CHECKPOINTS_DIR", "artifacts/checkpoints"),
        "figures_dir": os.getenv("FIGURES_DIR", "artifacts/figures"),
        "tables_dir": os.getenv("TABLES_DIR", "artifacts/tables"),
        "runs_dir": os.getenv("RUNS_DIR", "runs"),
        "reports_dir": os.getenv("REPORTS_DIR", "reports"),
        "notebooks_dir": os.getenv("NOTEBOOKS_DIR", "notebooks"),
        "logs_dir": os.getenv("LOGS_DIR", "runs/logs"),
        "default_device": os.getenv("DEFAULT_DEVICE", "cuda"),
        "default_random_seed": os.getenv("DEFAULT_RANDOM_SEED", 42),
        "default_num_workers": os.getenv("DEFAULT_NUM_WORKERS", 4),
        "default_log_level": os.getenv("DEFAULT_LOG_LEVEL", "INFO"),
        "default_timezone": os.getenv("DEFAULT_TIMEZONE", "UTC"),
        "market_timezone": os.getenv("MARKET_TIMEZONE", "America/New_York"),
        "exchange_calendar": os.getenv("EXCHANGE_CALENDAR", "XNYS"),
        "market_close_hour": os.getenv("MARKET_CLOSE_HOUR", 16),
        "market_close_minute": os.getenv("MARKET_CLOSE_MINUTE", 0),
        "market_start_date": os.getenv("MARKET_START_DATE", "2006-01-01"),
        "market_end_date": optional_env("MARKET_END_DATE"),
        "twelve_data_interval": os.getenv("TWELVE_DATA_INTERVAL", "1day"),
        "twelve_data_outputsize": os.getenv("TWELVE_DATA_OUTPUTSIZE", 5000),
        "twelve_data_credits_per_minute": os.getenv("TWELVE_DATA_CREDITS_PER_MINUTE", 8),
        "twelve_data_credits_per_day": os.getenv("TWELVE_DATA_CREDITS_PER_DAY", 800),
        "finnhub_news_chunk_days": os.getenv("FINNHUB_NEWS_CHUNK_DAYS", 30),
        "news_lookback_days": os.getenv("NEWS_LOOKBACK_DAYS", 20),
        "news_decay_half_life_days": os.getenv("NEWS_DECAY_HALF_LIFE_DAYS", 5),
        "news_use_summary": os.getenv("NEWS_USE_SUMMARY", "true"),
        "news_embedding_model": os.getenv(
            "NEWS_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        ),
        "hf_home": os.getenv("HF_HOME", ".cache/huggingface"),
        "transformers_cache": os.getenv(
            "TRANSFORMERS_CACHE", ".cache/huggingface/transformers"
        ),
        "torch_home": os.getenv("TORCH_HOME", ".cache/torch"),
        "train_batch_size": os.getenv("TRAIN_BATCH_SIZE", 256),
        "eval_batch_size": os.getenv("EVAL_BATCH_SIZE", 512),
        "use_mixed_precision": os.getenv("USE_MIXED_PRECISION", "true"),
        "use_pin_memory": os.getenv("USE_PIN_MEMORY", "true"),
        "enable_wandb": os.getenv("ENABLE_WANDB", "false"),
        "wandb_project": os.getenv("WANDB_PROJECT", "event-state-forecasting"),
        "wandb_entity": optional_env("WANDB_ENTITY"),
    }

    try:
        environment = EnvironmentSettings.model_validate(payload)
    except ValidationError as exc:
        raise ConfigError(f"Environment validation failed: {exc}") from exc

    return environment, env_file_result


def load_project_settings(
    env_file: str | Path | None = None,
    config_dir: str | Path | None = None,
    project_root: str | Path | None = None,
    create_directories: bool | None = None,
    required_config_names: set[str] | frozenset[str] | None = None,
) -> ResolvedSettings:
    """Load the local environment and YAML configs into one typed settings object."""

    root = find_project_root(project_root)
    environment, resolved_env_file = load_environment(env_file=env_file, project_root=root)
    if config_dir is not None:
        config_path = Path(config_dir)
        resolved_config_dir = config_path if config_path.is_absolute() else root / config_path
    else:
        resolved_config_dir = root / "configs"
    resolved_config_dir = resolved_config_dir.resolve()
    configs = load_all_yaml_configs(resolved_config_dir)

    configured_required_names = configs.get("project", {}).get("runtime", {}).get(
        "required_config_files"
    )
    names_to_validate = required_config_names
    if names_to_validate is None and isinstance(configured_required_names, list):
        names_to_validate = frozenset(str(item) for item in configured_required_names)

    validate_loaded_configs(configs=configs, required_config_names=names_to_validate)

    should_create_directories = create_directories
    if should_create_directories is None:
        runtime_cfg = configs.get("project", {}).get("runtime", {})
        should_create_directories = bool(runtime_cfg.get("create_base_directories_on_load", False))

    project_paths = build_project_paths(
        project_root=root,
        overrides={
            "data_dir": environment.data_dir,
            "data_raw_dir": environment.data_raw_dir,
            "data_interim_dir": environment.data_interim_dir,
            "data_final_dir": environment.data_final_dir,
            "data_embeddings_dir": environment.data_embeddings_dir,
            "data_kb_dir": environment.data_kb_dir,
            "data_manifests_dir": environment.data_manifests_dir,
            "artifacts_dir": environment.artifacts_dir,
            "checkpoints_dir": environment.checkpoints_dir,
            "figures_dir": environment.figures_dir,
            "tables_dir": environment.tables_dir,
            "runs_dir": environment.runs_dir,
            "reports_dir": environment.reports_dir,
            "notebooks_dir": environment.notebooks_dir,
            "logs_dir": environment.logs_dir,
        },
    )

    if should_create_directories:
        project_paths.ensure_base_directories()

    return ResolvedSettings(
        environment=environment,
        project_paths=project_paths,
        config_dir=resolved_config_dir,
        env_file=resolved_env_file,
        configs=configs,
    )


def _expand_env_placeholders(value: Any) -> Any:
    """Recursively expand `${VAR}` references inside YAML-loaded values."""

    if isinstance(value, dict):
        return {key: _expand_env_placeholders(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_env_placeholders(item) for item in value]
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value
