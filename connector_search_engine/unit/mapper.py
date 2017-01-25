# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector.unit.mapper import ExportMapper
from ..backend import se

import logging

_logger = logging.getLogger(__name__)


#@se
class JsonExportMapper(ExportMapper):

#    @classmethod
#    def match(cls, session, model):
#        """ Generic json mapper """
#        if cls._model_name is None:
#            return True
#        else:
#            return super(JsonExportMapper, cls).match(session, model)
#
    def __init__(self, connector_env):
        """
        :param connector_env: current environment (backend, session, ...)
        :type connector_env: :py:class:`connector.connector.Environment`
        """
        super(JsonExportMapper, self).__init__(connector_env)
        exporter = self.connector_env.index_record.exporter_id
        self._json_parser = exporter.get_json_parser()
        if 'id' not in self._json_parser:
            self._json_parser.append('id')

    def _apply(self, map_record, options=None):
        return map_record._source.jsonify(self._json_parser)[0]
