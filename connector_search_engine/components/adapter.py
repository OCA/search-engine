# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import AbstractComponent


class SeAdapter(AbstractComponent):
    _name = 'se.backend.adapter'
    _inherit = ['base.se.connector', 'base.backend.adapter']
    _usage = 'se.backend.adapter'

    @classmethod
    def match(cls, session, model):
        return True  # We are a generic exporter; how cool is that?

    def add(self, datas):
        return NotImplemented

    def delete(self, binding_ids):
        return NotImplemented
