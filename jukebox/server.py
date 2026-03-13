#!/usr/bin/env python3
"""G1 Jukebox — Robot Policy Remote Control Server.

Serves a mobile-friendly web UI for browsing and triggering trained policies
on the Unitree G1 robot. Designed to run on the robot's Jetson (or workstation
for dev). Includes WebSocket for real-time robot state.

Usage:
    python server.py                    # Default port 8080
    python server.py --port 9000        # Custom port
    python server.py --mock             # Mock robot state for dev
"""

import asyncio
import json
import os
import signal
import sys
import time
from pathlib import Path

try:
    import websockets
    from websockets.asyncio.server import serve as ws_serve
except ImportError:
    print("Install websockets: pip install websockets")
    sys.exit(1)

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from functools import partial
from socketserver import ThreadingTCPServer
import threading

PORT = 8080
STATIC_DIR = Path(__file__).parent
CMD_FILE = Path("/tmp/robojudo_gui_commands.json")

# Robot state — updated by WebSocket broadcast
robot_state = {
    "status": "idle",          # idle | loading | running | stopped | error
    "policy": None,            # Currently loaded policy ID
    "message": "Ready",
    "timestamp": 0,
}

ws_clients = set()
mock_mode = False


def write_command(cmd, **kwargs):
    """Write a command to the RoboJuDo virtual controller JSON file."""
    payload = {"command": cmd, "timestamp": time.time(), **kwargs}
    CMD_FILE.write_text(json.dumps(payload))
    return payload


async def handle_ws(websocket):
    """Handle a WebSocket connection."""
    ws_clients.add(websocket)
    try:
        # Send current state immediately
        await websocket.send(json.dumps({"type": "state", **robot_state}))

        async for raw in websocket:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
                continue

            cmd = msg.get("cmd")
            if cmd == "load":
                policy_id = msg.get("policy")
                if not policy_id:
                    await websocket.send(json.dumps({"type": "error", "message": "Missing policy ID"}))
                    continue
                robot_state["status"] = "loading"
                robot_state["policy"] = policy_id
                robot_state["message"] = f"Loading {policy_id}..."
                robot_state["timestamp"] = time.time()
                write_command("[POLICY_SWITCH]", policy=policy_id)
                await broadcast_state()

                if mock_mode:
                    await asyncio.sleep(1.5)
                    robot_state["status"] = "stopped"
                    robot_state["message"] = f"{policy_id} loaded"
                    await broadcast_state()

            elif cmd == "start":
                if robot_state["policy"]:
                    robot_state["status"] = "running"
                    robot_state["message"] = f"Playing {robot_state['policy']}"
                    robot_state["timestamp"] = time.time()
                    write_command("[MOTION_FADE_IN]")
                    await broadcast_state()
                else:
                    await websocket.send(json.dumps({"type": "error", "message": "No policy loaded"}))

            elif cmd == "stop":
                robot_state["status"] = "stopped"
                robot_state["message"] = f"{robot_state['policy']} stopped" if robot_state["policy"] else "Stopped"
                robot_state["timestamp"] = time.time()
                write_command("[MOTION_FADE_OUT]")
                await broadcast_state()

            elif cmd == "ping":
                await websocket.send(json.dumps({"type": "pong"}))

            else:
                await websocket.send(json.dumps({"type": "error", "message": f"Unknown command: {cmd}"}))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        ws_clients.discard(websocket)


async def broadcast_state():
    """Send current robot state to all connected clients."""
    if not ws_clients:
        return
    msg = json.dumps({"type": "state", **robot_state})
    await asyncio.gather(
        *[client.send(msg) for client in ws_clients],
        return_exceptions=True,
    )


class StaticHandler(SimpleHTTPRequestHandler):
    """Serve static files from the jukebox directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format, *args):
        pass  # Quiet


def run_http(port):
    """Run the HTTP server for static files on port+1."""
    ThreadingTCPServer.allow_reuse_address = True
    httpd = ThreadingTCPServer(("0.0.0.0", port), StaticHandler)
    httpd.serve_forever()


async def main():
    global mock_mode

    port = PORT
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--port" and i + 2 < len(sys.argv):
            port = int(sys.argv[i + 2])
        if arg == "--mock":
            mock_mode = True

    # Start HTTP server for static files on port+1
    http_port = port + 1
    http_thread = threading.Thread(target=run_http, args=(http_port,), daemon=True)
    http_thread.start()

    # Start WebSocket server
    stop = asyncio.get_event_loop().create_future()

    def shutdown(sig):
        stop.set_result(None)

    for sig in (signal.SIGTERM, signal.SIGINT):
        asyncio.get_event_loop().add_signal_handler(sig, shutdown, sig)

    async with ws_serve(handle_ws, "0.0.0.0", port):
        mode = " (mock)" if mock_mode else ""
        print(f"G1 Jukebox{mode}")
        print(f"  UI:        http://0.0.0.0:{http_port}")
        print(f"  WebSocket: ws://0.0.0.0:{port}")
        print(f"  Static:    {STATIC_DIR}")
        await stop


if __name__ == "__main__":
    asyncio.run(main())
