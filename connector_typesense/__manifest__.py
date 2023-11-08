# Copyright 2023 Derico
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "connector_typesense",
    "category": "Connector",
    "summary": "Connector For Typesense Search Engine",
    "version": "16.0.0.0.2",
    "license": "AGPL-3",
    "author": "Derico, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "depends": ["connector_search_engine"],
    "data": [
        "views/ts_backend.xml",
    ],
    # "demo": ["demo/backend_demo.xml"],
    # TODO: Get latest improvements from elasticsearch library
    "external_dependencies": {"python": ["typesense", "requests"]},
    "installable": True,
}
