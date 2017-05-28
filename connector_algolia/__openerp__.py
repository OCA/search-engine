# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Algolia Connector',
    'version': '8.0.0.0.1',
    'category': 'Connector',
    'summary': 'Connector For Algolia Search Engine',
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'images': [],
    'depends': [
        'connector_search_engine',
    ],
    'data': [
        'views/se_view.xml',
    ],
    'demo': [
        'demo/backend_demo.xml',
    ],
    'test': [
    ],
    'external_dependencies': {
        'python': ['algoliasearch'],
        },
    'installable': True,
    'auto_install': False,
    'application': False,
}
