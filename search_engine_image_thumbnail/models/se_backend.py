# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBackend(models.Model):

    _inherit = "se.backend"

    image_field_thumbnail_size_ids = fields.One2many(
        string="Thumbnail Sizes",
        comodel_name="se.image.field.thumbnail.size",
        inverse_name="backend_id",
    )
