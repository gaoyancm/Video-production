"""Utility helpers for storing uploaded assets."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional, Tuple

from fastapi import UploadFile

from ..core.config import AppSettings, get_settings
from ..utils.identifiers import new_job_id


class StorageService:
    """Persist uploads to the configured storage directory."""

    def __init__(self, settings: Optional[AppSettings] = None) -> None:
        self.settings = settings or get_settings()

    def persist_upload(self, upload: UploadFile, job_id: Optional[str] = None) -> Tuple[str, Path]:
        """Save an incoming file under storage_dir and return identifiers."""
        job_id = job_id or new_job_id("upload")
        target_dir = Path(self.settings.storage_dir) / job_id
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / upload.filename

        with target_path.open("wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)
        upload.file.close()

        return job_id, target_path
