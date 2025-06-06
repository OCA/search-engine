# Copyright 2024 Derico
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "connector_typesense",
    "category": "Connector",
    "summary": "Connector For Typesense Search Engine",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Derico, Kencove, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "maintainers": [],
    "depends": ["connector_search_engine"],
    "data": [
        "views/ts_backend.xml",
    ],
    "demo": [
        "demo/backend_demo.xml",
    ],
    "external_dependencies": {"python": ["typesense>=1.1.0", "requests"]},
    "installable": True,
}
