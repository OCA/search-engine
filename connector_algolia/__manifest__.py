# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Algolia Connector",
    "version": "12.0.3.0.1",
    "category": "Connector",
    "summary": "Connector For Algolia Search Engine",
    "author": "Akretion,"
    "ACSONE SA/NV,"
    "Camptocamp,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "license": "AGPL-3",
    "depends": ["connector_search_engine", "connector", "component", "base_jsonify"],
    "data": [
        "views/se_backend_algolia.xml",
        "views/se_menu.xml",
        "security/ir.model.access.csv",
        "security/se_index_config.xml",
    ],
    "demo": ["demo/backend_demo.xml"],
    "external_dependencies": {"python": ["algoliasearch"]},
    "installable": True,
}
