# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector_search_engine.unit.adapter import SeAdapter
from ..backend import algolia
import logging
_logger = logging.getLogger(__name__)


try:
    import algoliasearch
except ImportError:
    _logger.debug('Can not import algoliasearch')


@algolia
class AlgoliaAdapter(SeAdapter):
    _model_name = None

    __pool = {}  # pool of connection

    def __init__(self, connector_env):
        application = connector_env.backend_record.username
        api_key = connector_env.backend_record.password
        rec_index = connector_env.index_record
        if not self.__pool.get(rec_index.id):
            client = algoliasearch.client.Client(application, api_key)
            client_index = client.initIndex(rec_index.name)
            self.__pool[rec_index.id] = client_index
        self.index = self.__pool[rec_index.id]

    def add(self, datas):
        self.index.add_objects(datas)

    def delete(self, binding_ids):
        self.index.delete_objects(binding_ids)
