# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'NoSQL Catalog Indexer',
 'version': '9.0.0.0.1',
 'author': 'Akretion',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'depends': [
     'connector_nosql',
     'connector_base_product',
 ],
 'data': [
     'views/product_view.xml',
 ],
 'demo': [
     'demo/backend_demo.xml',
     'demo/ir.exports.line.csv',
 ],
 'installable': True,
 'application': False,
 }
