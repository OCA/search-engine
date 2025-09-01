# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging
from time import sleep
from urllib import parse as urlparse

from odoo_test_helper import FakeModelLoader
from vcr_unittest import VCRMixin

from odoo import tools
from odoo.modules.module import get_resource_path
from odoo.tests.common import TransactionCase


def load_xml(env, module, filepath):
    tools.convert_file(
        env.cr,
        module,
        get_resource_path(module, filepath),
        {},
        mode="init",
        noupdate=False,
        kind="test",
    )


class TestSeBackendCaseBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,  # speed up tests
                queue_job__no_delay=True,  # no jobs thanks
            )
        )

    @classmethod
    def _load_fixture(cls, fixture, module="connector_search_engine"):
        load_xml(cls.env, module, "tests/fixtures/%s" % fixture)

    @staticmethod
    def parse_path(url):
        return urlparse.urlparse(url).path

    def setUp(self):
        super(TestSeBackendCaseBase, self).setUp()
        loggers = ["odoo.addons.queue_job.utils"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        # pylint: disable=unused-variable
        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    def filter(self, record):
        return 0


class TestBindingIndexBase(TestSeBackendCaseBase, FakeModelLoader):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import (
            FakeSeAdapter,
            FakeSerializer,
            ResPartner,
            ResUsers,
            SeBackend,
            SeIndex,
        )

        cls.loader.update_registry((ResPartner, ResUsers, SeBackend, SeIndex))
        cls.binding_model = cls.env["se.binding"]
        cls.se_index_model = cls.env["se.index"]

        cls.se_adapter = FakeSeAdapter
        cls.model_serializer = FakeSerializer

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    @classmethod
    def _prepare_index_values(cls, backend=None):
        backend = backend or cls.backend
        return {
            "name": "Partner Index",
            "backend_id": backend.id,
            "model_id": cls.env["ir.model"]
            .search([("model", "=", "res.partner")], limit=1)
            .id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "serializer_type": "fake",
        }

    @classmethod
    def setup_records(cls, backend=None):
        backend = backend or cls.backend
        # create an index for partner model
        cls.se_index = cls.se_index_model.create(cls._prepare_index_values(backend))
        # create a binding + partner alltogether
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Marty McFly",
                "country_id": cls.env.ref("base.us").id,
                "email": "marty.mcfly@future.com",
                "child_ids": [
                    (0, 0, {"name": "Doc Brown", "email": "docbrown@future.com"})
                ],
            }
        )
        cls.partner_binding = cls.partner._add_to_index(cls.se_index)

        cls.partner_expected = {"id": cls.partner.id, "name": cls.partner.name}


class TestBindingIndexBaseFake(TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend_model = cls.env["se.backend"]
        cls.backend = cls.backend_model.create(
            {"name": "Fake SE", "tech_name": "fake_se", "backend_type": "fake"}
        )
        cls.setup_records()


class CommonTestAdapter(VCRMixin):
    """All adapter should behave exactly the same, whatever search engine
    we use, adapter should have the same input and same output"""

    _backend_xml_id = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref(cls._backend_xml_id)
        cls.setup_records()
        cls.adapter = cls.se_index.se_adapter
        cls.data = [
            {"id": 1, "name": "foo"},
            {"id": 2, "name": "bar"},
            {"id": 3, "name": "joe"},
        ]

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "one",
            "match_on": ["method", "path", "query", "raw_body"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    @classmethod
    def _se_index_config(cls):
        return {}

    @classmethod
    def setup_records(cls):
        vals = cls._se_index_config()
        # As body_str have a default value we can not write directly in body
        vals["body_str"] = json.dumps(vals.pop("body"))
        cls.se_config = cls.env["se.index.config"].create(vals)
        return super().setup_records()

    def setUp(self):
        super().setUp()
        # Always start with a clean index
        self.adapter.clear()

    @classmethod
    def _prepare_index_values(cls, backend):
        values = super()._prepare_index_values(backend)
        values.update({"config_id": cls.se_config.id})
        return values

    def tearDown(self):
        super().tearDown()
        # Ensure all call have been done to the cassette
        # when we are replaying it
        if not self.cassette.dirty:
            self.assertTrue(
                self.cassette.all_played, "All cassettes have been not played"
            )

    def _wait_search_engine(self):
        if self.cassette.dirty:
            # when we record the test we must wait for the search engine
            sleep(2)

    def test_index_adapter_index_and_iter(self):
        data = []
        for _id in range(1, 2000):
            data.append({"id": _id, "name": f"My name is {_id}"})
        self.adapter.index(data)
        self._wait_search_engine()
        res = [x for x in self.adapter.each()]
        res.sort(key=lambda d: d["id"])
        self.assertListEqual(res, data)

    def test_index_adapter_delete(self):
        self.adapter.index(self.data)
        self._wait_search_engine()
        self.adapter.delete([1, 2])
        self._wait_search_engine()
        res = [x for x in self.adapter.each()]
        res.sort(key=lambda d: d["id"])
        self.assertListEqual(res, [{"id": 3, "name": "joe"}])

    def test_index_adapter_delete_nonexisting_documents(self):
        """We try to delete records that do not exist.
        Because it does not matter, it is just ignored. No exception.
        """
        self.adapter.delete(["donotexist", "donotexisteither"])

    def test_index_adapter_reindex(self):
        self.adapter.index(self.data)
        index_name = self.adapter._get_current_aliased_index_name()
        next_index_name = self.adapter._get_next_aliased_index_name(index_name)
        self._wait_search_engine()
        self.adapter.reindex()
        self._wait_search_engine()
        res = [x for x in self.adapter.each()]
        res.sort(key=lambda d: d["id"])
        self.assertListEqual(res, self.data)
        self.assertEqual(
            self.adapter._get_current_aliased_index_name(), next_index_name
        )
