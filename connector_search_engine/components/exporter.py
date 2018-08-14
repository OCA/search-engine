# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class SeExporter(Component):
    _name = 'se.exporter'
    _inherit = ['base.se.connector', 'base.exporter']
    _usage = 'se.record.exporter'
    _base_mapper_usage = 'se.export.mapper'
    _base_backend_adapter_usage = 'se.backend.adapter'

    def _index(self, data):
        """ Index the record """
        return self.backend_adapter.index(data)

    def run(self):
        """ Run the synchronization """
        self.work.records.write({'sync_state': 'done'})
        return self._index([record.data for record in self.work.records])
