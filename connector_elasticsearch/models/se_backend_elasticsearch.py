# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBackendElasticsearch(models.Model):

    _name = "se.backend.elasticsearch"
    _inherit = "se.backend.spec.abstract"
    _description = "Elasticsearch Backend"

    es_server_host = fields.Char(string="ElasticSearch host")
