# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from odoo import exceptions, tools
from odoo.addons.connector_search_engine.tests.test_all \
    import TestBindingIndexBase

from ..components.adapter import AlgoliaAdapter
from .common import VCRMixin


class TestAlgoliaBackend(TestBindingIndexBase, VCRMixin):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AlgoliaAdapter._build_component(cls._components_registry)
        cls.backend_specific = cls.env.ref('connector_algolia.se_algolia_demo')
        cls.backend = cls.backend_specific.se_backend_id
        cls.backend_specific.algolia_app_id = 'RQJXD7ZPFA'
        cls.backend_specific.algolia_api_key = \
            'fd2b23ce63aebd599a738a8a558dbcdd'
        cls.setup_records()
        cls.recorder = cls.get_recorder()

    def test_get_api_credentials(self):
        self.assertEqual(
            self.backend_specific._get_api_credentials(),
            {'password': self.backend_specific.algolia_api_key}
        )

    def test_index_adapter_no_objectID(self):
        self.partner_binding.sync_state = 'to_update'
        with self.assertRaises(exceptions.UserError) as err:
            self.se_index.batch_export()
        self.assertTrue(err.exception.name.startswith(
            'Partner Index error. The key objectID is missing'
        ))

    def test_index_adapter(self):
        self.partner_binding.sync_state = 'to_update'
        # inject fake objectID
        self.partner_binding.data = dict(
            self.partner_binding.data, objectID='IamAnObjectID'
        )
        with self.recorder.use_cassette(
                'test_index_partner_batch') as cassette:
            self.se_index.batch_export()
        self.assertEqual(len(cassette.requests), 1)
        request = cassette.requests[0]
        self.assertEqual(request.method, 'POST')
        self.assertEqual(self.parse_path(request.uri),
                         '/1/indexes/Partner%20Index/batch')
        # TODO
        # request_data = json.loads(request.body)['requests']
        # expected = [{
        #     'action': 'addObject',
        #     'body': {
        #         'active': True,
        #         'child_ids': [{
        #             'child_ids': [],
        #             'country_id': {'code': 'US', 'name': 'United States'},
        #             'email': 'docbrown@future.com',
        #             'id': self.partner.child_ids[0].id,
        #             'name': 'Doc Brown'
        #         }],
        #         'color': 0,
        #         'country_id': {'code': 'US', 'name': 'United States'},
        #         'credit_limit': 0.0,
        #         'lang': 'en_US',
        #         'name': 'Marty McFly',
        #         'id': self.partner_binding.id,
        #         'objectID': 'IamAnObjectID'
        #     }
        # }]
        # self.assertEqual(request_data[0], expected[0])
        # TODO test response too

    def test_index_adapter_clear(self):
        with self.recorder.use_cassette(
                'test_index_partner_clear') as cassette:
            self.se_index.clear_index()
        self.assertEqual(len(cassette.requests), 1)
        request = cassette.requests[0]
        self.assertEqual(request.method, 'POST')
        self.assertEqual(self.parse_path(request.uri),
                         '/1/indexes/Partner%20Index/clear')
        self.assertEqual(request.body, None)

        response = cassette.responses[0]
        self.assertEqual(response['status'], {'code': 200, 'message': 'OK'})
        body = cassette.responses[0]['body']['string']
        body = json.loads(tools.pycompat.to_text(body))
        self.assertIn('updatedAt', body)
        self.assertIn('taskID', body)
