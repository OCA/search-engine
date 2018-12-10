# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Connector Search Engine',
    'version': '10.0.0.0.1',
    'author': 'Akretion,ACSONE SA/NV',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'depends': [
        'connector',
        'base_jsonify',
        'keychain',
    ],
    'data': [
        'views/se_backend.xml',
        'views/se_menu.xml',
        'data/ir_cron.xml',
        'security/connector_search_engine_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
