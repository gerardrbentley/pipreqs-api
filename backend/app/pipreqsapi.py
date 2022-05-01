import asyncio
import functools
import tempfile
from pathlib import Path
from typing import Any, Coroutine, Tuple

from cachetools import TTLCache
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.config import get_logger

log = get_logger()

router = APIRouter()


async def _run(cmd: str) -> Tuple[str, str, int]:
    log.debug(f"Running {cmd!r}")
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd.split(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as e:
        log.exception(e, stack_info=True)
        return "", str(e), 1
    stdout, stderr = await proc.communicate()

    log.debug(f"[{cmd!r} exited with {proc.returncode}]")
    if stdout:
        log.debug(f"[stdout]\n{stdout.decode()}")
    if stderr:
        log.debug(f"[stderr]\n{stderr.decode()}")
    return stdout.decode(), stderr.decode(), proc.returncode


async def fetch_code(
    code_url: str, destination_dir: str, requirements_path: str = "requirements.txt"
) -> str:
    log.debug(f"Fetching from url {code_url!r}")
    clone_cmd = f"git clone --depth 1 {code_url} {destination_dir}"
    stdout, stderr, returncode = await _run(clone_cmd)
    if returncode != 0:
        message = f"Could not clone the code from {code_url!r}!"
        log.exception(message, stack_info=True)
        raise HTTPException(status_code=400, detail=message)
    old_requirements = Path(destination_dir) / requirements_path
    if old_requirements.is_file():
        log.debug(f"Reading existing requirements from {str(old_requirements)!r}")
        return old_requirements.read_text()
    else:
        log.debug(f"No existing requirements at {str(old_requirements)!r}")
        return ""


async def run_pipreqs(code_url: str, dir_path: str) -> str:
    log.debug(f"Running pipreqs on temporary directory {dir_path!r}")
    clone_cmd = f"pipreqs --print {dir_path}"
    stdout, stderr, returncode = await _run(clone_cmd)
    if returncode != 0:
        message = f"Could not run pipreqs on the code from {code_url!r}!"
        log.exception(message, stack_info=True)
        raise HTTPException(status_code=500, detail=message)
    log.debug(stdout)
    return stdout


async def pipreqs_from_url(code_url: str) -> Tuple[str, str]:
    with tempfile.TemporaryDirectory() as dir_path:
        old_requirements = await fetch_code(code_url, dir_path)
        pipreqs_output = await run_pipreqs(code_url, dir_path)
    return pipreqs_output, old_requirements


class RequirementsCache(TTLCache):
    def __missing__(self, code_url: str) -> Coroutine[Any, Any, Tuple[str, str]]:
        future = asyncio.create_task(pipreqs_from_url(code_url))
        self[code_url] = future
        return future


@functools.lru_cache(maxsize=1)
def get_requirements_cache() -> RequirementsCache:
    requirements_cache = RequirementsCache(1024, 300)
    return requirements_cache


@router.get("/pipreqs", response_class=PlainTextResponse)
async def pipreqs_endpoint(code_url: str):
    requirements_cache = get_requirements_cache()
    requirements, old_requirements = await requirements_cache[code_url]
    return requirements
