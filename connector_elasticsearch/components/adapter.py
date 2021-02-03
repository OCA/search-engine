# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)

try:
    import elasticsearch
    import elasticsearch.helpers
except ImportError:
    _logger.debug("Can not import elasticsearch")


def _is_delete_nonexistent_documents(elastic_exception):
    """True iff all errors in this exception are deleting a nonexisting document."""
    b = lambda d: "delete" in d and d["delete"]["status"] == 404  # noqa
    return all(b(error) for error in elastic_exception.errors)


class ElasticsearchAdapter(Component):
    _name = "elasticsearch.adapter"
    _inherit = ["se.backend.adapter", "elasticsearch.se.connector"]
    _usage = "se.backend.adapter"

    @property
    def _index_name(self):
        return self.work.index.name.lower()

    @property
    def _es_connection_class(self):
        return elasticsearch.RequestsHttpConnection

    def _get_es_client(self):
        backend = self.backend_record

        es = elasticsearch.Elasticsearch(
            [backend.es_server_host], connection_class=self._es_connection_class
        )

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
        try:
            elasticsearch.helpers.bulk(es, dataforbulk)
        except elasticsearch.helpers.errors.BulkIndexError as e:
            # if the document we are trying to delete does not exist,
            # we can consider deletion a success (there is nothing to do).
            if not _is_delete_nonexistent_documents(e):
                raise e
            msg = "Trying to delete non-existent documents. Ignored: %s"
            _logger.info(msg, e)

    def clear(self):
        es = self._get_es_client()
        res = es.indices.delete(index=self._index_name, ignore=[400, 404])
        # recreate the index
        self._get_es_client()
        return res["acknowledged"]

    def iter(self):
        # `iter` is a built-in keyword -> to be replaced
        _logger.warning("DEPRECATED: use `each` instead of `iter`.")
        return self.each()

    def each(self):
        es = self._get_es_client()
        res = es.search(index=self._index_name, filter_path=["hits.hits._source"])
        hits = res["hits"]["hits"]
        return [r["_source"] for r in hits]
