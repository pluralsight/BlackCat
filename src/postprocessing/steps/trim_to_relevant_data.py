from typing import Dict, Any

from postprocessing.steps.post_process_step import PostProcessStep


class PostStepFlattenRelevantData(PostProcessStep):
    """
    A post-processing step for removing irrelevant or redundant fields from the GitHub API response.
    It also flattens the structure so items like dismisser are on the same level as vulnerability details.
    """
    def run(self, run_id: int, org: str, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        new_data = data.get('node').get('securityVulnerability')
        # Get metadata fields
        dismisser = data.get('node').get('dismisser')
        dismissed_at = data.get('node').get('dismissedAt')
        dismissed_reason = data.get('node').get('dismissReason')
        manifest_file = data.get('node').get('vulnerableManifestPath')

        # Push metadata into vuln object
        new_data['dismisser'] = dismisser
        new_data['dismissed_at'] = dismissed_at
        new_data['dismissed_reason'] = dismissed_reason
        new_data['manifest_file'] = manifest_file

        # Push our metadata, repo url and run id
        new_data['run_id'] = run_id
        new_data['repo_url'] = url
        return new_data
