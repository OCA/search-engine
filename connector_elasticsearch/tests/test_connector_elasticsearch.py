# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.addons.connector_search_engine.tests.test_all import (
    TestBindingIndexBase,
)

from .common import mock_api


class TestConnectorElasticsearch(TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend_specific = cls.env.ref("connector_elasticsearch.backend_1")
        cls.backend = cls.backend_specific.se_backend_id
        cls.exporter = cls.env.ref("base_jsonify.ir_exp_partner")
        cls.se_index_model = cls.env["se.index"]
        cls.setup_records()

    def test_index_adapter_no_objectID(self):
        self.partner_binding.sync_state = "to_update"
        with mock_api(self.env), self.assertRaises(
            exceptions.UserError
        ) as err:
            self.se_index.batch_export()
        self.assertIn("The key objectID is missing in", err.exception.name)

    def test_index_adapter(self):
        # Set partner to be updated with fake vals in data
        self.partner_binding.write(
            {"sync_state": "to_update", "data": {"objectID": "foo"}}
        )

        # Export index to elasticsearch should be called
        with mock_api(self.env) as mocked_api:
            self.se_index.batch_export()
            self.assertIn(self.se_index.name.lower(), mocked_api.index)
