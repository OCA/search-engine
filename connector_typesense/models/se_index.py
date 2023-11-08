# Copyright 2024 Derico
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..tools.serializer import TSJsonifySerializer


class SeIndex(models.Model):

    _inherit = "se.index"

    serializer_type = fields.Selection(selection_add=[("typesense", "Typesense")])

    def _get_serializer(self):
        if self.serializer_type == "typesense":
            return TSJsonifySerializer()
        else:
            return super()._get_serializer()
