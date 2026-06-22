#!/usr/bin/env python3
"""
Temporarily host a static HTML/CSS/JS site through a Cloudflare Quick Tunnel.

Usage:
  python static_cloudflare_host.py
  python static_cloudflare_host.py --dir ./edge-questionnaire-form --port 8000

Requirements:
  - Python 3.8+
  - cloudflared installed and available on PATH

Stop with Ctrl+C.
"""

import argparse
import functools
import http.server
import os
import re
import shutil
import signal
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

TUNNEL_URL_RE = re.compile(r"https://[-a-z0-9]+\.trycloudflare\.com")


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def validate_site_dir(site_dir: Path) -> Path:
    site_dir = site_dir.expanduser().resolve()
    if not site_dir.exists() or not site_dir.is_dir():
        raise FileNotFoundError(f"Site directory does not exist: {site_dir}")

    index_file = site_dir / "index.html"
    if not index_file.exists():
        print(
            f"Warning: no index.html found in {site_dir}. "
            "The server will still start, but the root URL may show a directory listing.",
            file=sys.stderr,
        )

    return site_dir


def ensure_cloudflared_available() -> None:
    if shutil.which("cloudflared") is None:
        raise RuntimeError(
            "cloudflared was not found on PATH. Install it first, then rerun this script."
        )


def start_static_server(site_dir: Path, host: str, port: int) -> tuple[ReusableTCPServer, threading.Thread]:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(site_dir))
    httpd = ReusableTCPServer((host, port), handler)

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    return httpd, thread


def stream_cloudflared_output(process: subprocess.Popen, url_holder: dict) -> None:
    if process.stdout is None:
        return

    for line in process.stdout:
        line = line.rstrip()
        print(f"[cloudflared] {line}")

        match = TUNNEL_URL_RE.search(line)
        if match and not url_holder.get("url"):
            url_holder["url"] = match.group(0)
            print("\nPublic URL:")
            print(f"  {url_holder['url']}\n")


def start_cloudflare_tunnel(local_url: str) -> tuple[subprocess.Popen, dict, threading.Thread]:
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", local_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    url_holder: dict[str, Optional[str]] = {"url": None}
    thread = threading.Thread(
        target=stream_cloudflared_output,
        args=(process, url_holder),
        daemon=True,
    )
    thread.start()

    return process, url_holder, thread


def stop_process(process: Optional[subprocess.Popen], name: str) -> None:
    if process is None or process.poll() is not None:
        return

    print(f"Stopping {name}...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Serve a static site locally and expose it through a Cloudflare Quick Tunnel."
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="Directory containing index.html, styles.css, script.js, etc. Default: current directory.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Local bind host. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=8000, help="Local server port. Default: 8000")
    parser.add_argument(
        "--no-open-browser",
        action="store_true",
        help="Do not attempt to open the local URL in your default browser.",
    )
    args = parser.parse_args()

    httpd = None
    tunnel_process = None

    try:
        site_dir = validate_site_dir(Path(args.dir))
        ensure_cloudflared_available()

        local_url = f"http://{args.host}:{args.port}"

        print(f"Serving directory: {site_dir}")
        print(f"Local URL:        {local_url}")
        print("Starting local static server...")

        httpd, _server_thread = start_static_server(site_dir, args.host, args.port)

        print("Starting Cloudflare Quick Tunnel...")
        tunnel_process, url_holder, _tunnel_thread = start_cloudflare_tunnel(local_url)

        print("Waiting for Cloudflare public URL...")
        print("Press Ctrl+C to stop the tunnel and local server.\n")

        if not args.no_open_browser:
            try:
                import webbrowser

                webbrowser.open(local_url)
            except Exception:
                pass

        while True:
            if tunnel_process.poll() is not None:
                print("cloudflared stopped unexpectedly.", file=sys.stderr)
                return tunnel_process.returncode or 1
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nShutdown requested.")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        stop_process(tunnel_process, "Cloudflare tunnel")
        if httpd is not None:
            print("Stopping local static server...")
            httpd.shutdown()
            httpd.server_close()
        print("Done.")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    raise SystemExit(main())
