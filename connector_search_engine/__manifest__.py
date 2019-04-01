# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Connector Search Engine",
    "version": "10.0.2.0.0",
    "author": "Akretion,"
    "ACSONE SA/NV,"
    "Camptocamp,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": ["connector", "base_jsonify"],
    "external_dependencies": {"python": ["unidecode"]},
    "data": [
        "views/se_backend.xml",
        "views/se_menu.xml",
        "data/ir_cron.xml",
        "security/connector_search_engine_security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
