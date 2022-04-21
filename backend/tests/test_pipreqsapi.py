
import pytest
from fastapi.exceptions import HTTPException

from app import pipreqsapi
from app.pipreqsapi import _run, fetch_code, run_pipreqs

MOCK_REQS = """fastapi==0.75.1
gunicorn==20.1.0
pipreqs==0.4.11
uvicorn==0.17.6"""


@pytest.mark.asyncio
class TestPipreqsApi:
    """Test backend logic that handles cloning repos and running pipreqs"""

    async def test_async_run_succeeds(self):
        stdout, stderr, resultcode = await _run("ls")
        assert resultcode == 0

    async def test_async_run_fails_bad_command(self):
        stdout, stderr, resultcode = await _run("lz")
        assert resultcode == 127

    async def test_fetch_code_succeeds(self, monkeypatch):
        async def fake_run_success(*args):
            return None, None, 0

        monkeypatch.setattr(pipreqsapi, "_run", fake_run_success)
        res = await fetch_code("good_clone_url", "none")
        assert res is None

    async def test_fetch_code_fails_bad_repo(self):
        with pytest.raises(HTTPException) as exception:
            await fetch_code("bad_clone_url", "none")
        result = exception.value
        assert result.status_code == 400
        assert result.detail == "Could not clone the code from 'bad_clone_url'!"

    async def test_run_pipreqs_succeeds(self, monkeypatch):
        async def fake_run_success(*args):
            return MOCK_REQS, None, 0

        monkeypatch.setattr(pipreqsapi, "_run", fake_run_success)
        res = await run_pipreqs("good_clone_url", "none")
        assert res == MOCK_REQS

    async def test_run_pipreqs_fails_bad_pipreqs(self, monkeypatch):
        async def fake_run_fail(*args):
            return None, "ERROR", 1

        monkeypatch.setattr(pipreqsapi, "_run", fake_run_fail)
        with pytest.raises(HTTPException) as exception:
            await run_pipreqs("bad_pipreqs_url", "none")
        result = exception.value
        assert result.status_code == 500
        assert (
            result.detail == "Could not run pipreqs on the code from 'bad_pipreqs_url'!"
        )

    async def test_pipreqs_endpoint_succeeds(self, test_app, monkeypatch):
        async def fake_run_pipreqs_success(*args):
            return MOCK_REQS

        async def fake_fetch_success(*args):
            return None

        monkeypatch.setattr(pipreqsapi, "run_pipreqs", fake_run_pipreqs_success)
        monkeypatch.setattr(pipreqsapi, "fetch_code", fake_fetch_success)
        response = test_app.get("/pipreqs", params={"code_url": "good_clone_url"})
        assert response.status_code == 200
        assert response.text == MOCK_REQS

    async def test_pipreqs_endpoint_fails_bad_repo(self, test_app):
        response = test_app.get("/pipreqs", params={"code_url": "bad_clone_url"})
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Could not clone the code from 'bad_clone_url'!"
        )

    async def test_pipreqs_endpoint_fails_bad_pipreqs(self, test_app, monkeypatch):
        async def fake_run_fail(*args):
            return None, "ERROR", 1

        async def fake_fetch_success(*args):
            return None

        monkeypatch.setattr(pipreqsapi, "_run", fake_run_fail)
        monkeypatch.setattr(pipreqsapi, "fetch_code", fake_fetch_success)
        response = test_app.get("/pipreqs", params={"code_url": "bad_pipreqs_url"})

        assert response.status_code == 500
        assert (
            response.json()["detail"]
            == "Could not run pipreqs on the code from 'bad_pipreqs_url'!"
        )
