# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from odoo import exceptions

from .common import TestSeBackendCaseBase
from .models import (
    BindingResPartnerFake,
    ResPartnerFake,
    SeAdapterFake,
    SeBackendFake,
)


class TestBindingIndexBase(TestSeBackendCaseBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        BindingResPartnerFake._test_setup_model(cls.env)
        ResPartnerFake._test_setup_model(cls.env)
        cls._load_fixture("ir_exports_test.xml")
        cls.exporter = cls.env.ref(
            "connector_search_engine.ir_exp_partner_test"
        )

    @classmethod
    def tearDownClass(cls):
        ResPartnerFake._test_teardown_model(cls.env)
        BindingResPartnerFake._test_teardown_model(cls.env)
        super().tearDownClass()

    @classmethod
    def _prepare_index_values(cls, backend=None):
        backend = backend or cls.backend
        return {
            "name": "Partner Index",
            "backend_id": backend.id,
            "model_id": cls.env.ref(
                "connector_search_engine.model_res_partner_binding_fake"
            ).id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "exporter_id": cls.exporter.id,
        }

    @classmethod
    def setup_records(cls, backend=None):
        backend = backend or cls.backend
        # create an index for partner model
        cls.se_index = cls.se_index_model.create(
            cls._prepare_index_values(backend)
        )
        # create a binding + partner alltogether
        cls.binding_model = cls.env[BindingResPartnerFake._name]
        cls.partner_binding = cls.binding_model.create(
            {
                "name": "Marty McFly",
                "country_id": cls.env.ref("base.us").id,
                "email": "marty.mcfly@future.com",
                "child_ids": [
                    (
                        0,
                        0,
                        {"name": "Doc Brown", "email": "docbrown@future.com"},
                    )
                ],
                "index_id": cls.se_index.id,
            }
        )
        cls.partner = cls.partner_binding.record_id


class TestBindingIndexBaseFake(TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SeAdapterFake._build_component(cls._components_registry)
        SeBackendFake._test_setup_model(cls.env)
        cls.fake_backend_model = cls.env[SeBackendFake._name]
        cls.backend_specific = cls.fake_backend_model.create(
            {"name": "Fake SE"}
        )
        cls.backend = cls.backend_specific.se_backend_id
        cls.setup_records()

    @classmethod
    def tearDownClass(cls):
        SeBackendFake._test_teardown_model(cls.env)
        super().tearDownClass()


class TestBindingIndex(TestBindingIndexBaseFake):

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
        sel = "{},{}".format(
            self.fake_backend_model._name, self.backend_specific.id
        )
        self.assertIn(
            (sel, self.backend_specific.name),
            self.env["se.backend"]._select_specific_backend(),
        )

    def test_backend_defaults(self):
        self.assertEqual(
            self.backend.specific_model, self.backend_specific._name
        )

    def test_backend_unlink(self):
        self.assertTrue(self.backend_specific.exists())
        self.assertTrue(self.backend.exists())
        self.backend_specific.unlink()
        self.assertFalse(self.backend_specific.exists())
        self.assertFalse(self.backend.exists())

    def test_changing_name_with_index_raise_warning(self):
        res = self.backend_specific.onchange_backend_name()
        self.assertIn("warning", res)
        self.backend_specific.index_ids.unlink()
        res = self.backend_specific.onchange_backend_name()
        self.assertIsNone(res)

    def test_changing_model_remove_exporter(self):
        res = self.se_index.onchange_model_id()
        self.assertEqual(len(self.se_index.exporter_id), 0)
        self.assertIn("domain", res)
        self.assertIn("exporter_id", res["domain"])

    def test_get_model_domain(self):
        result = self.se_index._get_model_domain()
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
        with mock.patch.object(
            type(self.se_index), "recompute_all_binding"
        ) as mocked:
            self.se_index.force_recompute_all_binding()
        mocked.assert_called_with(force_export=True)

    def test_force_batch_export(self):
        self.partner_binding.sync_state = "new"
        with mock.patch.object(type(self.se_index), "batch_export") as mocked:
            self.se_index.force_batch_export()
        self.assertEqual(self.partner_binding.sync_state, "to_update")
        mocked.assert_called()

    def test_generate_batch_export_per_index(self):
        with mock.patch.object(type(self.se_index), "batch_export") as mocked:
            self.env["se.index"].generate_batch_export_per_index()
        mocked.assert_called()

    def test_get_domain_for_exporting_binding(self):
        expected = [
            ("index_id", "=", self.se_index.id),
            ("sync_state", "=", "to_update"),
        ]
        self.assertEqual(
            self.se_index._get_domain_for_exporting_binding(), expected
        )

    def test_batch_export(self):
        # state = new, nothing to export
        self.partner_binding.sync_state = "new"
        with mock.patch.object(
            type(self.partner_binding), "synchronize"
        ) as mocked:
            self.se_index.batch_export()
        self.assertEqual(self.partner_binding.sync_state, "new")
        mocked.assert_not_called()
        # now it should find the bindings marked for update and schedule them
        self.partner_binding.sync_state = "to_update"
        with mock.patch.object(
            type(self.partner_binding), "synchronize"
        ) as mocked:
            self.se_index.batch_export()
        self.assertEqual(self.partner_binding.sync_state, "scheduled")
        mocked.assert_called()
        # even if the binding is inactive it should schedule them
        self.partner_binding.sync_state = "to_update"
        self.partner_binding.active = False
        with mock.patch.object(
            type(self.partner_binding), "synchronize"
        ) as mocked:
            self.se_index.batch_export()
        self.assertEqual(self.partner_binding.sync_state, "scheduled")
        mocked.assert_called()

    def test_clear_index(self):
        with SeAdapterFake.mocked_calls() as calls:
            self.se_index.clear_index()
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["work_ctx"]["index"], self.se_index)
            self.assertEqual(calls[0]["method"], "clear")

    def test_synchronize_active_binding(self):
        # when binding is active it should update it
        with SeAdapterFake.mocked_calls() as calls:
            self.partner_binding.synchronize()
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["work_ctx"]["index"], self.se_index)
            self.assertEqual(
                calls[0]["work_ctx"]["records"], self.partner_binding
            )
            self.assertEqual(calls[0]["method"], "index")

    def test_synchronize_inactive_binding(self):
        # when binding is inactive it should delete it
        self.partner_binding.active = False
        with SeAdapterFake.mocked_calls() as calls:
            self.partner_binding.synchronize()
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["work_ctx"]["index"], self.se_index)
            self.assertEqual(
                calls[0]["work_ctx"]["records"], self.partner_binding
            )
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
        with SeAdapterFake.mocked_calls() as calls:
            self.se_index.resynchronize_all_bindings()
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0]["work_ctx"]["index"], self.se_index)
            self.assertEqual(calls[0]["method"], "iter")
            self.assertEqual(calls[1]["work_ctx"]["index"], self.se_index)
            self.assertEqual(calls[1]["method"], "delete")
            self.assertEqual(calls[1]["args"], [42])
