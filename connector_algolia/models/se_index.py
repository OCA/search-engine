# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SeIndex(models.Model):

    _inherit = "se.index"

    def _get_settings(self):
        settings = super()._get_settings()
        if self.config_id and self.config_id.body:
            settings.update(self.config_id.body)
        return settings
