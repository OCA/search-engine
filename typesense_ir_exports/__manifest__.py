# Copyright 2023 Kencove (https://kencove.com).
# @author Mohamed Alkobrosli <malkobrosly@kencove.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Typesense Serializer Ir Export",
    "summary": "Use Exporter (ir.exports) as serializer for index",
    "version": "16.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/search-engine",
    "author": "Kencove, Odoo Community Association (OCA)",
    "maintainers": ["Kencove"],
    "license": "AGPL-3",
    "development_status": "Alpha",
    "depends": [
        "connector_search_engine_serializer_ir_export",
    ],
    "data": [
        "data/se_index_config_data.xml",
        "views/se_index_view.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "typesense_ir_exports/static/src/action_ir_export.xml",
            "typesense_ir_exports/static/src/action_ir_export.esm.js",
        ],
    },
}
