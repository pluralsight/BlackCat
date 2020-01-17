from blackcat import BlackCatPostProcessor, PostStepFlattenRelevantData


class TestPostProcessor(object):
    TEST_OBJ = {
        'node': {
            'securityVulnerability': {'test-field': True},
            'dismisser': 'Nobody',
            'dismissedAt': 'Never',
            'dismissReason': 'None of your business',
            'vulnerableManifestPath': 'package.json'
        }
    }

    def test_post_processor(self):
        BlackCatPostProcessor.add_post_step(PostStepFlattenRelevantData())
        out = BlackCatPostProcessor.run(1, 'test_org', 'https://www.google.com', self.TEST_OBJ)
        assert out == {
            'test-field': True,
            'dismisser': 'Nobody',
            'dismissed_at': 'Never',
            'dismissed_reason': 'None of your business',
            'manifest_file': 'package.json',
            'run_id': 1,
            'repo_url': 'https://www.google.com'
        }
