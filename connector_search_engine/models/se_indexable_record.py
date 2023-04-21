# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from __future__ import annotations

from typing import TYPE_CHECKING

from odoo import fields, models

if TYPE_CHECKING:
    from .se_binding import SeBinding
    from .se_index import SeIndex


class SeIndexableRecord(models.AbstractModel):
    _name = "se.indexable.record"
    _description = "Mixin that make record indexable in a search engine"
    _se_indexable = True

    binding_ids = fields.One2many(
        string="Seacrh Engine Bindings",
        comodel_name="se.binding",
        compute="_compute_binding_ids",
    )

    def _compute_binding_ids(self) -> None:
        binding_model = self.env["se.binding"]
        values = {
            read["res_id"][0]: read["ids"]
            for read in binding_model.read_group(
                domain=[
                    ("res_model", "=", self._name),
                    ("res_id", "in", self.ids),
                ],
                fields=["ids:array_agg(id)"],
                groupby=["res_id"],
            )
        }
        for record in self:
            record.binding_ids = binding_model.browse(values.get(record.id, []))

    def _get_bindings(self, index: SeIndex = None) -> SeBinding:
        domain = [
            ("res_model", "=", self._name),
            ("res_id", "in", self.ids),
        ]
        if index:
            domain.append(("index_id", "=", index.id))
        return self.env["se.binding"].search(domain)

    def _add_to_index(self, index: SeIndex) -> SeBinding:
        """Add the record to the index.

        It will create a binding for each record that is not already
        binded to the index and mark the others to be updated.

        :param index: The index where the record should be added
        :return: The binding recordset
        """
        bindings = self._get_bindings(index)
        bindings.filtered(lambda s: s.state == "to_delete").write(
            {"state": "to_recompute"}
        )
        if bindings:
            todo = self - bindings.record
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

    def _remove_from_index(self, index: SeIndex) -> None:
        """Remove the record from the index.

        It will mark the binding to be deleted.
        Once the data will be removed from the index, the binding will be
        deleted.
        """
        bindings = self._get_bindings(index)
        bindings.write({"state": "to_delete"})

    def _se_mark_to_update(self, index: SeIndex | None = None) -> None:
        """Mark the record to be updated in the index."""
        bindings = self._get_bindings(index)
        bindings.write({"state": "to_recompute"})

    def unlink(self):
        bindings = self._get_bindings()
        bindings.write(
            {
                "state": "to_delete",
                "res_id": False,
            }
        )
        return super().unlink()
