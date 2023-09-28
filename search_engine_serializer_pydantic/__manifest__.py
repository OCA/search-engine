# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Search Engine Serilizer Pydantic",
    "summary": """
        Defines base class for pydantic baser serializer""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["lmignon"],
    "website": "https://github.com/OCA/search-engine",
    "depends": [
        "connector_search_engine",
        "pydantic",
    ],
    "data": [
        "views/se_index.xml",
    ],
    "demo": [],
    "external_dependencies": {
        "python": [
            "pydantic",
        ],
    },
}
