# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SeIndexableRecord(models.AbstractModel):
    _name = "se.indexable.record"
    _description = "Mixin that make record indexable in a search engine"
    _se_indexable = True

    def _get_bindings(self, index=None):
        domain = [
            ("res_model", "=", self._name),
            ("res_id", "in", self.ids),
        ]
        if index:
            domain.append(("index_id", "=", index.id))
        return self.env["se.binding"].search(domain)

    def _add_to_index(self, index):
        bindings = self._get_bindings(index)
        bindings.filtered(lambda s: s.state == "to_delete").write(
            {"state": "to_recompute"}
        )
        if bindings:
            todo = self - bindings.record_id
        else:
            todo = self
        vals_list = [
            {
                "index_id": index.id,
                "res_id": record.id,
                "res_model": self._name,
            }
            for record in todo
        ]
        return bindings | self.env["se.binding"].create(vals_list)

    def _remove_from_index(self, index):
        bindings = self._get_bindings(index)
        bindings.write({"state": "to_delete"})

    def unlink(self):
        bindings = self._get_bindings()
        bindings.write(
            {
                "state": "to_delete",
                "res_id": False,
            }
        )
        return super().unlink()
