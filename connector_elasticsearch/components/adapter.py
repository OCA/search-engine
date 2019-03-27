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

    @property
    def _doc_type(self):
        return self.work.index.config_id.doc_type

    def _get_es(self):
        backend = self.backend_record

        es = elasticsearch.Elasticsearch(
            [
                {
                    "host": backend.elasticsearch_server_ip,
                    "port": int(backend.elasticsearch_server_port),
                }
            ]
        )

        if not es.ping():
            raise ValueError("Connect Exception with elasticsearch")

        if not es.indices.exists(self._index_name):
            es.indices.create(
                index=self._index_name, body=self.work.index.config_id.body
            )
        return es

    def index(self, datas):
        es = self._get_es()
        dataforbulk = []
        for data in datas:
            # Ensure that the objectID is set for creating/updating the record
            if not data.get("objectID"):
                raise UserError(
                    _("The key objectID is missing in the data %s") % data
                )
            else:
                action = {
                    "_index": self._index_name,
                    "_type": self._doc_type,
                    "_id": data.get("objectID"),
                    "_source": data,
                }
                dataforbulk.append(action)

        res = elasticsearch.helpers.bulk(es, dataforbulk)
        # checks if number of indexed object and object in datas are equal
        return len(datas) - res[0] == 0

    def delete(self, binding_ids):
        es = self._get_es()
        res = es.delete(
            index=self._index_name, doc_type=self._doc_type, id=binding_ids
        )
        return res

    def clear(self):
        es = self._get_es()
        res = es.indices.delete(index=self._index_name, ignore=[400, 404])
        # recreate the index
        self._get_es()
        return res["acknowledged"]
