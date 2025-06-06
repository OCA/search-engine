# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError

from odoo.addons.connector_search_engine.tests.common import (
    CommonTestAdapter,
    TestBindingIndexBase,
)

# NOTE: if you need to refresh tests, you can fire up an Typesense instance
# using `docker-compose.typesense.example.yml` in this same folder.
# If you are not running in a docker env, you'll need to add an alias
# in /etc/hosts to make "typesense" name point to 127.0.0.1


class TestConnectorTypesense(CommonTestAdapter, TestBindingIndexBase):
    _backend_xml_id = "connector_typesense.backend_1"

    @classmethod
    def _se_index_config(cls):
        return {
            "name": "my_config",
            "body": {"fields": [{"name": "name", "type": "string"}]},
        }

    def _update_schema(self, fields):
        self.se_index.config_id.write({"body": {"fields": fields}})
        self.adapter.settings()

    def _assert_fields_in_schema(self, expected_fields):
        res = self.adapter._ts_client.collections[self.adapter._index_name].retrieve()
        fields = [x["name"] for x in res["fields"]]
        fields.sort()
        expected_fields.sort()
        self.assertEqual(expected_fields, fields)

    def test_update_schema(self):
        self.adapter.settings()
        self._assert_fields_in_schema(["name"])

        self._update_schema([{"name": "title", "type": "string"}])
        # Only adding field are supported so the name is still here
        self._assert_fields_in_schema(["title", "name"])

    def test_index_adapter_reindex(self):
        with self.assertRaisesRegex(UserError, "not needed"):
            self.adapter.reindex()
