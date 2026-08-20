# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "connector_opensearch",
    "category": "Connector",
    "summary": "Connector For OpenSearch Search Engine",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "depends": ["connector_search_engine"],
    "data": [
        "views/se_backend.xml",
    ],
    "demo": ["demo/backend_demo.xml"],
    "external_dependencies": {"python": ["opensearch-py>=3.2.0,<4"]},
    "installable": True,
}
