# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models

from odoo.addons.fs_image.fields import FSImage


class TestImageRelation(models.Model):

    _name = "test.image.relation"
    _inherit = "fs.image.relation.mixin"
    _description = "Test Multi Image Thumbnail Image"

    test_id = fields.Many2one(
        "test.multi.image",
        required=True,
        ondelete="cascade",
    )


class TestMultiImage(models.Model):

    _name = "test.multi.image"
    _inherit = ["se.indexable.record"]
    _description = "Test Image Thumbnail"

    name = fields.Char(required=True)
    image_ids = fields.One2many(
        string="Images",
        comodel_name="test.image.relation",
        inverse_name="test_id",
    )


class TestImage(models.Model):

    _name = "test.image"
    _inherit = ["se.indexable.record"]
    _description = "Test Image"

    name = fields.Char(required=True)
    image = fields.Image(required=True)


class TestFSImage(models.Model):

    _name = "test.fsimage"
    _inherit = ["se.indexable.record"]
    _description = "Test FSImage"

    name = fields.Char(required=True)
    image = FSImage(required=True)
