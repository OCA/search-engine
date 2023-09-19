# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "connector_elasticsearch",
    "category": "Connector",
    "summary": "Connector For Elasticsearch Search Engine",
    "version": "12.0.0.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "http://www.acsone.eu",
    "depends": [
        "connector_search_engine",
        "connector",
        "component",
        "base_jsonify",
    ],
    "data": [
        "security/se_backend_elasticsearch.xml",
        "security/se_index_config.xml",
        "views/se_index_config.xml",
        "views/se_backend_elasticsearch.xml",
        "views/se_menu.xml",
    ],
    "demo": ["demo/backend_demo.xml"],
    "external_dependencies": {"python": ["elasticsearch"]},
}
