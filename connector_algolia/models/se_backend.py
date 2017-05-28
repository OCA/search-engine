# -*- coding: utf-8 -*-
# © 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class SeBackend(models.Model):
    _inherit = 'se.backend'

    version = fields.Selection(selection_add=[('algolia_v1', 'Algolia V1')])


class SeIndex(models.Model):
    _inherit = 'se.index'

    id_key = fields.Char(
        'Identifier key',
        help="This field will be used as ObjectID for algolia")
