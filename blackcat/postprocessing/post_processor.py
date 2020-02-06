from typing import Dict, Any

from blackcat.postprocessing.steps.post_process_step import PostProcessStep


class BlackCatPostProcessor(object):
    __STEPS = []
    @classmethod
    def add_post_step(cls, step: PostProcessStep):
        cls.__STEPS.append(step)

    @classmethod
    def run(cls, run_id: int, org: str, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
         Executes all post-processing steps.
        :param run_id: The current run id (may just be time)
        :param org: The current organization
        :param url: The URL of the repository being scanned
        :param data: The data found
        :return: If the data was modified, this will return that modified data, otherwise it will return the
                 original value
        """
        for step in cls.__STEPS:
            data = step.run(run_id, org, url, data)
        return data
