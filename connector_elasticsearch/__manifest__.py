# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "connector_elasticsearch",
    "category": "Connector",
    "summary": "Connector For Elasticsearch Search Engine",
    "version": "16.0.0.3.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "depends": ["connector_search_engine"],
    "data": [
        "views/se_backend.xml",
    ],
    "demo": ["demo/backend_demo.xml"],
    # TODO: Get latest improvements from elasticsearch library
    "external_dependencies": {
        "python": [
            "elasticsearch>=8.0.0,<9.0.0",
            "elastic-transport>=8.15.1,<9.0.0",
            "requests",
        ]
    },
    "installable": True,
}
