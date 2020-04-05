# -*- coding: utf-8 -*-
# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SeBackendFake(models.Model):

    _name = "se.backend.fake"
    _inherit = "se.backend.spec.abstract"
    _description = "Unit Test SE Backend"


# Fake partner binding


class BindingResPartnerFake(models.Model):
    _name = "res.partner.binding.fake"
    _inherit = ["se.binding"]
    _inherits = {"res.partner": "record_id"}

    record_id = fields.Many2one(
        comodel_name="res.partner",
        string="Odoo record",
        required=True,
        ondelete="cascade",
    )


class ResPartnerFake(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    binding_ids = fields.One2many(
        comodel_name=BindingResPartnerFake._name,
        inverse_name="record_id",
        copy=False,
        string="Bindings",
        context={"active_test": False},
    )
