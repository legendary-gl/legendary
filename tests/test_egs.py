import unittest
from unittest.mock import Mock

import requests

from legendary.api.egs import EPCAPI


class GetGameAssetsTest(unittest.TestCase):
    def test_returns_assets_from_launcher_endpoint(self):
        api = EPCAPI()
        api.session = Mock()
        response = Mock()
        response.json.return_value = [{'appName': 'Game'}]
        api.session.get.return_value = response

        self.assertEqual(
            [{'appName': 'Game'}], api.get_game_assets(platform='Mac', label='Test')
        )
        api.session.get.assert_called_once_with(
            f'https://{api._launcher_host}/launcher/api/public/assets/Mac',
            params={'label': 'Test'},
            timeout=api.request_timeout,
        )

    def test_does_not_fall_back_for_client_errors(self):
        api = EPCAPI()
        api.session = Mock()
        response = requests.Response()
        response.status_code = 401
        api.session.get.return_value = response

        with self.assertRaises(requests.HTTPError):
            api.get_game_assets()
        self.assertEqual(1, api.session.get.call_count)

    def test_falls_back_to_paginated_library_when_asset_request_returns_gateway_timeout(
        self,
    ):
        api = EPCAPI()
        api.session = Mock()

        asset_response = requests.Response()
        asset_response.status_code = 504
        first_library_page = Mock()
        first_library_page.json.return_value = {
            'records': [
                {
                    'appName': 'FirstGame',
                    'catalogItemId': 'first-id',
                    'namespace': 'first-namespace',
                },
                {
                    'appName': 'UnrealAsset',
                    'catalogItemId': 'ue-id',
                    'namespace': 'ue',
                },
            ],
            'responseMetadata': {'nextCursor': 'page-2'},
        }
        second_library_page = Mock()
        second_library_page.json.return_value = {
            'records': [
                {
                    'appName': 'SecondGame',
                    'catalogItemId': 'second-id',
                    'namespace': 'second-namespace',
                },
                {
                    'appName': 'ExternalGame',
                    'catalogItemId': 'external-id',
                    'namespace': 'external-namespace',
                },
            ],
            'responseMetadata': {},
        }
        first_manifest = Mock()
        first_manifest.json.return_value = {
            'elements': [
                {
                    'appName': 'FirstGame',
                    'catalogItemId': 'first-id',
                    'namespace': 'first-namespace',
                    'buildVersion': '1.0',
                    'labelName': 'Live',
                }
            ],
        }
        second_manifest = Mock()
        second_manifest.json.return_value = {
            'elements': [
                {
                    'appName': 'SecondGame',
                    'catalogItemId': 'second-id',
                    'namespace': 'second-namespace',
                    'buildVersion': '2.0',
                    'labelName': 'Live',
                }
            ],
        }
        missing_manifest = requests.Response()
        missing_manifest.status_code = 404
        api.session.get.side_effect = [
            asset_response,
            first_library_page,
            second_library_page,
            first_manifest,
            second_manifest,
            missing_manifest,
        ]

        assets = api.get_game_assets()

        self.assertEqual(
            ['FirstGame', 'SecondGame'], [asset['appName'] for asset in assets]
        )
        self.assertEqual(['1.0', '2.0'], [asset['buildVersion'] for asset in assets])
        library_calls = [
            call
            for call in api.session.get.call_args_list
            if '/library/api/public/items' in call.args[0]
        ]
        self.assertEqual(2, len(library_calls))
        self.assertNotIn('cursor', library_calls[0].kwargs['params'])
        self.assertEqual('page-2', library_calls[1].kwargs['params']['cursor'])


if __name__ == '__main__':
    unittest.main()
