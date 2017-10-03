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

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(SeExporter, self).__init__(environment)
        self.bindings = None

    def _add(self, data):
        """ Create the SolR record """
        return self.backend_adapter.add(data)

    def _export_data(self):
        return NotImplemented

    def run(self):
        """ Run the synchronization
        :param binding_id: identifier of the binding record to export
        """
        datas = []
        for record in self.work.records:
            map_record = self.mapper.map_record(record)
            datas.append(map_record.values())
        return self._add(datas)
