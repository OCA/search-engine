# -*- coding: utf-8 -*-
# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import os
from time import sleep

from vcr_unittest import VCRMixin

from odoo import exceptions

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBase

from ..components.adapter import AlgoliaAdapter


class TestAlgoliaBackend(VCRMixin, TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super(TestAlgoliaBackend, cls).setUpClass()
        AlgoliaAdapter._build_component(cls._components_registry)
        cls.backend_specific = cls.env.ref("connector_algolia.se_algolia_demo")
        cls.backend = cls.backend_specific.se_backend_id
        cls.backend_specific.algolia_app_id = os.environ.get(
            "ALGOLIA_APP_ID", "FAKE_APP"
        )
        cls.backend_specific.algolia_api_key = os.environ.get(
            "ALGOLIA_API_KEY", "FAKE_KEY"
        )
        cls.setup_records()
        with cls.backend_specific.work_on("se.index", index=cls.se_index) as work:
            cls.adapter = work.component(usage="se.backend.adapter")

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "once",
            "match_on": ["method", "path", "query"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    def test_get_api_credentials(self):
        self.assertEqual(
            self.backend_specific._get_api_credentials(),
            {"password": self.backend_specific.algolia_api_key},
        )

    def test_index_adapter_no_objectID(self):
        with self.assertRaises(exceptions.UserError) as err:
            self.adapter.index([{"foo": "bar"}])
        self.assertIn("The key objectID is missing in", err.exception.name)

    def test_index_adapter(self):
        data = {"objectID": "IamAnObjectID1", "foo": "bar"}
        self.adapter.index([data])
        self.assertEqual(len(self.cassette.requests), 1)
        request = self.cassette.requests[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(
            self.parse_path(request.uri),
            "/1/indexes/demo_algolia_backend_res_partner_binding_fake_en_US" "/batch",
        )
        request_data = json.loads(request.body.decode("utf-8"))["requests"]
        self.assertEqual(len(request_data), 1)
        self.assertEqual(request_data[0]["action"], "addObject")
        self.assertEqual(request_data[0]["body"], data)

    def test_index_adapter_clear(self):
        self.se_index.clear_index()
        self.assertEqual(len(self.cassette.requests), 1)
        request = self.cassette.requests[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(
            self.parse_path(request.uri),
            "/1/indexes/demo_algolia_backend_res_partner_binding_fake_en_US" "/clear",
        )

    def test_delete_adapter(self):
        self.adapter.delete(["IamAnObjectID"])
        self.assertEqual(len(self.cassette.requests), 1)
        request = self.cassette.requests[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(
            self.parse_path(request.uri),
            "/1/indexes/demo_algolia_backend_res_partner_binding_fake_en_US" "/batch",
        )
        request_data = json.loads(request.body.decode("utf-8"))["requests"]
        self.assertEqual(len(request_data), 1)
        self.assertEqual(request_data[0]["action"], "deleteObject")
        self.assertEqual(request_data[0]["body"], {"objectID": "IamAnObjectID"})

    def test_iter_adapter(self):
        data = [{"objectID": "foo"}]
        self.adapter.clear()
        self.adapter.index(data)
        if self.cassette.dirty:
            # when we record the test we must wait for algolia
            sleep(2)
        res = [x for x in self.adapter.iter()]
        self.assertEqual(res, data)
