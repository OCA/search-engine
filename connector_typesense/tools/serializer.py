# Copyright 2023 Kencove (https://kencove.com).
# @author Mohamed Alkobrosli <malkobrosly@kencove.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.tools.serializer import ModelSerializer


class TSJsonifySerializer(ModelSerializer):
    def serialize(self, record):
        # Typesense SE requires id field to be string
        # It also requires other intger field types to be searchable
        data = {}
        if record.id:
            data["id"] = str(record.id)
        if record.name:
            data["name"] = record.name
        return data
