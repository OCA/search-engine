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

    def _get_index(self):
        backend = self.backend_record
        client = algoliasearch.client.Client(
            backend.username, backend.password)
        return client.initIndex(self.connector_env.index_record.name)

    def add(self, datas):
        index = self._get_index()
        index.add_objects(datas)

    def delete(self, binding_ids):
        index = self._get_index()
        index.delete_objects(binding_ids)
