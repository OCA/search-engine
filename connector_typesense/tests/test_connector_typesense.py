# Copyright 2019 Kencove
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from time import sleep

from vcr_unittest import VCRMixin

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBase

from ..tools.adapter import TypesenseAdapter


class TestConnectorTypeSense(VCRMixin, TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref("connector_typesense.backend_1")
        cls.se_config = cls.env.ref("connector_typesense.se_index_config_product")
        cls.setup_records()
        cls.adapter: TypesenseAdapter = cls.se_index.se_adapter
        cls.demo_data = [
            {"id": "1", "name": "Foo"},
            {"id": "2", "name": "Bar"},
            {"id": "3", "name": "Baz"},
        ]

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "one",
            "match_on": ["method", "path", "query"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    @classmethod
    def _prepare_index_values(cls, backend):
        values = super()._prepare_index_values(backend)
        values.update({"config_id": cls.se_config.id})
        return values

    def test_index_adapter(self):
        # ts serialize type converts id type from integer into string
        self.se_index.write({"serializer_type": "typesense"})
        # Export collection settings to cassette (typesense)
        self.se_index.export_settings()

        data = self.partner_binding.data
        self.assertFalse(data)

        # Recompute data to be sent
        self.se_index.batch_recompute(force_export=True)
        data = self.partner_binding.data
        self.assertEqual(data["name"], "Marty McFly")
        self.assertIsInstance(data["id"], str)

        # Set partner to be updated and patch data to cassette (typesense)
        self.partner_binding.write({"state": "to_export"})
        self.se_index.batch_sync(force_export=True)

        # Ensure that calls have been recorded in cassette
        self.assertTrue(self.cassette.all_played)
        self.assertGreaterEqual(len(self.cassette.requests), 2)

        request_1 = self.cassette.requests[0]
        self.assertEqual(request_1.method, "GET")
        expected_path = f"/collections/{self.se_index.name}".lower()
        self.assertEqual(self.parse_path(request_1.uri), expected_path)
        response_1 = self.cassette.responses[0]
        body = response_1.get("body").get("string").decode("utf-8")
        lines = [line for line in filter(lambda line: line, body.split("\n"))]
        # we must have 1 line for the index op
        self.assertEqual(len(lines), 1)
        index_action = json.loads(lines[0])
        self.assertEqual(index_action.get("name"), f"{self.se_index.name}-2".lower())

        request_2 = self.cassette.requests[-1]
        self.assertEqual(request_2.method, "POST")
        body = request_2.body.decode("utf-8")
        data = json.loads(body)
        # Mock the preserved id in the cassette: 107 to new record id
        data["id"] = self.partner_binding.data.get("id")
        self.assertDictEqual(data, self.partner_binding.data)

    def test_index_config_as_str(self):
        self.se_config.write({"body_str": '{"mappings": {"1":1}}'})
        self.assertDictEqual(self.se_config.body, {"mappings": {"1": 1}})
        self.assertEqual(self.se_config.body_str, '{"mappings": {"1":1}}')

    def test_index_adapter_iter(self):
        data = self.demo_data
        self.adapter.clear()
        self.adapter.settings()
        self.adapter.index(data)
        if self.cassette.dirty:
            # when we record the test we must wait for es
            sleep(2)
        res = [x["document"] for x in self.adapter.each()]
        res.sort(key=lambda d: d["id"])
        self.assertListEqual(res, data)

    def test_index_adapter_delete(self):
        data = self.demo_data
        self.adapter.clear()
        self.adapter.index(data)
        if self.cassette.dirty:
            # when we record the test we must wait for es
            sleep(2)
        self.adapter.delete([1, 3])
        if self.cassette.dirty:
            # when we record the test we must wait for es
            sleep(2)
        res = [x["document"] for x in self.adapter.each()]
        res.sort(key=lambda d: d["id"])
        self.assertListEqual(res, [{"id": "2", "name": "Bar"}])

    def test_index_adapter_delete_nonexisting_documents(self):
        """We try to delete records that do not exist.
        Because it does not matter, it is just ignored. No exception.
        """
        self.adapter.delete(["donotexist", "donotexisteither"])

    def test_index_adapter_reindex(self):
        data = self.demo_data
        self.adapter.clear()
        self.adapter.index(data)
        index_name = self.adapter._get_current_aliased_index_name()
        next_index_name = self.adapter._get_next_aliased_index_name(index_name)
        if self.cassette.dirty:
            # when we record the test we must wait for es
            sleep(2)
        self.adapter.reindex()
        if self.cassette.dirty:
            # when we record the test we must wait for es
            sleep(2)
        res = [x["document"] for x in self.adapter.each()]
        res.sort(key=lambda d: d["id"])
        self.assertListEqual(res, data)
        self.assertEqual(
            self.adapter._get_current_aliased_index_name(), next_index_name
        )
