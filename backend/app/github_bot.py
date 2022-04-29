import os

import gidgethub.httpx
import httpx
from fastapi import APIRouter, Response
from gidgethub import routing, sansio

from app.config import get_logger
from app.pipreqsapi import get_requirements_cache

log = get_logger()

router = APIRouter()


gh_router = routing.Router()


@gh_router.register("push")
async def push_to_repo_event(event, gh, *args, **kwargs):
    """
    Whenever a push is made, check the requirements matches pipreqs output; else open an issue.
    """
    url = event.data["repository"]["url"]
    pusher = event.data["pusher"]["name"]

    log.info(
        f"Recent push by @{pusher} to {url}! Checking if requirements.txt is in line."
    )
    requirements_cache = get_requirements_cache()
    requirements, old_requirements = await requirements_cache[url]
    if requirements == old_requirements:
        log.debug(f"Requirements satisfied in repo {url}")
    else:
        issues_url = event.data["repository"]["issues_url"]
        payload = {
            "title": "Check dependencies",
            "body": f"Please confirm dependencies are satisfied.\n\nRequirements from pipreqs:\n```txt\n{requirements_cache}\n```\n\nRequirements found in push:\n```txt\n{old_requirements}\n```",
            "assignees": [pusher],
        }
        log.debug(f"Posting {payload} to {issues_url!r}")
        await gh.post(issues_url, data=payload)


@router.post("/", response_class=Response)
async def main(request):

    body = await request.read()

    secret = os.environ.get("GITHUB_SECRET")
    oauth_token = os.environ.get("GITHUB_TOKEN")

    event = sansio.Event.from_http(request.headers, body, secret=secret)
    async with httpx.AsyncClient() as client:
        gh = gidgethub.httpx.GitHubAPI(
            client, "gerardrbentley", oauth_token=oauth_token
        )
        await router.dispatch(event, gh)
    return Response(status_code=200)