# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeIndexableRecord(models.AbstractModel):
    _name = "se.indexable.record"
    _description = "Mixin that make record indexable in a search engine"
    _se_indexable = True

    index_bind_ids = fields.One2many(
        "se.binding",
        "res_id",
        "Index Binding",
    )

    def _add_to_index(self, index):
        bindings = self.env["se.binding"]
        for record in self:
            binding = record.index_bind_ids.filtered(lambda s: s.index_id == index)
            if binding and binding.state == "to_delete":
                binding.state = "to_recompute"
            else:
                binding = self.env["se.binding"].create(
                    {
                        "index_id": index.id,
                        "res_id": record.id,
                        "res_model": self._name,
                    }
                )
        bindings += binding
        return bindings

    def _remove_from_index(self, index):
        binding = self.index_bind_ids.filtered(lambda s: s.index_id == index)
        binding.write({"state": "to_delete"})

    def unlink(self):
        self.index_bind_ids.write(
            {
                "state": "to_delete",
                "res_id": False,
            }
        )
        return super().unlink()
