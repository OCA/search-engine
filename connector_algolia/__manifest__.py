# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Algolia Connector',
    'version': '10.0.0.0.1',
    'category': 'Connector',
    'summary': 'Connector For Algolia Search Engine',
    'author': 'Akretion,ACSONE SA/NV',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'images': [],
    'depends': [
        'connector_search_engine',
        'connector',
        'component',
        'base_jsonify',
    ],
    'data': [
        'views/se_backend_algolia.xml',
        'views/se_menu.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/backend_demo.xml',
    ],
    'external_dependencies': {
        'python': ['algoliasearch'],
    },
    'installable': True,
    'application': False,
}
