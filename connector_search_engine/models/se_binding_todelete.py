# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBindingToDelete(models.Model):
    """Search Engine Binding To Delete

    When bound records are deleted, their IDs are temporarily stored here
    until the next synchronization.
    """

    _name = "se.binding.todelete"
    _description = "Search Engine Binding To Delete"

    index_id = fields.Many2one(
        "se.index",
        string="Index",
        ondelete="cascade",
        required=True,
    )
    binding_id = fields.Integer(
        string="Binding ID",
        required=True,
    )

    def synchronize(self):
        delete_ids = []
        for index in self.index_id:
            todelete = self.filtered(lambda rec: rec.index_id == index)
            binding_ids = todelete.mapped("binding_id")
            adapter = index._get_backend_adapter()
            adapter.delete(binding_ids)
            delete_ids += binding_ids
        self.unlink()
        return f"Deleted ids : {delete_ids}"
