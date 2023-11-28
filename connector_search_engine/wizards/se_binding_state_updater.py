# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBindingStateUpdater(models.TransientModel):

    _name = "se.binding.state.updater"
    _description = "Update state of SE bindings"

    state = fields.Selection(
        string="New state",
        selection=lambda self: self.env["se.binding"]._fields["state"].selection,
        required=True,
    )

    def doit(self):
        res_ids = self.env.context.get("active_ids")
        self.env["se.binding"].browse(res_ids).write({"state": self.state})
