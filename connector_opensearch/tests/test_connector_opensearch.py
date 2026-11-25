# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.connector_search_engine.tests.common import (
    CommonTestAdapter,
    TestBindingIndexBase,
)

_logger = logging.getLogger(__name__)

# NOTE: if you need to refresh tests, you can fire up an OpenSearch instance
# using `docker-compose.opensearch.example.yml` in this same folder.
# If you are not running in a docker env, you'll need to add an alias
# in /etc/hosts to make "opensearch" name point to 127.0.0.1

try:
    import opensearchpy
    import opensearchpy.helpers
except ImportError:
    _logger.debug("Can not import opensearchpy")


class TestConnectorOpensearch(CommonTestAdapter, TestBindingIndexBase):
    _backend_xml_id = "connector_opensearch.backend_1"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # gzip embeds a timestamp in its header, so a compressed request
        # body is never byte-identical across runs: keep it off so VCR
        # cassettes (matched on raw_body) replay deterministically.
        cls.backend.os_http_compress = False

    @classmethod
    def _se_index_config(cls):
        return {"name": "my_config", "body": {"mappings": {}}}

    def test_each_with_corrupted_index(self):
        opensearchpy.helpers.bulk(
            self.adapter._os_client,
            [
                # Record with string as id
                {
                    "_index": self.adapter._index_name,
                    "_id": "wtf",
                    "_source": {"name": "I am wrong"},
                },
                # Record with a wrong ID
                {
                    "_index": self.adapter._index_name,
                    "_id": 42,
                    "_source": {
                        "id": 3,
                        "name": "Who I am ?",
                    },
                },
            ],
        )
        self._wait_search_engine()
        res = list(self.adapter.each())
        self.assertEqual(
            res,
            [
                {"id": "wtf", "name": "I am wrong"},
                {"id": 42, "name": "Who I am ?"},
            ],
        )
