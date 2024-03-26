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
    do_it_now = fields.Boolean(help="Don't wait for the cron to process these records")

    def doit(self):
        res_ids = self.env.context.get("active_ids")
        bindings = self.env["se.binding"].browse(res_ids)
        bindings.write({"state": self.state})
        if self.do_it_now and self.state == "to_recompute":
            bindings.index_id._jobify_batch_recompute(binding_ids=bindings.ids)
