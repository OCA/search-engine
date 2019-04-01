# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeIndex(models.Model):

    _inherit = "se.index"

    config_id = fields.Many2one(
        comodel_name="se.index.config",
        string="Config",
        help="Elasticseacrh index definition (see https://www.elastic.co/"
        "guide/en/elasticsearch/reference/current/"
        "indices-create-index.html)",
        required=True,
    )
