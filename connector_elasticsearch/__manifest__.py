# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "connector_elasticsearch",
    "category": "Connector",
    "summary": "Connector For Elasticsearch Search Engine",
    "version": "14.0.2.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "depends": [
        "connector_search_engine",
        "connector",
        "component",
        "base_jsonify",
        "server_environment",
    ],
    "data": [
        "security/se_backend_elasticsearch.xml",
        "views/se_backend_elasticsearch.xml",
        "views/se_menu.xml",
    ],
    "demo": ["demo/backend_demo.xml"],
    # TODO: Get latest improvements from elasticsearch library
    "external_dependencies": {"python": ["elasticsearch>=7.0.0,<=7.13.4", "requests"]},
    "installable": True,
}
