# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.tests.common import (
    CommonTestAdapter,
    TestBindingIndexBase,
)

# NOTE: if you need to refresh tests, you can fire up an ElasticSearch instance
# using `docker-compose.elasticsearch.example.yml` in this same folder.
# If you are not running in a docker env, you'll need to add an alias
# in /etc/hosts to make "elastic" name point to 127.0.0.1


class TestConnectorElasticsearch(CommonTestAdapter, TestBindingIndexBase):
    _backend_xml_id = "connector_elasticsearch.backend_1"

    @classmethod
    def _se_index_config(cls):
        return {"name": "my_config", "body": {"mappings": {}}}
