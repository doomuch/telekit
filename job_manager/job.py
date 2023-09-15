import os
import uuid
from abc import ABC


class BaseJob(ABC):
    def __init__(self, client_handler, message):
        self._id = str(uuid.uuid4())
        self._client_handler = client_handler
        self._message = message

    def _create_job_directory(self) -> str:
        job_directory = "jobs/" + self._id
        if not os.path.exists(job_directory):
            os.makedirs(job_directory)

        return job_directory

