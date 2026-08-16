"""HTTP and WebSocket adapters for DryvApiServer."""

from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute

from dryv_api.server import DryvApiServer

from .http import (
    cancel_build,
    create_build,
    delete_build,
    get_build,
    get_bundle,
    get_plan,
    preflight_build,
    render_build,
)
from .websocket import build_events


def create_app(server: DryvApiServer | None = None) -> Starlette:
    app = Starlette(
        routes=[
            Route("/v1/builds", create_build, methods=["POST"]),
            Route("/v1/builds/{build_id}", get_build, methods=["GET"]),
            Route("/v1/builds/{build_id}", delete_build, methods=["DELETE"]),
            Route("/v1/builds/{build_id}/plan", get_plan, methods=["GET"]),
            Route("/v1/builds/{build_id}/preflight", preflight_build, methods=["POST"]),
            Route("/v1/builds/{build_id}/render", render_build, methods=["POST"]),
            Route("/v1/builds/{build_id}/cancel", cancel_build, methods=["POST"]),
            Route("/v1/builds/{build_id}/bundle", get_bundle, methods=["GET"]),
            WebSocketRoute("/v1/builds/{build_id}/events", build_events),
        ]
    )
    app.state.dryv_server = server or DryvApiServer()
    return app


__all__ = ["create_app"]
