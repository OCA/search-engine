# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Connector Search Engine',
 'version': '8.0.0.0.1',
 'author': 'Akretion',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'depends': [
     'connector',
     'base_jsonify',
 ],
 'data': [
     'views/se_view.xml',
     'views/se_menu.xml',
     'security/ir.model.access.csv',
 ],
 'installable': True,
 'application': False,
 }
