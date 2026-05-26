import pytest


@pytest.fixture(autouse=True)
def isolate_home(monkeypatch, tmp_path):
    """Keep tests from reading or writing the user's real home/config."""
    home = tmp_path / "home"
    yt2mp3_home = tmp_path / "yt2mp3-home"
    home.mkdir()
    yt2mp3_home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("YT2MP3_HOME", str(yt2mp3_home))
