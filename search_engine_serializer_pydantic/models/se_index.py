# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from typing import Type

from pydantic import BaseModel

from odoo import api, fields, models

from ..tools.serializer import PydanticModelSerializer


class SeIndex(models.Model):

    _inherit = "se.index"

    is_pydantic_serializer = fields.Boolean(
        string="Is a Serializer based on Pydantic Model?",
        compute="_compute_is_pydantic_serializer",
        store=False,
    )

    record_json_schema = fields.Serialized(
        string="JSON Schema of a record stored in this index (as dict)",
        compute="_compute_record_json_schema",
        store=False,
    )

    record_json_schema_str = fields.Char(
        string="JSON Schema of a record stored in this index",
        compute="_compute_record_json_schema",
        store=False,
    )

    @api.depends("serializer_type")
    def _compute_is_pydantic_serializer(self):
        for rec in self:
            rec.is_pydantic_serializer = isinstance(
                rec.model_serializer, PydanticModelSerializer
            )

    @api.depends("serializer_type")
    def _compute_record_json_schema(self):
        for rec in self:
            if not rec.is_pydantic_serializer:
                rec.record_json_schema = None
                rec.record_json_schema_str = ""
            else:
                model: Type[BaseModel] = rec.model_serializer.get_model_class()
                rec.record_json_schema = model.model_json_schema()
                rec.record_json_schema_str = json.dumps(
                    rec.record_json_schema, indent=2
                )
