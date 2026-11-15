"""Credentials for the live tests, which talk to the real services.

From the environment first. Failing that, the maintainer's own secret store,
if it happens to be importable (it is never in this repository). With neither,
the test prints SKIP and exits 0, so a checkout without keys stays green.
"""
import os
import sys


def key_or_skip(test, env_names, store_names):
    vals = [os.environ.get(n, "").strip() for n in env_names]
    if all(vals):
        return vals
    try:
        from secrets_store import get_secret  # noqa: PLC0415
        vals = [get_secret(n) for n in store_names]
        if all(vals):
            return vals
    except Exception:  # noqa: BLE001
        pass
    print(f"SKIP {test}: set {' and '.join(env_names)} to run it against the live service")
    sys.exit(0)
