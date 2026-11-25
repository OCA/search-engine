# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SeIndex(models.Model):

    _inherit = "se.index"

    @api.constrains("config_id", "backend_id")
    def _check_os_config_id_required(self):
        for rec in self:
            if rec.backend_id.backend_type == "opensearch" and not rec.config_id:
                raise ValidationError(
                    _("An index definition is required for OpenSearch")
                )
