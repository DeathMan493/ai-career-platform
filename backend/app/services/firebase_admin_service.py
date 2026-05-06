from __future__ import annotations

import json
from pathlib import Path
import logging

import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_firebase_app():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    options = {}
    if settings.firebase_project_id:
        options["projectId"] = settings.firebase_project_id

    if settings.firebase_service_account_json:
        service_account = json.loads(settings.firebase_service_account_json)
        logger.info("Initializing Firebase Admin with service account from environment")
        cred = credentials.Certificate(service_account)
        return firebase_admin.initialize_app(cred, options=options or None)

    if settings.firebase_credentials_path:
        raw_path = Path(settings.firebase_credentials_path)
        if raw_path.is_absolute():
            credentials_path = raw_path
        else:
            backend_root = Path(__file__).resolve().parents[2]
            project_root = backend_root.parent
            candidates = [
                raw_path,
                backend_root / raw_path,
                project_root / raw_path,
            ]
            credentials_path = next((candidate for candidate in candidates if candidate.exists()), backend_root / raw_path)

        logger.info("Initializing Firebase Admin with credentials file: %s", credentials_path)
        cred = credentials.Certificate(str(credentials_path))
        return firebase_admin.initialize_app(cred, options=options or None)

    return firebase_admin.initialize_app(options=options or None)


def verify_firebase_token(id_token: str) -> dict:
    app = get_firebase_app()
    return auth.verify_id_token(
        id_token,
        app=app,
        clock_skew_seconds=settings.firebase_clock_skew_seconds,
    )
