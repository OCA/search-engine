# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from odoo_test_helper import FakeModelLoader

from odoo import exceptions
from odoo.tests.common import Form

from .common import TestSeBackendCaseBase


class TestBindingIndexBase(TestSeBackendCaseBase, FakeModelLoader):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import (
            BindingResPartnerFake,
            ResPartnerFake,
            SeBackendFake,
            SeAdapterFake,
        )

        cls.loader.update_registry(
            (BindingResPartnerFake, ResPartnerFake, SeBackendFake)
        )
        cls.binding_model = cls.env[BindingResPartnerFake._name]
        cls.fake_backend_model = cls.env[SeBackendFake._name]
        # ->/ Load fake models

        cls.se_adapter_fake = SeAdapterFake
        cls._load_fixture("ir_exports_test.xml")
        cls.exporter = cls.env.ref("connector_search_engine.ir_exp_partner_test")

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
            .search([("model", "=", "res.partner.binding.fake")], limit=1)
            .id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "exporter_id": cls.exporter.id,
        }

    @classmethod
    def setup_records(cls, backend=None):
        backend = backend or cls.backend
        # create an index for partner model
        cls.se_index = cls.se_index_model.create(cls._prepare_index_values(backend))
        # create a binding + partner alltogether
        cls.partner_binding = cls.binding_model.create(
            {
                "name": "Marty McFly",
                "country_id": cls.env.ref("base.us").id,
                "email": "marty.mcfly@future.com",
                "child_ids": [
                    (0, 0, {"name": "Doc Brown", "email": "docbrown@future.com"})
                ],
                "index_id": cls.se_index.id,
            }
        )
        cls.partner = cls.partner_binding.record_id


class TestBindingIndexBaseFake(TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.se_adapter_fake._build_component(cls._components_registry)

        cls.backend_specific = cls.fake_backend_model.create(
            {"name": "Fake SE", "tech_name": "fake_se"}
        )
        cls.backend = cls.backend_specific.se_backend_id
        cls.setup_records()


class TestBindingIndex(TestBindingIndexBaseFake):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    # TODO: the following `test_backend*` methods
    # should be splitted to a smaller test case.
    # ATM is not possible since the teardown of this class
    # is going to drop the fake models and make any subsequent test case fail.
    # We should find a way to run tear down at the end of ALL test cases.
    def test_backend_specific_select(self):
        self.assertIn(
            self.fake_backend_model._name,
            [x[0] for x in self.env["se.backend"]._select_specific_model()],
        )

    def test_backend_specific_records(self):
        self.assertIn(
            (self.fake_backend_model._name, self.backend_specific.name),
            self.env["se.backend"]._select_specific_backend(),
        )

    def test_backend_defaults(self):
        self.assertEqual(self.backend.specific_model, self.backend_specific._name)

    def test_backend_unlink(self):
        self.assertTrue(self.backend_specific.exists())
        self.assertTrue(self.backend.exists())
        self.backend_specific.unlink()
        self.assertFalse(self.backend_specific.exists())
        self.assertFalse(self.backend.exists())

    def test_backend_name(self):
        form = Form(self.env["se.backend"])
        form.name = "Á weird nämë plenty of CR@P!"
        # tech name normalized
        self.assertEqual(form.tech_name, "a_weird_name_plenty_of_cr_p")
        self.assertEqual(form.index_prefix_name, "a_weird_name_plenty_of_cr_p")
        form.tech_name = "better_name"
        form.index_prefix_name = "better_prefix"
        form.name = "My search backend"
        # name updated, tech names stay
        self.assertEqual(form.tech_name, "better_name")
        self.assertEqual(form.index_prefix_name, "better_prefix")

    def test_backend_create_tech_defaults(self):
        b1 = self.fake_backend_model.create({"name": "Fake 1"})
        self.assertEqual(b1.tech_name, "fake_1")
        self.assertEqual(b1.index_prefix_name, "fake_1")
        b2 = self.fake_backend_model.create({"name": "Fake 2", "tech_name": "test2"})
        self.assertEqual(b2.tech_name, "test2")
        self.assertEqual(b2.index_prefix_name, "test2")
        b3 = self.fake_backend_model.create(
            {"name": "Fake 3", "tech_name": "test3", "index_prefix_name": "baz"}
        )
        self.assertEqual(b3.tech_name, "test3")
        self.assertEqual(b3.index_prefix_name, "baz")

    def test_index_name(self):
        self.assertEqual(self.se_index.name, "fake_se_res_partner_binding_fake_en_US")
        # control indexes' name via prefix tech name
        self.backend.index_prefix_name = "foo_baz"
        # TODO: not sure why this is needed here
        self.se_index.invalidate_cache()
        self.assertEqual(self.se_index.name, "foo_baz_res_partner_binding_fake_en_US")

    def test_changing_model_remove_exporter(self):
        res = self.se_index.onchange_model_id()
        self.assertEqual(len(self.se_index.exporter_id), 0)
        self.assertIn("domain", res)
        self.assertIn("exporter_id", res["domain"])

    def test_model_id_domain(self):
        result = self.se_index._model_id_domain()
        models = result[0][2]
        self.assertIn("res.partner.binding.fake", models)

    def test_recompute_all_indexes(self):
        # on creation indexes are computed and external data stored
        expected = {
            "id": self.partner_binding.id,
            "active": True,
            "lang": "en_US",
            "name": "Marty McFly",
            "credit_limit": 0.0,
            "country_id": {"code": "US", "name": "United States"},
            "color": 0,
            "child_ids": [
                {
                    "id": self.partner.child_ids[0].id,
                    "name": "Doc Brown",
                    "email": "docbrown@future.com",
                    "child_ids": [],
                    "country_id": {"code": "US", "name": "United States"},
                }
            ],
        }
        self.assertEqual(self.partner_binding.get_export_data(), expected)
        self.assertEqual(self.partner_binding.sync_state, "to_update")
        # on index recompute external data must be updated
        self.partner.name = "George McFly"
        expected["name"] = self.partner.name
        self.env["se.index"].recompute_all_index()
        self.assertEqual(self.partner_binding.get_export_data(), expected)
        self.assertEqual(self.partner_binding.sync_state, "to_update")

    def test_force_recompute_all_binding(self):
        with mock.patch.object(type(self.se_index), "recompute_all_binding") as mocked:
            self.se_index.force_recompute_all_binding()
        mocked.assert_called_with(force_export=True)

    def test_force_batch_export(self):
        # "new" should not be sync'ed but it will because we run forced export
        self.partner_binding.sync_state = "new"
        tracking = []
        self.se_index.with_context(call_tracking=tracking).force_batch_export()
        self.assertEqual(tracking, ["Exported ids : [1]\nDeleted ids : []"])
        self.assertEqual(self.partner_binding.sync_state, "scheduled")

    def test_generate_batch_export_per_index(self):
        tracking = []
        self.env["se.index"].with_context(
            call_tracking=tracking
        ).generate_batch_export_per_index()
        self.assertEqual(tracking, ["Exported ids : [1]\nDeleted ids : []"])

    def test_get_domain_for_exporting_binding(self):
        expected = [
            ("index_id", "=", self.se_index.id),
            ("sync_state", "=", "to_update"),
        ]
        self.assertEqual(self.se_index._get_domain_for_exporting_binding(), expected)

    def test_batch_export(self):
        # state = new, nothing to export
        self.partner_binding.sync_state = "new"
        tracking = []
        self.se_index.with_context(call_tracking=tracking).batch_export()
        self.assertEqual(tracking, [])
        self.assertEqual(self.partner_binding.sync_state, "new")

        # now it should find the bindings marked for update and schedule them
        self.partner_binding.sync_state = "to_update"
        tracking = []
        self.se_index.with_context(call_tracking=tracking).batch_export()
        self.assertEqual(tracking, ["Exported ids : [1]\nDeleted ids : []"])
        self.assertEqual(self.partner_binding.sync_state, "scheduled")

        # even if the binding is inactive it should schedule and delete them
        self.partner_binding.sync_state = "to_update"
        self.partner_binding.active = False
        tracking = []
        self.se_index.with_context(call_tracking=tracking).batch_export()
        self.assertEqual(tracking, ["Exported ids : []\nDeleted ids : [1]"])
        self.assertEqual(self.partner_binding.sync_state, "scheduled")

    def test_clear_index(self):
        with self.se_adapter_fake.mocked_calls() as calls:
            self.se_index.clear_index()
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["work_ctx"]["index"], self.se_index)
            self.assertEqual(calls[0]["method"], "clear")

    def test_synchronize_active_binding(self):
        # when binding is active it should update it
        with self.se_adapter_fake.mocked_calls() as calls:
            self.partner_binding.synchronize()
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["work_ctx"]["index"], self.se_index)
            self.assertEqual(calls[0]["work_ctx"]["records"], self.partner_binding)
            self.assertEqual(calls[0]["method"], "index")

    def test_synchronize_inactive_binding(self):
        # when binding is inactive it should delete it
        self.partner_binding.active = False
        with self.se_adapter_fake.mocked_calls() as calls:
            self.partner_binding.synchronize()
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["work_ctx"]["index"], self.se_index)
            self.assertEqual(calls[0]["work_ctx"]["records"], self.partner_binding)
            self.assertEqual(calls[0]["method"], "delete")

    def test_unlink_new_binding(self):
        self.partner_binding.sync_state = "new"
        self.partner_binding.unlink()
        self.assertEqual(len(self.partner_binding.exists()), 0)

    def test_unlink_done_inactive_binding(self):
        self.partner_binding.active = False
        self.partner_binding.sync_state = "done"
        self.partner_binding.unlink()
        self.assertEqual(len(self.partner_binding.exists()), 0)

    def test_unlink_to_update_inactive_binding(self):
        self.partner_binding.active = False
        self.partner_binding.sync_state = "to_update"
        with self.assertRaises(exceptions.UserError) as err:
            self.partner_binding.unlink()
        self.assertIn("wait until it's synchronized.", err.exception.name)

    def test_unlink_to_upgrade_active_binding(self):
        self.partner_binding.sync_state = "to_update"
        with self.assertRaises(exceptions.UserError) as err:
            self.partner_binding.unlink()
        self.assertIn("unactivate it first", err.exception.name)

    def test_unlink_done_active_binding(self):
        self.partner_binding.sync_state = "done"
        with self.assertRaises(exceptions.UserError) as err:
            self.partner_binding.unlink()
        self.assertIn("unactivate it first", err.exception.name)

    def test_inactive_binding_change_state(self):
        self.partner_binding.sync_state = "done"
        self.partner_binding.active = False
        self.assertEqual(self.partner_binding.sync_state, "to_update")

    def test_inactive_new_binding_do_not_change_state(self):
        self.partner_binding.sync_state = "new"
        self.partner_binding.active = False
        self.assertEqual(self.partner_binding.sync_state, "new")

    def test_resynchronize_all_bindings(self):
        # The iter method in the mock will return the item id 42 that do not
        # exist as we have dropped all binding
        # the resync method will call the delete to remove this obsolete item
        bindings = self.binding_model.search([])
        bindings.write({"sync_state": "new"})
        bindings.unlink()
        with self.se_adapter_fake.mocked_calls() as calls:
            self.se_index.resynchronize_all_bindings()
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["work_ctx"]["index"], self.se_index)
            self.assertEqual(calls[0]["method"], "each")
            self.assertEqual(calls[1]["work_ctx"]["index"], self.se_index)
            self.assertEqual(calls[1]["method"], "delete")
            self.assertEqual(calls[1]["args"], [42])
