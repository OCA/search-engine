# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class NosqlProductTemplate(models.Model):
    _inherit = 'nosql.binding'
    _name = 'nosql.product.template'
    _description = 'Nosql Product Template Binding'

    record_id = fields.Many2one('product.template')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    nosql_bind_ids = fields.One2many(
        'nosql.product.template',
        'record_id',
        string='Nosql Binding')
