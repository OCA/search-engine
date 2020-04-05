# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo.addons.component.core import Component


class SeAdapterFake(Component):
    _name = "se.adapter.fake"
    _inherit = "base.backend.adapter"
    _usage = "se.backend.adapter"
    _collection = "se.backend.fake"
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
