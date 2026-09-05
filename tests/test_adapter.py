import json

import requests
import responses

from hyperion_flaresolverr import FlareSolverrAdapter, FlareSolverrError

ENDPOINT = "http://localhost:8191/v1"
TARGET = "https://protected.example"


def make_session():
    adapter = FlareSolverrAdapter(endpoint=ENDPOINT)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session, adapter


def flaresolverr_rpc(
    solve_calls, *, response_html="<html>browser</html>", user_agent="BrowserUA/1.0"
):
    def callback(request):
        payload = json.loads(request.body)
        cmd = payload["cmd"]
        if cmd == "request.get":
            solve_calls.append(payload)
            solution = {
                "status": 200,
                "headers": {},
                "cookies": [{"name": "cf_clearance", "value": "granted"}],
                "userAgent": user_agent,
                "response": response_html,
                "url": payload["url"],
            }
            return (200, {}, json.dumps({"status": "ok", "solution": solution}))
        return (200, {}, json.dumps({"status": "ok"}))

    return callback


@responses.activate
def test_unchallenged_request_never_calls_flaresolverr():
    solve_calls = []
    responses.add(responses.GET, TARGET + "/", status=200, body="plain page")
    responses.add_callback(responses.POST, ENDPOINT, callback=flaresolverr_rpc(solve_calls))

    session, adapter = make_session()
    resp = session.get(TARGET + "/")

    assert resp.status_code == 200
    assert resp.text == "plain page"
    assert solve_calls == []
    adapter.close()


@responses.activate
def test_challenge_triggers_one_solve_and_one_retry():
    solve_calls = []
    responses.add(
        responses.GET, TARGET + "/", status=503,
        headers={"server": "cloudflare"}, body="Just a moment...",
    )
    responses.add(responses.GET, TARGET + "/", status=200, body="cleared page")
    responses.add_callback(responses.POST, ENDPOINT, callback=flaresolverr_rpc(solve_calls))

    session, adapter = make_session()
    resp = session.get(TARGET + "/")

    assert resp.status_code == 200
    assert resp.text == "cleared page"
    assert len(solve_calls) == 1
    adapter.close()


@responses.activate
def test_harvested_credentials_reused_without_second_solve():
    solve_calls = []
    responses.add(
        responses.GET, TARGET + "/", status=503,
        headers={"cf-mitigated": "challenge"}, body="",
    )
    responses.add(responses.GET, TARGET + "/", status=200, body="cleared")
    responses.add(responses.GET, TARGET + "/", status=200, body="second visit")
    responses.add_callback(responses.POST, ENDPOINT, callback=flaresolverr_rpc(solve_calls))

    session, adapter = make_session()
    session.get(TARGET + "/")
    second = session.get(TARGET + "/")

    assert second.text == "second visit"
    assert len(solve_calls) == 1

    reused = responses.calls[-1].request
    assert reused.headers["User-Agent"] == "BrowserUA/1.0"
    assert "cf_clearance=granted" in reused.headers["Cookie"]
    adapter.close()


@responses.activate
def test_persistent_challenge_returns_browser_html():
    solve_calls = []
    responses.add(
        responses.GET, TARGET + "/", status=503,
        headers={"cf-mitigated": "challenge"}, body="Just a moment...",
    )
    responses.add(
        responses.GET, TARGET + "/", status=503,
        headers={"cf-mitigated": "challenge"}, body="Just a moment...",
    )
    responses.add_callback(
        responses.POST, ENDPOINT,
        callback=flaresolverr_rpc(solve_calls, response_html="<html>rendered by browser</html>"),
    )

    session, adapter = make_session()
    resp = session.get(TARGET + "/")

    assert resp.status_code == 200
    assert resp.text == "<html>rendered by browser</html>"
    assert len(solve_calls) == 1
    adapter.close()


@responses.activate
def test_flaresolverr_error_status_raises():
    responses.add(
        responses.GET, TARGET + "/", status=503,
        headers={"cf-mitigated": "challenge"}, body="",
    )
    responses.add(
        responses.POST, ENDPOINT,
        json={"status": "error", "message": "no browser available"},
    )

    session, adapter = make_session()
    try:
        session.get(TARGET + "/")
        raise AssertionError("expected FlareSolverrError")
    except FlareSolverrError as exc:
        assert "no browser available" in str(exc)
    adapter.close()
