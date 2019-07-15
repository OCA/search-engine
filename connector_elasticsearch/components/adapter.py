# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _
from odoo.addons.component.core import Component
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import elasticsearch
    import elasticsearch.helpers
except ImportError:
    _logger.debug("Can not import elasticsearch")


class ElasticsearchAdapter(Component):
    _name = "elasticsearch.adapter"
    _inherit = ["base.backend.adapter", "elasticsearch.se.connector"]
    _usage = "se.backend.adapter"

    @property
    def _index_name(self):
        return self.work.index.name.lower()

    def _get_es_client(self):
        backend = self.backend_record

        es = elasticsearch.Elasticsearch([backend.es_server_host])

        if not es.ping():  # pragma: no cover
            raise ValueError("Connect Exception with elasticsearch")

        if not es.indices.exists(self._index_name):
            es.indices.create(
                index=self._index_name, body=self.work.index.config_id.body
            )
        return es

    def index(self, datas):
        es = self._get_es_client()
        dataforbulk = []
        for data in datas:
            # Ensure that the _record_id_key is set for creating/updating
            # the record
            if not data.get(self._record_id_key):
                raise UserError(
                    _("The key %s is missing in the data %s")
                    % (self._record_id_key, data)
                )
            else:
                action = {
                    "_index": self._index_name,
                    "_id": data.get(self._record_id_key),
                    "_source": data,
                }
                dataforbulk.append(action)

        res = elasticsearch.helpers.bulk(es, dataforbulk)
        # checks if number of indexed object and object in datas are equal
        return len(datas) - res[0] == 0

    def delete(self, binding_ids):
        es = self._get_es_client()
        dataforbulk = []
        for binding_id in binding_ids:
            action = {
                "_op_type": "delete",
                "_index": self._index_name,
                "_id": binding_id,
            }
            dataforbulk.append(action)

        res = elasticsearch.helpers.bulk(es, dataforbulk)
        # checks if number of indexed object and object in datas are equal
        return len(binding_ids) - res[0] == 0

    def clear(self):
        es = self._get_es_client()
        res = es.indices.delete(index=self._index_name, ignore=[400, 404])
        # recreate the index
        self._get_es_client()
        return res["acknowledged"]

    def iter(self):
        es = self._get_es_client()
        res = es.search(
            index=self._index_name, filter_path=["hits.hits._source"]
        )
        hits = []
        if res:
            hits = res["hits"]["hits"]
        return [r["_source"] for r in hits]
