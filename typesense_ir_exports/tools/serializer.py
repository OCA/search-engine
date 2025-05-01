# Copyright 2023 Kencove (https://kencove.com).
# @author Mohamed Alkobrosli <malkobrosly@kencove.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.addons.connector_search_engine.tools.serializer import ModelSerializer


class JsonifySerializer(ModelSerializer):
    def __init__(self, parser, index):
        super().__init__()
        self.parser = parser
        self.index = index

    # typesense search engine requires id to be string
    def stringify_id(self, obj):
        if obj.get("id"):
            obj["id"] = f"{obj['id']}"
        return obj

    def serialize(self, record):
        ################################
        # Validating populated json data
        ################################
        data = record.jsonify(self.parser, one=True)
        # Should convert binary data to string as data field is of type json
        for key, value in data.items():
            if isinstance(value, bytes):
                data[key] = base64.b64encode(value).decode("utf-8")
            if isinstance(value, dict):
                data[key] = self.stringify_id(value)
            if isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], dict):
                        value[i] = self.stringify_id(value[i])
                data[key] = value
        data = self.stringify_id(data)
        return data
