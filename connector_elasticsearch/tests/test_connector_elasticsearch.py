# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.connector_search_engine.tests.common import (
    CommonTestAdapter,
    TestBindingIndexBase,
)

_logger = logging.getLogger(__name__)

# NOTE: if you need to refresh tests, you can fire up an ElasticSearch instance
# using `docker-compose.elasticsearch.example.yml` in this same folder.
# If you are not running in a docker env, you'll need to add an alias
# in /etc/hosts to make "elastic" name point to 127.0.0.1

try:
    import elasticsearch
    import elasticsearch.helpers
except ImportError:
    _logger.debug("Can not import elasticsearch")


class TestConnectorElasticsearch(CommonTestAdapter, TestBindingIndexBase):
    _backend_xml_id = "connector_elasticsearch.backend_1"

    @classmethod
    def _se_index_config(cls):
        return {"name": "my_config", "body": {"mappings": {}}}

    def test_each_with_corrupted_index(self):
        elasticsearch.helpers.bulk(
            self.adapter._es_client,
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
