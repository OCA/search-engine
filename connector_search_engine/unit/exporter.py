# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import Exporter
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)


class SearchEngineExporter(Exporter):

    @classmethod
    def match(cls, session, model):
        return True  # We are a generic exporter; how cool is that?

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(SearchEngineExporter, self).__init__(environment)
        self.bindings = None

    def _add(self, data):
        """ Create the SolR record """
        return self.backend_adapter.add(data)

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


def export_record_search_engine(get_env, session, model_name, binding_ids):
    # check that all binding believe to the same backend
    res = session.env[model_name].read_group(
        [('id', 'in', binding_ids)],
        ['id', 'backend_id'],
        ['backend_id'])
    if len(res) > 1:
        raise UserError('Binding do not believe to the same backend')
    env = get_env(session, model_name, res[0]['backend_id'][0])
    exporter = env.get_connector_unit(SearchEngineExporter)
    return exporter.run(binding_ids)
