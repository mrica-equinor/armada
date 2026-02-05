import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import requests
from loguru import logger
from requests import Response

from robotics_integration_tests.settings.settings import settings
from robotics_integration_tests.utilities.authentication import (
    retrieve_access_token_for_integration_tests_app,
)


def _add_headers() -> Dict[str, str]:
    access_token: str = retrieve_access_token_for_integration_tests_app(
        settings.SARA_AZURE_CLIENT_ID
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def _list_database_entries(backend_url: str, request_path: str) -> List[Dict]:
    logger.info(f"Listing database entries for path: {backend_url}/{request_path}")
    response: Response = requests.get(
        f"{backend_url}/{request_path}", headers=_add_headers()
    )
    response.raise_for_status()
    return response.json()


def wait_for_sara_to_be_responsive(sara_url: str, timeout: int = 60) -> None:
    start_time: datetime = datetime.now()
    while True:
        if datetime.now() - start_time > timedelta(seconds=timeout):
            raise RuntimeError(
                f"Sara was not responsive within the given timeout {timeout} seconds"
            )

        try:
            analysis_mapping: List[Dict] = _list_database_entries(
                backend_url=sara_url, request_path="AnalysisMapping"
            )
        except Exception as e:
            logger.warning(
                f"Backend is not responsive yet, will retry until timeout... Exception: {e}"
            )
            time.sleep(1)
            continue

        if len(analysis_mapping) >= 0:
            logger.info("Sara is responsive")
            return
