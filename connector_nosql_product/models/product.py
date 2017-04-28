# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class NosqlProductProduct(models.Model):
    _inherit = 'nosql.binding'
    _name = 'nosql.product.product'
    _description = 'Nosql Product Product Binding'
    _inherits = {'product.product': 'record_id'}

    record_id = fields.Many2one(
        'product.product',
        required=True,
        ondelete='cascade')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    nosql_bind_ids = fields.One2many(
        'nosql.product.product',
        'record_id',
        string='Nosql Binding')
