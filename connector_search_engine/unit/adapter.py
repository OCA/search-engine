# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector.unit.backend_adapter import BackendAdapter
from ..backend import se


@se
class SeAdapter(BackendAdapter):
    _model_name = None

    @classmethod
    def match(cls, session, model):
        return True  # We are a generic exporter; how cool is that?

    def add(self, datas):
        return NotImplemented

    def delete(self, binding_ids):
        return NotImplemented
