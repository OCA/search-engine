# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SeThumbnail(models.Model):

    _name = "se.thumbnail"
    _inherit = "fs.image.thumbnail.mixin"
    _description = "Indexed Image Thumbnail"
