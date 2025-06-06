# Copyright 2024 Derico
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from typing import Any, Iterator

import requests

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.connector_search_engine.tools.adapter import SearchEngineAdapter

_logger = logging.getLogger(__name__)


try:
    import typesense
except ImportError:
    _logger.debug("Can not import typesense")


class TypesenseAdapter(SearchEngineAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__ts_client = None

    @property
    def _index_name(self):
        return self.index_record.name.lower()

    @property
    def _ts_client(self):
        if not self.__ts_client:
            self.__ts_client = self._get_ts_client()
        return self.__ts_client

    @property
    def _collections(self):
        return self._ts_client.collections

    def _get_ts_client(self):
        backend = self.backend_record
        return typesense.Client(
            {
                "nodes": [
                    {
                        "host": backend.ts_server_host,
                        "port": backend.ts_server_port,
                        "protocol": backend.ts_server_protocol,
                    }
                ],
                "api_key": backend.ts_api_key,
                "connection_timeout_seconds": int(backend.ts_server_timeout) or 300,
            }
        )

    def test_connection(self):
        try:
            self._collections.retrieve()
        except typesense.exceptions.ObjectNotFound as exc:
            raise UserError(
                _("Not Found - The requested resource is not found.")
            ) from exc
        except typesense.exceptions.RequestUnauthorized as exc:
            raise UserError(_("Unauthorized - Your API key is wrong.")) from exc
        except requests.exceptions.ConnectionError as exc:
            raise UserError(_("Unable to connect :") + "\n\n" + repr(exc)) from exc
        except requests.exceptions.InvalidURL as exc:
            raise UserError(
                _("Invalid URL - No host supplied") + "\n\n" + repr(exc)
            ) from exc

    def index(self, records) -> None:
        # With typesense id must be a string so we have to convert
        # the id into a string
        items = []
        for record in records:
            item = record.copy()
            item["id"] = str(item["id"])
            items.append(item)
        try:
            res = self._collections[self._index_name].documents.import_(
                items, {"action": "upsert"}
            )
        except typesense.exceptions.ObjectNotFound as e:
            _logger.warning(
                f"{self._index_name} not found, creating a new index (collection)!"
                f" and index records\n\n{e}"
            )
            self.settings()
            self.index(items)

        errors = len([item for item in res if not item.get("success")])
        if errors:
            raise UserError(
                _(
                    "Unable to index all records. (nbr errors: %(errors)s, "
                    "total: %(total)s)\n%(result)s",
                    indexed=len(res),
                    total=len(records),
                    result=res,
                )
            )

    def delete(self, binding_ids) -> None:
        self._collections[self._index_name].documents.delete(
            {"filter_by": f"id:{binding_ids}"}
        )

    def clear(self) -> None:
        try:
            self._collections[self._index_name].delete()
        except typesense.exceptions.ObjectNotFound:
            _logger.debug(
                "Index %s do not exist, no need to clear it" % self._index_name
            )
        self.settings()

    def each(self, fetch_fields=None) -> Iterator[dict[str, Any]]:
        params = {"per_page": 250, "q": "*", "page": 1}
        if fetch_fields:
            params["include_fields"] = fetch_fields
        res = self._collections[self._index_name].documents.search(params)
        while True:
            for hit in res["hits"]:
                try:
                    hit["document"]["id"] = int(hit["document"]["id"])
                except ValueError:
                    _logger.warning(
                        "Fail to convert id %s into an integer" % hit["document"]["id"]
                    )
                    # In that case there is something wrong
                    # normally we should only have integer
                    # let's the resynchronize mecanism fix it
                yield hit["document"]
            if len(res["hits"]) < 250:
                break
            params["page"] += 1
            res = self._collections[self._index_name].documents.search(params)

    def _prepare_params_for_new_config(self, new_config, current_config):
        """We choose to have a simple implementation of update of the configuration
        Typesense have a great UI https://github.com/bfritscher/typesense-dashboard
        So the best is to manage advanced config their.
        So we only support adding new field. No remove, no update
        if you want to do it you can inherit this method
        """
        existing_fields = {field["name"] for field in current_config["fields"]}
        fields_to_add = [
            field
            for field in new_config["fields"]
            if field["name"] not in existing_fields
        ]
        if fields_to_add:
            return {"fields": fields_to_add}
        else:
            return {}

    def settings(self) -> None:
        config = self.index_record.config_id.body
        try:
            res = self._collections[self._index_name].retrieve()
        except typesense.exceptions.ObjectNotFound:
            config["name"] = self._index_name
            self._collections.create(config)
        else:
            config = self._prepare_params_for_new_config(config, res)
            if config:
                self._collections[self._index_name].update(config)

    def reindex(self) -> None:
        raise UserError(
            _(
                "Reindexing is not needed with TypeSense, as schema can be updated. "
                "So you just need to export the setting after changing them"
            )
        )
