from backend.models import *
from backend.db import get_db
import datetime
import os


def submit_fault(
    source: list[str],
    message: str,
    code: int,
    owner: str,
    public: bool,
    log_file_path: str,
):
    db = get_db()
    f = Fault(
        time=datetime.datetime.utcnow(),
        source=source,
        message=message,
        code=code,
        owner=owner,
        public=public,
    )
    db.add(f)
    db.commit()
    log_content = open(log_file_path, "r").read()
    log = FaultLog(fault_id=f.id, log_content=log_content)
    db.add(log)
    db.commit()
    db.close()


def generate_log_path(source: str, id: int) -> str:
    return os.path.join(os.getenv("LOG_PATH"), f"{source}_task_{id}.log")
