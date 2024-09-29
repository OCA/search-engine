# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from odoo import api, fields, models, tools
from odoo.osv.expression import FALSE_DOMAIN


class SeImageFieldThumbnailSize(models.Model):

    _name = "se.image.field.thumbnail.size"
    _description = "Index Thumbnail Size"

    display_name = fields.Char(
        compute="_compute_display_name",
        store=True,
    )
    size_ids = fields.Many2many(
        "se.thumbnail.size",
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        domain=lambda self: self._model_id_domain(),
        ondelete="cascade",
    )
    model = fields.Char(
        related="model_id.model",
        string="Model name",
        readonly=True,
        store=True,
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Images field",
        required=True,
        ondelete="cascade",
    )
    field_name = fields.Char(
        related="field_id.name",
        string="Images field name",
        readonly=True,
        store=True,
    )
    allowed_field_ids = fields.Many2many(
        "ir.model.fields",
        string="Images fields",
        compute="_compute_allowed_field_ids"
    )
    backend_id = fields.Many2one(
        "se.backend",
        string="Search Engine Backend",
        required=True,
        ondelete="cascade",
    )

    _sql_constraints = [
        (
            "model_field_unique",
            "unique(model_id, field_id, backend_id)",
            "A thumbnail size already exists for this backend, model and field",
        )
    ]

    @api.depends("model", "field_name")
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.model}.{record.field_name}"

    @tools.ormcache()
    @api.model
    def _model_id_domain(self):
        models = [
            model for model in self.env if self._is_model_valid_for_thumbnail(model)
        ]
        models.sort()
        return [("model", "in", models)]

    @api.model
    def _is_model_valid_for_thumbnail(self, model_name):
        model = self.env[model_name]
        is_indexable = (
            hasattr(self.env[model_name], "_se_indexable")
            and not self.env[model_name]._abstract
            and not self.env[model_name]._transient
        )
        if is_indexable:
            for field in model._fields.values():
                if self._is_field_valid_for_thumbnail(field):
                    return True
        return False

    @api.depends("model_id")
    def _compute_allowed_field_ids(self):
        for record in self:
            domain_fields = []
            if record.model_id:
                model = self.env[record.model_id.model]
                domain_fields = model._fields.values()
            
            names = []
            for field in domain_fields:
                if self._is_field_valid_for_thumbnail(field):
                    names.append(field.name)
            
            domain = [('name', 'in', names)]
            records = self.env['ir.model.fields'].search(domain)
            record.allowed_field_ids = records
    
    @api.model
    def _is_field_valid_for_thumbnail(self, field: fields.Field):
        if isinstance(field, fields.Image) or field.type == "fs_image":
            return True
        if not field.comodel_name:
            return False
        if field.comodel_name not in self.env:
            return False
        abstract = self.env["fs.image.relation.mixin"]
        model = self.env[field.comodel_name]
        return isinstance(model, abstract.__class__)
