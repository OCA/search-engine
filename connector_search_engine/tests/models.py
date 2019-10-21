# -*- coding: utf-8 -*-
# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from contextlib import contextmanager

from odoo import fields, models

from odoo.addons.component.core import Component

from .models_mixin import TestMixin


class SeBackendFake(models.Model, TestMixin):

    _name = "se.backend.fake"
    _inherit = "se.backend.spec.abstract"
    _description = "Unit Test SE Backend"


class SeAdapterFake(Component):
    _name = "se.adapter.fake"
    _inherit = "base.backend.adapter"
    _usage = "se.backend.adapter"
    _collection = SeBackendFake._name
    _record_id_key = "id"

    def index(self, data):
        self._mocked_calls.append(
            dict(work_ctx=self.work.__dict__, method="index", args=data)
        )

    def delete(self, binding_ids):
        self._mocked_calls.append(
            dict(work_ctx=self.work.__dict__, method="delete", args=binding_ids)
        )

    def clear(self):
        self._mocked_calls.append(
            dict(work_ctx=self.work.__dict__, method="clear", args=None)
        )

    def iter(self):
        self._mocked_calls.append(
            dict(work_ctx=self.work.__dict__, method="iter", args=None)
        )
        return [{"id": 42}]

    @classmethod
    @contextmanager
    def mocked_calls(cls):
        """Handle mocking of calls.

        Usage:

            with SeAdapterFake.mocked_calls() as calls:
                # do something, then
                self.assertEqual(calls[0]['method'], 'clear')
                # do more
        """
        cls._mocked_calls = []
        yield cls._mocked_calls
        cls._mocked_calls = []


# Fake partner binding


class BindingResPartnerFake(models.Model, TestMixin):
    _name = "res.partner.binding.fake"
    _inherit = ["se.binding"]
    _inherits = {"res.partner": "record_id"}
    # we need to reference this model for the index
    _test_setup_gen_xid = True

    # TODO: use autosetup fields to handle these fields in mixins
    record_id = fields.Many2one(
        comodel_name="res.partner",
        string="Odoo record",
        required=True,
        ondelete="cascade",
    )


class ResPartnerFake(models.Model, TestMixin):
    _name = "res.partner"
    _inherit = "res.partner"
    _test_teardown_no_delete = True
    _test_purge_fields = ["binding_ids"]

    # TODO: use autosetup fields to handle these fields in mixins
    binding_ids = fields.One2many(
        comodel_name=BindingResPartnerFake._name,
        inverse_name="record_id",
        copy=False,
        string="Bindings",
        context={"active_test": False},
        manual=True,  # required to make teardown work
    )
