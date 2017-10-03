# -*- coding: utf-8 -*-
# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class KeychainAccount(models.Model):

    _inherit = 'keychain.account'

    namespace = fields.Selection(
        selection_add=[('search_engine_backend', 'Search Engine Backend')])

    @api.multi
    def _search_engine_backend_validate_data(self, data):
        return True

    @api.multi
    def _search_engine_backend_init_data(self):
        return {}
