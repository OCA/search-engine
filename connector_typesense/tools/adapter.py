# Copyright 2023 Derico
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
import time
from typing import Any, Iterator

from odoo import _
from odoo.exceptions import UserError

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
            raise UserError(
                _("Not Found - The requested resource is not found.")
            ) from exc
        except typesense.RequestUnauthorized as exc:
            raise UserError(_("Unauthorized - Your API key is wrong.")) from exc
        except typesense.TypesenseClientError as exc:
            raise UserError(_("Unable to connect :") + "\n\n" + repr(exc)) from exc

    def index(self, records) -> None:
        """ """
        ts = self._ts_client
        records_for_bulk = ""
        for record in records:
            if "id" in record:
                record["id"] = str(record["id"])
            records_for_bulk += f"{json.dumps(record)}\n"

        _logger.info(f"Bulk import records into {self._index_name}'...")
        res = ts.collections[self._index_name].documents.import_(
            records_for_bulk, {"action": "create"}
        )
        res = res.split("\n")
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
        """ """
        ts = self._ts_client
        _logger.info(f"Delete binding_ids: {', '.join(binding_ids)} from collection '{self.index_name}'.")
        res = ts.collections[self._index_name].documents.delete(
            {"filter_by=id": binding_ids}
        )

    def clear(self) -> None:
        """ """
        ts = self._ts_client
        index_name = self._get_current_aliased_index_name() or self._index_name
        _logger.info(f"Clear current_aliased_index_name '{index_name}'.")
        res = ts.collections[index_name].delete()
        self.settings()

    def each(self) -> Iterator[dict[str, Any]]:
        """ """
        ts = self._ts_client
        res = ts.collections[self._index_name].documents.search(
            {
                "q": "*",
            }
        )
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
            index_config.update(
                {
                    "name": aliased_index_name,
                }
            )
            _logger.info(f"Create aliased_index_name '{aliased_index_name}'...")
            client.collections.create(index_config)
            _logger.info(f"Set collection alias '{self._index_name}' >> aliased_index_name '{aliased_index_name}'.")
            client.aliases.upsert(
                self._index_name, {"collection_name": aliased_index_name}
            )

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

    def reindex(self) -> None:
        """Reindex records according to the current config
        This method is useful to allows a rolling update of index
        configuration.
        This process is based on the following steps:
        1. export data from current aliased index
        2. create a new index (collection) with the current config
        3. import data into new aliased index (collection)
        4. Update the index alias to point to the new aliased index (collection)
        5. Drop the old index.
        """
        client = self._ts_client
        current_aliased_index_name = self._get_current_aliased_index_name()
        data = client.collections[current_aliased_index_name].documents.export()
        next_aliased_index_name = self._get_next_aliased_index_name(
            current_aliased_index_name
        )
        try:
            collection = client.collections[next_aliased_index_name].retrieve()
        except typesense.exceptions.ObjectNotFound as e:
            # To allow rolling updates, we work with index aliases
            # index_name / collection_name is part of the schema defined in self._index_config
            _logger.info(f"Create new_aliased_index_name '{next_aliased_index_name}'...")
            index_config = self._index_config
            index_config.update(
                {
                    "name": next_aliased_index_name,
                }
            )
            client.collections.create(index_config)
            _logger.info(f"Import existing data into new_aliased_index_name '{next_aliased_index_name}'...")
            client.collections[next_aliased_index_name].documents.import_(
                data.encode("utf-8"), {"action": "create"}
            )

            try:
                collection = client.collections[next_aliased_index_name].retrieve()
            except typesense.exceptions.ObjectNotFound as e:
                _logger.warn(f"New aliased_index_name not found, skip updating alias and not removing old index (collection)!\n\n{e}")
            else:
                _logger.info(f"Set collection alias '{self._index_name}' >> new_aliased_index_name '{next_aliased_index_name}'.")
                client.aliases.upsert(
                    self._index_name, {"collection_name": next_aliased_index_name}
                )
                _logger.info(f"Remove old aliased index (collection) '{current_aliased_index_name}'.")
                res = client.collections[current_aliased_index_name].delete()

        else:
            _logger.warning(f"next_aliased_index_name '{next_aliased_index_name}' already exists, skip!", self._index_name)



