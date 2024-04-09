# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeIndex(models.Model):

    _inherit = "se.index"

    image_field_thumbnail_size_ids = fields.One2many(
        string="Thumbnail Sizes",
        comodel_name="se.image.field.thumbnail.size",
        related="backend_id.image_field_thumbnail_size_ids",
    )

    def _get_thumbnail_sizes(self, record, field_name):
        """Return a list of thumbnail sizes for the given field_name"""
        self.ensure_one()
        return self.image_field_thumbnail_size_ids.filtered(
            lambda r: r.field_name == field_name and r.model == record._name
        ).mapped("size_ids")
