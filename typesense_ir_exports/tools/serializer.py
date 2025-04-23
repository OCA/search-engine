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

    def serialize(self, record):
        ################################
        # Validating populated json data
        ################################
        data = record.jsonify(self.parser, one=True)
        # Should convert binary data to string as data field is of type json
        for key, value in data.items():
            if isinstance(value, bytes):
                data[key] = base64.b64encode(value).decode("utf-8")
        # typesense search engine requires id to be string
        if data.get("id"):
            data["id"] = f"{data['id']}"
        return data
