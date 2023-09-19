# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent


class SeAdapter(AbstractComponent):
    _name = "se.backend.adapter"
    _inherit = ["base.se.connector", "base.backend.adapter"]
    _usage = "se.backend.adapter"

    @classmethod
    def match(cls, session, model):
        # We are a generic exporter; how cool is that?
        return True  # pragma: no cover

    def index(self, datas):
        raise NotImplementedError()

    def delete(self, binding_ids):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    def each(self):
        raise NotImplementedError()

    def settings(self, force=False):
        raise NotImplementedError()

    def external_id(self, record):
        return record[self._record_id_key]
