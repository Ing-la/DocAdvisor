#!/usr/bin/env python3
"""DocAdvisor FastAPI server entrypoint."""

import uvicorn


def main() -> None:
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
