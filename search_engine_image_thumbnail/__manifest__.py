# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Search Engine Multi Image Thumbnail",
    "summary": """
        Generate thumbnails for binded record""",
    "version": "16.0.1.0.3",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "depends": [
        "base_partition",
        "connector_search_engine",
        "fs_image_thumbnail",
        "fs_base_multi_image",
    ],
    "maintainers": ["lmignon"],
    "development_status": "Alpha",
    "data": [
        "security/se_image_field_thumbnail_size.xml",
        "security/se_thumbnail_size.xml",
        "security/se_thumbnail.xml",
        "views/ir_attachment.xml",
        "views/se_menu.xml",
        "views/se_backend.xml",
        "views/se_index.xml",
        "views/se_image_field_thumbnail_size.xml",
        "views/se_thumbnail.xml",
        "views/se_thumbnail_size.xml",
    ],
    "demo": [],
}
