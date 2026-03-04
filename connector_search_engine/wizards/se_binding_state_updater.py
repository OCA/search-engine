# Copyright 2023 ACSONE SA/NV
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import groupby


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
        selected_bindings = self.env["se.binding"].browse(res_ids)
        selected_bindings.write({"state": self.state})
        if self.do_it_now and self.state == "to_recompute":
            for index, bindings in groupby(selected_bindings, key=lambda x: x.index_id):
                index._jobify_batch_recompute(binding_ids=[x.id for x in bindings])
