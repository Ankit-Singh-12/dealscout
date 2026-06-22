import os

def _read_bool_env(name: str, default: bool = False) -> bool:
    """Read a boolean-ish environment variable (1/true/yes/on -> True)."""
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# Source of truth for demo mode.
DEMO_MODE = _read_bool_env("DEALSCOUT_DEMO_MODE", default=False)