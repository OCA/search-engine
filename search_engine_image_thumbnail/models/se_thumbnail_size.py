# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SeThumbnailSize(models.Model):

    _name = "se.thumbnail.size"
    _description = "Thumbnail Size"

    name = fields.Char(required=True)
    key = fields.Char(required=True)
    size_x = fields.Integer(required=True)
    size_y = fields.Integer(required=True)

    @api.depends("size_x", "size_y")
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{} ({}x{})".format(
                record.name, record.size_x, record.size_y
            )
