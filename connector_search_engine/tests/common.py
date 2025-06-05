# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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


class CommonTestAdapter(VCRMixin, TestBindingIndexBase):
    _backend_xml_id = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref(cls._backend_xml_id)
        cls.setup_records()
        cls.adapter = cls.se_index.se_adapter

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "one",
            "match_on": ["method", "path", "query"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    @classmethod
    def _se_index_config(cls):
        return {}

    @classmethod
    def setup_records(cls):
        cls.se_config = cls.env["se.index.config"].create(cls._se_index_config())
        return super().setup_records()

    @classmethod
    def _prepare_index_values(cls, backend):
        values = super()._prepare_index_values(backend)
        values.update({"config_id": cls.se_config.id})
        return values

    def test_index_adapter(self):
        # Set partner to be updated with fake vals in data
        self.partner_binding.write({"state": "to_export", "data": {"id": "foo"}})
        # Export index to elasticsearch should be called
        self.se_index.batch_sync()

        # Ensure that call have been done to the cassette
        self.assertTrue(self.cassette.all_played)

    def test_index_config_as_str(self):
        self.se_config.write({"body_str": '{"mappings": {"1":1}}'})
        self.assertDictEqual(self.se_config.body, {"mappings": {"1": 1}})
        self.assertEqual(self.se_config.body_str, '{"mappings": {"1":1}}')

    def test_index_adapter_iter(self):
        data = [{"id": "foo"}, {"id": "foo2"}, {"id": "foo3"}]
        self.adapter.clear()
        self.adapter.index(data)
        if self.cassette.dirty:
            # when we record the test we must wait for es
            sleep(2)
        res = [x for x in self.adapter.each()]
        res.sort(key=lambda d: d["id"])
        self.assertListEqual(res, data)

    def test_index_adapter_delete(self):
        data = [{"id": "foo"}, {"id": "foo2"}, {"id": "foo3"}]
        self.adapter.clear()
        self.adapter.index(data)
        if self.cassette.dirty:
            # when we record the test we must wait for es
            sleep(2)
        self.adapter.delete(["foo", "foo3"])
        if self.cassette.dirty:
            # when we record the test we must wait for es
            sleep(2)
        res = [x for x in self.adapter.each()]
        res.sort(key=lambda d: d["id"])
        self.assertListEqual(res, [{"id": "foo2"}])

    def test_index_adapter_delete_nonexisting_documents(self):
        """We try to delete records that do not exist.
        Because it does not matter, it is just ignored. No exception.
        """
        self.adapter.delete(["donotexist", "donotexisteither"])

    def test_index_adapter_reindex(self):
        data = [{"id": "foo"}, {"id": "foo2"}, {"id": "foo3"}]
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
        res = [x for x in self.adapter.each()]
        res.sort(key=lambda d: d["id"])
        self.assertListEqual(res, data)
        self.assertEqual(
            self.adapter._get_current_aliased_index_name(), next_index_name
        )
