# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from odoo.addons.connector_search_engine.tests.common import CommonTestAdapter

# NOTE: if you need to refresh tests, you can fire up an ElasticSearch instance
# using `docker-compose.elasticsearch.example.yml` in this same folder.
# If you are not running in a docker env, you'll need to add an alias
# in /etc/hosts to make "elastic" name point to 127.0.0.1


class TestConnectorElasticsearch(CommonTestAdapter):
    _backend_xml_id = "connector_elasticsearch.backend_1"

    @classmethod
    def _se_index_config(cls):
        return {"name": "my_config", "body": {"mappings": {}}}

    def test_index_adapter(self):
        super().test_index_adapter()
        self.assertGreaterEqual(len(self.cassette.requests), 1)
        request = self.cassette.requests[-1]
        self.assertEqual(request.method, "POST")
        self.assertEqual(self.parse_path(request.uri), "/_bulk")
        body = request.body.decode("utf-8")
        lines = [line for line in filter(lambda line: line, body.split("\n"))]
        # we must have 2 lines: 1 for the index op and 1 with data
        self.assertEqual(len(lines), 2)
        index_action = json.loads(lines[0])
        self.assertDictEqual(
            index_action,
            {
                "index": {
                    "_index": "demo_elasticsearch_backend_contact_en_us",
                    "_id": "foo",
                }
            },
        )
        index_data = json.loads(lines[1])
        self.assertDictEqual(index_data, {"id": "foo"})
