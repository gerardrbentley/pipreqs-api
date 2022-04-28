import asyncio
import functools
import tempfile

from cachetools import TTLCache
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.config import get_logger

log = get_logger()

router = APIRouter()


async def _run(cmd):
    log.debug(f"Running {cmd!r}")
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    log.debug(f"[{cmd!r} exited with {proc.returncode}]")
    if stdout:
        log.debug(f"[stdout]\n{stdout.decode()}")
    if stderr:
        log.debug(f"[stderr]\n{stderr.decode()}")
    return stdout, stderr, proc.returncode


async def fetch_code(code_url: str, destination_dir: str) -> None:
    log.debug(f"Fetching from url {code_url!r}")
    clone_cmd = f"git clone --depth 1 {code_url!r} {destination_dir!r}"
    stdout, stderr, returncode = await _run(clone_cmd)
    if returncode != 0:
        message = f"Could not clone the code from {code_url!r}!"
        log.exception(message, stack_info=True)
        raise HTTPException(status_code=400, detail=message)


async def run_pipreqs(code_url: str, dir_path: str):
    log.debug(f"Running pipreqs on temporary directory {dir_path!r}")
    clone_cmd = f"pipreqs --print {dir_path}"
    stdout, stderr, returncode = await _run(clone_cmd)
    if returncode != 0:
        message = f"Could not run pipreqs on the code from {code_url!r}!"
        log.exception(message, stack_info=True)
        raise HTTPException(status_code=500, detail=message)
    log.debug(stdout)
    return stdout


async def pipreqs_from_url(code_url: str) -> str:
    with tempfile.TemporaryDirectory() as dir_path:
        await fetch_code(code_url, dir_path)
        pipreqs_output = await run_pipreqs(code_url, dir_path)
    return pipreqs_output


class RequirementsCache(TTLCache):
    def __missing__(self, code_url):
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
    return await requirements_cache[code_url]
