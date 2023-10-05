# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SeIndex(models.Model):

    _inherit = "se.index"

    image_field_thumbnail_size_ids = fields.One2many(
        string="Thumbnail Sizes",
        comodel_name="se.image.field.thumbnail.size",
        compute="_compute_image_field_thumbnail_size_ids",
    )

    @api.depends("backend_id.image_field_thumbnail_size_ids", "model_id")
    def _compute_image_field_thumbnail_size_ids(self):
        for record in self:
            record.image_field_thumbnail_size_ids = (
                record.backend_id.image_field_thumbnail_size_ids.filtered(
                    lambda r: r.model_id == record.model_id
                )
            )

    def _get_thumbnail_sizes(self, field_name):
        """Return a list of thumbnail sizes for the given field_name"""
        self.ensure_one()
        return self.image_field_thumbnail_size_ids.filtered(
            lambda r: r.field_name == field_name
        ).mapped("size_ids")
