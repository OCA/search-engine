# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# DON'T IMPORT THIS MODULE IN INIT TO AVOID THE CREATION OF THE MODELS
# DEFINED FOR TESTS INTO YOUR ODOO INSTANCE

from odoo import api, fields, models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'se.binding']

    @api.model
    def _get_default_index_id(self):
        return self.env['se.index'].search(
            [('model_id.model', '=', 'res.partner')])

    index_id = fields.Many2one(
        'se.index',
        default=_get_default_index_id)
