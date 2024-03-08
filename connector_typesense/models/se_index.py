# Copyright 2024 Derico
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SeIndex(models.Model):

    _inherit = "se.index"
