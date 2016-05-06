# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging
from openerp.addons.connector.unit.synchronizer import Exporter
from openerp.exceptions import UserError
from ..connector import get_environment
from ..backend import nosql

_logger = logging.getLogger(__name__)


@nosql
class NosqlExporter(Exporter):

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(NosqlExporter, self).__init__(environment)
        self.bindings = None

    def get_export_func(self):
        """ Should return the delay export func of the binding """
        return NotImplemented

    def _add(self, data):
        """ Create the SolR record """
        return self.backend_adapter.add(data)

    def _export_data(self):
        return NotImplemented

    def run(self, binding_ids):
        """ Run the synchronization
        :param binding_id: identifier of the binding record to export
        """
        self.bindings = self.model.browse(binding_ids)
        datas = []
        for binding in self.bindings:
            self.binding = binding
            map_record = self.mapper.map_record(binding)
            datas.append(map_record.values())
        return self._add(datas)


def export_record_nosql(session, model_name, binding_ids):
    # check that all binding believe to the same index
    res = session.env[model_name].read_group(
        [('id', 'in', binding_ids)],
        ['id', 'index_id'],
        ['index_id'])
    if len(res) > 1:
        raise UserError('Binding do not believe to the same index')
    index_id = res[0]['index_id'][0]
    env = get_environment(session, model_name, index_id)
    exporter = env.get_connector_unit(NosqlExporter)
    return exporter.run(binding_ids)
