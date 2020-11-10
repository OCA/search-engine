# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Connector Search Engine",
    "version": "13.0.2.1.1",
    "author": "Akretion,"
    "ACSONE SA/NV,"
    "Camptocamp,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": ["connector", "base_jsonify", "server_environment"],
    "external_dependencies": {"python": ["unidecode"]},
    "data": [
        "security/connector_search_engine_security.xml",
        "security/se_index_config.xml",
        "security/ir.model.access.csv",
        "views/se_backend.xml",
        "views/se_menu.xml",
        "views/se_index_config.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
}
