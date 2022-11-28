import os

from pathlib import Path


def read_env_file(file_path: str | bytes | Path | os.PathLike) -> dict[str, str]:
    """
    Read an .env file and return a dict with the contents.
    """
    env = {}
    with open(file_path) as file:
        for line in file:
            # skip comments and empty lines
            if line.startswith('#') or line.strip() == '':
                continue

            # split on = and assert wellformed line by checking length
            parts = line.split('=')
            assert len(parts) == 2, f"Malformed line in env-file at {file_path}"

            # add stripped parts to our mapping, newer overwrite older entries
            env[parts[0].strip()] = parts[1].strip()

    return env
