"""Run the API server: `python -m app` (or the packaged binary).

    python -m app --host 0.0.0.0 --port 8000

The packaged single-file binaries (see GitHub Releases) embed the feed
registry; ingested city data lands in ./data (override: TRANSIT_DATA_DIR).
"""

from __future__ import annotations

import argparse


def main() -> None:
    p = argparse.ArgumentParser(prog="public-transit-api", description=__doc__)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    args = p.parse_args()

    import uvicorn

    from app.main import app

    # ASCII only: Windows consoles default to cp1252 and crash on fancy arrows.
    print(f"City Transit API -> http://{args.host}:{args.port}/docs")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
