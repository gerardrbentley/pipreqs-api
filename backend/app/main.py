import logging

import uvicorn
from fastapi import FastAPI

from app import config, healthcheck, pipreqsapi, github_bot

log = config.get_logger()
log.setLevel(logging.DEBUG)


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(healthcheck.router)
    application.include_router(pipreqsapi.router)
    application.include_router(github_bot.router)

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
