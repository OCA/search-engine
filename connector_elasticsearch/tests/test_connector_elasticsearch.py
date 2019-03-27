# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.addons.connector_search_engine.tests.test_all import (
    TestBindingIndexBase,
)
from odoo.exceptions import ValidationError

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

    @classmethod
    def setup_records(cls):
        cls.se_config = cls.env["se.index.config"].create(
            {
                "name": "my_config",
                "doc_type": "odoo_doc",
                "body": {"mappings": {"odoo_doc": {}}},
            }
        )
        super().setup_records()

    @classmethod
    def _prepare_index_values(cls, backend):
        values = super()._prepare_index_values(backend)
        values.update({"config_id": cls.se_config.id})
        return values

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
            index_name = self.se_index.name.lower()
            self.assertIn(index_name, mocked_api.index)
            self.assertEqual(
                mocked_api.index[index_name].get("body"), self.se_config.body
            )

    def test_index_config(self):
        """Check constrains on doc_type and config body: If a mappings is
        specified, at least one entry must exist for the given doctype
        """
        self.assertEqual(self.se_config.doc_type, "odoo_doc")
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.se_config.body = {"mappings": "toto"}
        self.se_config.write(
            {
                "doc_type": "new_doc_type",
                "body": {"mappings": {"new_doc_type": {}}},
            }
        )

    def test_inex_config_as_str(self):
        self.se_config.write(
            {"body_str": '{"mappings": {"odoo_doc": {"1":1}}}'}
        )
        self.assertDictEqual(
            self.se_config.body, {"mappings": {"odoo_doc": {"1": 1}}}
        )
