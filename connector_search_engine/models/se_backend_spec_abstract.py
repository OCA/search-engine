# -*- coding: utf-8 -*-
# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SeBackendSpecAbstract(models.AbstractModel):
    _name = 'se.backend.spec.abstract'
    _description = 'Se Specialized Backend'
    _inherit = 'connector.backend'

    # This field may be removed in next  version, check comment in se.backend
    # file
    name = fields.Char(
        related='se_backend_id.name',
        store=True,
        required=False
    )
    # Delegation inheritance
    se_backend_id = fields.Many2one(
        comodel_name='se.backend',
        ondelete="cascade",
        index=True,
        auto_join=True,
        delegate=True,
        required=True,
    )

    @api.model
    def create(self, vals):
        vals['specific_model'] = self._name
        return super(SeBackendSpecAbstract, self).create(vals)

    @api.multi
    def unlink(self):
        se_backend = self.mapped('se_backend_id')
        res = super(SeBackendSpecAbstract, self).unlink()
        se_backend.unlink()
        return res

    @api.multi
    def _get_existing_keychain(self):
        return self.se_backend_id._get_existing_keychain()

    @api.onchange('name')
    def onchange_backend_name(self):
        if self.index_ids:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Changing this name will change the name of '
                                 'the indexes. If you proceed, you have to '
                                 'take care of the configuration in your '
                                 'website. Cancel the modification if you are'
                                 ' not comfortable with this configuration.')
                }
            }
