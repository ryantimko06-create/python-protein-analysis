import requests

from search import TIMEOUT_SECONDS, download_pdb


class FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text


class FakeSession:
    """Returns queued responses in order; queued exceptions are raised instead."""

    def __init__(self, queued):
        self.queued = list(queued)
        self.calls = []

    def get(self, url, timeout=None):
        self.calls.append((url, timeout))
        item = self.queued.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def no_sleep(_seconds):
    pass


def test_success_writes_file_and_sets_timeout(tmp_path):
    session = FakeSession([FakeResponse(200, "ATOM      1")])
    assert download_pdb(session, "1ABC", tmp_path, sleep=no_sleep) is True
    assert (tmp_path / "1ABC.pdb").read_text() == "ATOM      1"
    assert session.calls[0][1] == TIMEOUT_SECONDS


def test_404_is_not_retried(tmp_path):
    session = FakeSession([FakeResponse(404)])
    assert download_pdb(session, "XXXX", tmp_path, sleep=no_sleep) is False
    assert len(session.calls) == 1
    assert not (tmp_path / "XXXX.pdb").exists()


def test_500_retries_then_gives_up(tmp_path):
    sleeps = []
    session = FakeSession([FakeResponse(500)] * 3)
    assert download_pdb(session, "1ABC", tmp_path, retries=3, backoff=2.0, sleep=sleeps.append) is False
    assert len(session.calls) == 3
    assert sleeps == [2.0, 2.0]  # no sleep after the final attempt


def test_429_is_retried(tmp_path):
    session = FakeSession([FakeResponse(429), FakeResponse(200, "ok")])
    assert download_pdb(session, "1ABC", tmp_path, sleep=no_sleep) is True
    assert len(session.calls) == 2


def test_network_error_then_success(tmp_path):
    session = FakeSession([requests.exceptions.ConnectionError("reset"), FakeResponse(200, "ok")])
    assert download_pdb(session, "1ABC", tmp_path, sleep=no_sleep) is True
    assert (tmp_path / "1ABC.pdb").read_text() == "ok"
