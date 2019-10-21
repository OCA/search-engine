# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from time import sleep

from vcr_unittest import VCRMixin

from odoo import exceptions

from odoo.addons.connector_search_engine.tests.models import SeBackendFake
from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBase


class TestConnectorElasticsearch(VCRMixin, TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super(TestConnectorElasticsearch, cls).setUpClass()
        cls.backend_specific = cls.env.ref("connector_elasticsearch.backend_1")
        cls.backend = cls.backend_specific.se_backend_id
        cls.se_index_model = cls.env["se.index"]
        cls.setup_records()
        with cls.backend_specific.work_on("se.index", index=cls.se_index) as work:
            cls.adapter = work.component(usage="se.backend.adapter")
        SeBackendFake._test_setup_model(cls.env)
        cls.fake_backend_model = cls.env[SeBackendFake._name]
        cls.fake_backend_specific = cls.fake_backend_model.create({"name": "Fake SE"})
        cls.fake_backend = cls.fake_backend_specific.se_backend_id

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "one",
            "match_on": ["method", "path", "query"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    @classmethod
    def setup_records(cls):
        cls.se_config = cls.env["se.index.config"].create(
            {"name": "my_config", "body": {"mappings": {}}}
        )
        super(TestConnectorElasticsearch, cls).setup_records()

    @classmethod
    def _prepare_index_values(cls, backend):
        values = super(TestConnectorElasticsearch, cls)._prepare_index_values(backend)
        values.update({"config_id": cls.se_config.id})
        return values

    def test_index_adapter_no_objectID(self):
        self.partner_binding.sync_state = "to_update"
        with self.assertRaises(exceptions.UserError) as err:
            self.se_index.batch_export()
        self.assertIn("The key objectID is missing in", err.exception.name)

    def test_index_adapter(self):
        # Set partner to be updated with fake vals in data
        self.partner_binding.write(
            {"sync_state": "to_update", "data": {"objectID": "foo"}}
        )
        # Export index to elasticsearch should be called
        self.se_index.batch_export()
        # We should have 3 or 4 request...
        # ping
        # index exists?
        # if not exits -> create (dependening of the elasticsearch content)
        # export
        self.assertGreaterEqual(len(self.cassette.requests), 3)
        request = self.cassette.requests[-1]
        self.assertEqual(request.method, "POST")
        self.assertEqual(self.parse_path(request.uri), "/_bulk")
        body = request.body.decode("utf-8")
        lines = [l for l in filter(lambda l: l, body.split("\n"))]
        # we must have 2 lines: 1 for the index op and 1 with data
        self.assertEqual(len(lines), 2)
        index_action = json.loads(lines[0])
        self.assertDictEqual(
            index_action,
            {
                "index": {
                    "_index": "demo_elasticsearch_backend_res_partner_"
                    "binding_fake_en_us",
                    "_id": "foo",
                }
            },
        )
        index_data = json.loads(lines[1])
        self.assertDictEqual(index_data, {"objectID": "foo"})

    def test_index_config_as_str(self):
        self.se_config.write({"body_str": '{"mappings": {"1":1}}'})
        self.assertDictEqual(self.se_config.body, {"mappings": {"1": 1}})
        self.assertEqual(self.se_config.body_str, '{"mappings": {"1": 1}}')

    def test_index_adapter_iter(self):
        data = [{"objectID": "foo"}, {"objectID": "foo2"}, {"objectID": "foo3"}]
        self.adapter.clear()
        self.adapter.index(data)
        if self.cassette.dirty:
            # when we record the test we must wait for algolia
            sleep(2)
        res = [x for x in self.adapter.iter()]
        res.sort(key=lambda d: d["objectID"])
        self.assertListEqual(res, data)

    def test_index_adapter_delete(self):
        data = [{"objectID": "foo"}, {"objectID": "foo2"}, {"objectID": "foo3"}]
        self.adapter.clear()
        self.adapter.index(data)
        if self.cassette.dirty:
            # when we record the test we must wait for algolia
            sleep(2)
        res = self.adapter.delete(["foo", "foo3"])
        self.assertTrue(res)
        if self.cassette.dirty:
            # when we record the test we must wait for algolia
            sleep(2)
        res = [x for x in self.adapter.iter()]
        res.sort(key=lambda d: d["objectID"])
        self.assertListEqual(res, [{"objectID": "foo2"}])
