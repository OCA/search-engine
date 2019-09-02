# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeIndex(models.Model):

    _inherit = "se.index"

    config_id = fields.Many2one(
        comodel_name="se.index.config", string="Config", help="Algolia index settings"
    )

    def _get_settings(self):
        settings = super()._get_settings()
        if self.config_id:
            settings.update(self.config_id.body)
        return settings
