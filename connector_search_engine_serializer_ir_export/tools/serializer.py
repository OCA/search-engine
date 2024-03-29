# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.tools.serializer import ModelSerializer


class JsonifySerializer(ModelSerializer):
    def __init__(self, parser):
        super().__init__()
        self.parser = parser

    def serialize(self, record):
        return record.jsonify(self.parser, one=True)
