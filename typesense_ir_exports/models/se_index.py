# Copyright 2023 Kencove (https://kencove.com).
# @author Mohamed Alkobrosli <malkobrosly@kencove.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from ..tools.serializer import JsonifySerializer


class SeIndex(models.Model):
    _inherit = "se.index"

    def _get_serializer(self):
        if (
            self.serializer_type == "ir_exports"
            and self.backend_id.backend_type == "typesense"
        ):
            parser = self.exporter_id.get_json_parser()
            return JsonifySerializer(parser=parser, index=self)
        else:
            return super()._get_serializer()
