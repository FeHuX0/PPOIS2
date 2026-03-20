from __future__ import annotations

from pathlib import Path

from crimsoland.app import CrimsolandApp


def main(
    config_dir: str | Path | None = None,
    highscores_file: str | Path | None = None,
    headless: bool = False,
    max_frames: int | None = None,
) -> int:
    app = CrimsolandApp(
        config_dir=config_dir,
        highscores_file=highscores_file,
        headless=headless,
    )
    try:
        return app.run(max_frames=max_frames)
    finally:
        app.shutdown()
