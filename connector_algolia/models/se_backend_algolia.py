# © 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class SeBackendAlgolia(models.Model):
    _name = 'se.backend.algolia'
    _inherit = 'se.backend.spec.abstract'
    _description = 'Algolia Backend'

    # TODO: load values from server env
    algolia_app_id = fields.Char(string="APP ID")
    # v12: we removed keychain inheritance
    # which was providing the field `password`.
    # This field was related to it, this is why `oldname` is here.
    algolia_api_key = fields.Char(string="API KEY", oldname='password')
