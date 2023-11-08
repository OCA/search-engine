# Copyright 2023 Derico
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import time
from typing import Any, Iterator

from odoo import _
from odoo.exceptions import UserError
from pprint import pprint

from odoo.addons.connector_search_engine.tools.adapter import SearchEngineAdapter

_logger = logging.getLogger(__name__)


try:
    import typesense
except ImportError:
    _logger.debug("Can not import typesense")


# def _is_delete_nonexistent_documents(elastic_exception):
#     """True iff all errors in this exception are deleting a nonexisting document."""
#     b = lambda d: "delete" in d and d["delete"]["status"] == 404  # noqa
#     return all(b(error) for error in elastic_exception.errors)


class TypesenseAdapter(SearchEngineAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__ts_client = None

    @property
    def _index_name(self):
        return self.index_record.name.lower()

    # @property
    # def _es_connection_class(self):
    #     return elasticsearch.RequestsHttpConnection

    @property
    def _ts_client(self):
        if not self.__ts_client:
            self.__ts_client = self._get_ts_client()
        return self.__ts_client

    @property
    def _index_config(self):
        return self.index_record.config_id.body

    def _get_ts_client(self):
        backend = self.backend_record
        return typesense.Client(
            {
                "nodes": [
                    {
                        "host": backend.ts_server_host,  # For Typesense Cloud use xxx.a1.typesense.net
                        "port": backend.ts_server_port,  # For Typesense Cloud use 443
                        "protocol": backend.ts_server_protocol,  # For Typesense Cloud use https
                    }
                ],
                "api_key": backend.api_key,
                "connection_timeout_seconds": int(backend.ts_server_timeout) or 300,
            }
        )

    def test_connection(self):
        ts = self._ts_client
        try:
            ts.collections.retrieve()
        except typesense.exceptions.ObjectNotFound as exc:
            raise UserError(_("Not Found - The requested resource is not found.")) from exc
        except typesense.RequestUnauthorized as exc:
            raise UserError(_("Unauthorized - Your API key is wrong.")) from exc
        except typesense.TypesenseClientError as exc:
            raise UserError(_("Unable to connect :") + "\n\n" + repr(exc)) from exc

    def index(self, records) -> None:
        """
        """
        ts = self._ts_client
        records_for_bulk = "\n".join(records)
        pprint(records_for_bulk)
        res = ts.collections[self._index_name].documents.import_(records_for_bulk, {'action': 'create'})
        print(res)
        res = res.split("\n")
        # res = elasticsearch.helpers.bulk(es, records_for_bulk)
        # checks if number of indexed object and object in records are equal
        if not len(res) == len(records):
            raise SystemError(
                _(
                    "Unable to index all records. (indexed: %(indexed)s, "
                    "total: %(total)s)\n%(result)s",
                    indexed=len(res),
                    total=len(records),
                    result=res,
                )
            )

    def delete(self, binding_ids) -> None:
        """
        """
        ts = self._ts_client
        print(f"delete ids: {binding_ids}")
        res = ts.collections[self._index_name].documents.delete({"filter_by=id": binding_ids})
        print(f"deleted: {res}")

        # records_for_bulk = []
        # for binding_id in binding_ids:
        #     action = {
        #         "_op_type": "delete",
        #         "_index": self._index_name,
        #         "_id": binding_id,
        #     }
        #     records_for_bulk.append(action)
        # try:
        #     elasticsearch.helpers.bulk(es, records_for_bulk)
        # except elasticsearch.helpers.errors.BulkIndexError as e:
        #     # if the document we are trying to delete does not exist,
        #     # we can consider deletion a success (there is nothing to do).
        #     if not _is_delete_nonexistent_documents(e):
        #         raise e
        #     msg = "Trying to delete non-existent documents. Ignored: %s"
        #     _logger.info(msg, e)

    def clear(self) -> None:
        """
        """
        ts = self._ts_client
        index_name = self._get_current_aliased_index_name() or self._index_name
        res = ts.collections[index_name].delete()
        print(f"tpyesense clear: {res}")
        # res = es.indices.delete(index=index_name, ignore=[400, 404])
        self.settings()
        # if not res["acknowledged"]:
        #     raise SystemError(
        #         _(
        #             "Unable to clear index %(index_name)s: %(result)",
        #             index_name=index_name,
        #             result=res,
        #         )
        #     )

    def each(self) -> Iterator[dict[str, Any]]:
        """
        """
        ts = self._ts_client
        # res = es.search(index=self._index_name, filter_path=["hits.hits._source"])
        res = ts.collections[self._index_name].documents.search({
            "q": "*",
        })
        pprint(res)
        if not res:
            # eg: empty index
            return
        hits = res["hits"]["documents"]
        for hit in hits:
            yield hit

    def settings(self) -> None:
        ts = self._ts_client
        try:
            collection = ts.collections[self._index_name].retrieve()
        except typesense.exceptions.ObjectNotFound as e:
            client = self._ts_client
            # To allow rolling updates, we work with index aliases
            aliased_index_name = self._get_next_aliased_index_name()
            # index_name / collection_name is part of the schema defined in self._index_config
            index_config = self._index_config
            index_config.update({
                "name": aliased_index_name,
            })
            client.collections.create(index_config)
            # client.indices.create(index=aliased_index_name, body=self._index_config)
            client.aliases.upsert(self._index_name, {"collection_name": aliased_index_name})
            # client.indices.put_alias(index=aliased_index_name, name=self._index_name)
            msg = "Missing index %s created."
            _logger.info(msg, self._index_name)

    def _get_current_aliased_index_name(self) -> str:
        """Get the current aliased index name if any"""
        current_aliased_index_name = None
        alias = self._ts_client.aliases[self._index_name].retrieve()
        if "collection_name" in alias:
            current_aliased_index_name = alias["collection_name"]
        return current_aliased_index_name

    def _get_next_aliased_index_name(
        self, aliased_index_name: str | None = None
    ) -> str:
        """Get the next aliased index name

        The next aliased index name is based on the current aliased index name.
        It's the current aliased index name incremented by 1.

        :param aliased_index_name: the current aliased index name
        :return: the next aliased index name
        """
        next_version = 1
        if aliased_index_name:
            next_version = int(aliased_index_name.split("-")[-1]) + 1
        return f"{self._index_name}-{next_version}"

    # def reindex(self) -> None:
    #     """Reindex records according to the current config
    #     This method is useful to allows a rolling update of index
    #     configuration.
    #     This process is based on the following steps:
    #     1. create a new index with the current config
    #     2. trigger a reindex into SE from the current index to the new one
    #     3. Update the index alias to point to the new index
    #     4. Drop the old index.
    #     """
    #     client = self._ts_client
    #     current_aliased_index_name = self._get_current_aliased_index_name()
    #     next_aliased_index_name = self._get_next_aliased_index_name(
    #         current_aliased_index_name
    #     )
    #     # create new idx
    #     client.indices.create(index=next_aliased_index_name, body=self._index_config)
    #     task_def = client.reindex(
    #         {
    #             "source": {"index": self._index_name},
    #             "dest": {"index": next_aliased_index_name},
    #         },
    #         request_timeout=9999999,
    #         wait_for_completion=False,
    #     )
    #     while True:
    #         time.sleep(5)
    #         _logger.info("Waiting for task completion %s", task_def)
    #         task = client.tasks.get(task_id=task_def["task"], wait_for_completion=False)
    #         if task.get("completed"):
    #             break
    #     if current_aliased_index_name:
    #         client.indices.update_aliases(
    #             body={
    #                 "actions": [
    #                     {
    #                         "remove": {
    #                             "index": current_aliased_index_name,
    #                             "alias": self._index_name,
    #                         },
    #                     },
    #                     {
    #                         "add": {
    #                             "index": next_aliased_index_name,
    #                             "alias": self._index_name,
    #                         }
    #                     },
    #                 ]
    #             }
    #         )
    #         client.indices.delete(index=current_aliased_index_name, ignore=[400, 404])
    #     else:
    #         # This code will only be triggered the first time the reindex is
    #         # called on an index created before the use of index aliases.
    #         client.indices.delete(index=self._index_name, ignore=[400, 404])
    #         client.indices.put_alias(
    #             index=next_aliased_index_name, name=self._index_name
    #         )
