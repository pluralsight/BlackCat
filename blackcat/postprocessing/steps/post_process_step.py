from abc import ABC, abstractmethod
from typing import Dict, Any


class PostProcessStep(ABC):
    @abstractmethod
    def run(self, run_id: int, org: str, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
         Executes this post-processing step.
        :param run_id: The current run id (may just be time)
        :param org: The current organization
        :param url: The URL of the repository being scanned
        :param data: The data found
        :return: If the data was modified, this will return that modified data, otherwise it will return the
                 original value
        """
        pass
