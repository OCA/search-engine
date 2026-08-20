# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import time

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.connector_search_engine.tools.adapter import SearchEngineAdapter

_logger = logging.getLogger(__name__)


try:
    import opensearchpy
    import opensearchpy.helpers
except ImportError:
    _logger.debug("Can not import opensearchpy")


class OpenSearchAdapter(SearchEngineAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__os_client = None

    @property
    def _index_name(self):
        return self.index_record.name.lower()

    @property
    def _index_config(self):
        return self.index_record.config_id.body

    @property
    def _os_connection_class(self):
        return opensearchpy.Urllib3HttpConnection

    @property
    def _os_client(self):
        if not self.__os_client:
            self.__os_client = self._get_os_client()
        return self.__os_client

    def _get_os_client(self):
        backend = self.backend_record
        kwargs = {
            "connection_class": self._os_connection_class,
            "http_compress": backend.os_http_compress,
            "timeout": max(backend.os_timeout, 1),
            "retry_on_timeout": backend.os_retry_on_timeout,
            "max_retries": max(0, backend.os_max_retries),
        }
        if backend.os_auth_type == "api_key":
            kwargs["api_key"] = (
                (backend.os_api_key_id, backend.os_api_key)
                if backend.os_api_key_id and backend.os_api_key
                else None
            )
        elif backend.os_auth_type == "http":
            kwargs["http_auth"] = (backend.os_user, backend.os_password)
            kwargs["use_ssl"] = backend.os_ssl
        return opensearchpy.OpenSearch([backend.os_server_host], **kwargs)

    def test_connection(self):
        es = self._os_client
        try:
            es.info()
        except opensearchpy.NotFoundError as exc:
            raise UserError(_("Unable to reach host.")) from exc
        except opensearchpy.AuthenticationException as exc:
            raise UserError(_("Unable to authenticate. Check credentials.")) from exc
        except Exception as exc:
            raise UserError(_("Unable to connect :") + "\n\n" + repr(exc)) from exc

    def index(self, records) -> None:
        es = self._os_client
        records_for_bulk = [
            {
                "_index": self._index_name,
                "_id": record["id"],
                "_source": record,
            }
            for record in records
        ]
        res = opensearchpy.helpers.bulk(es, records_for_bulk)
        # checks if number of indexed object and object in records are equal
        if not res[0] == len(records):
            raise SystemError(
                _(
                    "Unable to index all records. (indexed: %(indexed)s, "
                    "total: %(total)s)\n%(result)s",
                    indexed=res[0],
                    total=len(records),
                    result=res,
                )
            )

    def delete(self, binding_ids) -> None:
        es = self._os_client
        records_for_bulk = [
            {
                "_op_type": "delete",
                "_index": self._index_name,
                "_id": binding_id,
            }
            for binding_id in binding_ids
        ]
        # Deleting a document that does not exist returns a 404 for that
        # item. The end result (document absent from the index) is what we
        # want, so such failures are ignored instead of raising.
        opensearchpy.helpers.bulk(es, records_for_bulk, ignore_status=(404,))

    def clear(self) -> None:
        es = self._os_client
        index_name = self._get_current_aliased_index_name() or self._index_name
        res = es.indices.delete(index=index_name, ignore=[400, 404])
        self.settings()
        # A missing "acknowledged" key means the delete's error status (400
        # or 404, i.e. the index was already absent) was ignored above: the
        # end result (index gone) is what we want, so treat it as a success.
        if not res.get("acknowledged", True):
            raise SystemError(
                _(
                    "Unable to clear index %(index_name)s: %(result)",
                    index_name=index_name,
                    result=res,
                )
            )

    def each(self, fetch_fields=None):
        es = self._os_client
        query = {}
        if fetch_fields:
            query["_source"] = fetch_fields
        # helpers.scan owns the scroll lifecycle (including clearing it once
        # exhausted), unlike a hand-rolled search/scroll loop.
        for item in opensearchpy.helpers.scan(
            es,
            index=self._index_name,
            query=query,
            scroll="5m",
            size=1000,
        ):
            # In OpenSearch the real id is "_id", so we force it
            try:
                real_id = int(item["_id"])
            except ValueError:
                # In that case there is something wrong
                # normally we should only have integer
                # but we still set the _id like that
                # so the resynchronize mecanism will fix it
                real_id = item["_id"]
            info = item["_source"]
            info["id"] = real_id
            yield info

    def settings(self) -> None:
        es = self._os_client
        if not es.indices.exists(index=self._index_name):
            # To allow rolling updates, we work with index aliases
            aliased_index_name = self._get_next_aliased_index_name()
            es.indices.create(index=aliased_index_name, body=self._index_config)
            es.indices.put_alias(index=aliased_index_name, name=self._index_name)
            _logger.info("Missing index %s created.", self._index_name)

    def _get_current_aliased_index_name(self) -> str:
        """Get the current aliased index name if any"""
        current_aliased_index_name = None
        alias = self._os_client.indices.get_alias(
            name=self._index_name, ignore=[400, 404]
        )
        if "error" not in alias:
            current_aliased_index_name = next(iter(alias))  # get the first key
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
        return "%s-%d" % (self._index_name, next_version)

    def reindex(self) -> None:
        """Reindex records according to the current config

        This method is useful to allows a rolling update of index
        configuration.
        This process is based on the following steps:
        1. create a new index with the current config
        2. trigger a reindex into SE from the current index to the new one
        3. Update the index alias to point to the new index
        4. Drop the old index.
        """
        client = self._os_client
        current_aliased_index_name = self._get_current_aliased_index_name()
        next_aliased_index_name = self._get_next_aliased_index_name(
            current_aliased_index_name
        )
        client.indices.create(index=next_aliased_index_name, body=self._index_config)
        task_def = client.reindex(
            body={
                "source": {"index": self._index_name},
                "dest": {"index": next_aliased_index_name},
            },
            request_timeout=9999999,
            wait_for_completion=False,
        )
        while True:
            time.sleep(5)
            _logger.info("Waiting for task completion %s", task_def)
            task = client.tasks.get(task_id=task_def["task"], wait_for_completion=False)
            if task.get("completed"):
                break
        if current_aliased_index_name:
            client.indices.update_aliases(
                body={
                    "actions": [
                        {
                            "remove": {
                                "index": current_aliased_index_name,
                                "alias": self._index_name,
                            },
                        },
                        {
                            "add": {
                                "index": next_aliased_index_name,
                                "alias": self._index_name,
                            }
                        },
                    ]
                }
            )
            client.indices.delete(index=current_aliased_index_name, ignore=[400, 404])
        else:
            # This code will only be triggered the first time the reindex is
            # called on an index created before the use of index aliases.
            client.indices.delete(index=self._index_name, ignore=[400, 404])
            client.indices.put_alias(
                index=next_aliased_index_name, name=self._index_name
            )
