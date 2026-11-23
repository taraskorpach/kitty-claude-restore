from kcr.model import Session


def session(sid: str, cwd: str | None = None) -> Session:
    return Session(session_id=sid, cwd=cwd or f"/work/{sid}", name=sid, started_at=0)
