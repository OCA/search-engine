# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from contextlib import contextmanager

from odoo import fields, models

from odoo.addons.component.core import Component


class SeBackend(models.Model):
    _inherit = "se.backend"

    backend_type = fields.Selection(
        selection_add=[("fake", "Fake")], ondelete={"fake": "cascade"}
    )


class SeAdapterFake(Component):
    _name = "se.adapter.fake"
    _inherit = "se.backend.adapter"
    _usage = "se.backend.adapter"
    _collection = "se.backend"

    def __init__(self, work_context):
        super().__init__(work_context)
        if not hasattr(self, "_mocked_calls"):
            # Not using the context manager below
            self._mocked_calls = []

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

    def each(self):
        self._mocked_calls.append(
            dict(work_ctx=self.work.__dict__, method="each", args=None)
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


class SeBinding(models.Model):
    _inherit = "se.binding"

    # TODO see if we can remove this as it's for test only
    def export_record(self):
        # You can set `call_tracking` as a list in ctx to collect the results.
        res = super().export_record()
        if "call_tracking" in self.env.context:
            self.env.context["call_tracking"].append(res)
        return res

    def delete_record(self):
        # You can set `call_tracking` as a list in ctx to collect the results.
        res = super().delete_record()
        if "call_tracking" in self.env.context:
            self.env.context["call_tracking"].append(res)
        return res


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "se.indexable.record"]

    index_bind_ids = fields.One2many(domain=[("res_model", "=", "res.partner")])
