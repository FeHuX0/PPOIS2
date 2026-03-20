from crimsoland.config_loader import ConfigLoader
from crimsoland.settings import DATA_DIR


def test_music_assets_exist():
    config = ConfigLoader(DATA_DIR / "configs").load_json("audio.json")
    asset_root = DATA_DIR / "assets"

    for track_name in ("menu", "game"):
        asset_path = asset_root / config["music"][track_name]
        assert asset_path.exists(), f"Missing music asset for {track_name}: {asset_path}"
        assert asset_path.stat().st_size > 44