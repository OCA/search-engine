# Copyright 2013 Akretion (http://www.akretion.com)
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import logging
import traceback
from collections import defaultdict
from typing import Any, Dict, Iterator

from psycopg2.errors import Error
from typing_extensions import Self

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.job import identity_exact

from ..tools.json_comparer import compare_json

_logger = logging.getLogger(__name__)


class SeBinding(models.Model):
    _name = "se.binding"
    _description = "Search Engine Record"

    # when we recompute several binding we order by res_model, res_id so for a
    # record indexed in several index all the binding will be recomputed
    # in the same job as index have a lot of common data most of the field will
    # be in cache after computing the first binding
    _order = "res_model, res_id desc"

    backend_id = fields.Many2one(
        "se.backend",
        related="index_id.backend_id",
        string="Search Engine Backend",
        store=True,
        readonly=True,
    )
    index_id = fields.Many2one(
        "se.index",
        string="Index",
        required=True,
        # TODO: shall we use 'restrict' here to preserve existing data?
        ondelete="cascade",
        readonly=True,
    )
    state = fields.Selection(
        [
            ("to_recompute", "To recompute"),
            ("recomputing", "Recomputing"),
            ("to_export", "To export"),
            ("exporting", "Exporting"),
            ("done", "Done"),
            ("invalid_data", "Invalid Data"),
            ("recompute_error", "Fail to Recompute"),
            ("to_delete", "To Delete"),
            ("deleting", "Deleting"),
        ],
        default="to_recompute",
        readonly=True,
    )
    date_recomputed = fields.Datetime(readonly=True)
    date_synchronized = fields.Datetime(readonly=True)
    data = fields.Json(readonly=True, prefetch=False)
    data_display = fields.Text(
        compute="_compute_data_display",
        help="Include this in debug mode to be able to inspect index data.",
    )
    error = fields.Text()
    res_id = fields.Integer(
        string="Record ID",
        help="ID of the target record in the database",
        readonly=True,
    )
    res_model = fields.Selection(
        selection=lambda s: s._get_indexable_model_selection(), readonly=True
    )
    record_id = fields.Reference(
        selection=lambda s: s._get_indexable_model_selection(),
        compute="_compute_record_id",
        readonly=True,
    )

    _sql_constraints = [
        (
            "item_uniq_per_index",
            "unique(res_id, res_model, index_id)",
            _("A record can only be bind one time per index !"),
        ),
    ]

    @api.constrains("res_model", "index_id")
    def _check_model(self):
        for binding in self:
            if (
                binding.res_model
                and binding.res_model != binding.index_id.model_id.model
            ):
                raise ValidationError(
                    _("Binding model must be equal to the index model")
                )

    @tools.ormcache()
    @api.model
    def _get_indexable_model_selection(self):
        return [
            (model, self.env[model]._description)
            for model in self.env
            if (
                hasattr(self.env[model], "_se_indexable")
                and not self.env[model]._abstract
                and not self.env[model]._transient
            )
        ]

    @property
    def record(self) -> models.Model:
        if len(set(self.mapped("res_model"))) > 1:
            raise ValueError("All record must have the same model")
        return self.env[self[0].res_model].browse(self.mapped("res_id")).exists()

    @api.depends("res_model", "res_id")
    def _compute_record_id(self):
        """Compute the record field."""
        for binding in self:
            if binding.res_model and binding.res_id:
                binding.record_id = (
                    self.env[binding.res_model].browse(binding.res_id).exists()
                )
            else:
                binding.record_id = False

    @api.depends("data")
    def _compute_data_display(self):
        for rec in self:
            rec.data_display = json.dumps(rec.data, sort_keys=True, indent=4)

    def get_export_data(self) -> Dict[str, Any]:
        """Public method to retrieve export data."""
        return self.data

    def _batch(self, size: int) -> Iterator["SeBinding"]:
        """Return an iterator on the records in batch of size."""
        for i in range(0, len(self), size):
            yield self[i : i + size]

    def jobify_recompute_json(self, force_export: bool = False):
        """Create batch job for records to recompute the json."""
        # The job creation with tracking is very costly. So disable it.
        if not self:
            # Nothing to do
            return
        size = min(self.index_id.mapped("batch_exporting_size"))
        for binding in self.with_context(tracking_disable=True)._batch(size):
            description = _(
                "Recompute %(name)s json and check if need update", name=self._name
            )
            binding.with_delay(
                description=description, identity_key=identity_exact
            ).recompute_json(force_export=force_export)

    def _contextualize(self, record):
        ctx = {"index_id": record.index_id.id}
        # force the lang if needed
        if record.index_id.lang_id:
            ctx["lang"] = record.index_id.lang_id.code
        return record.with_context(**ctx)

    def recompute_json(self, force_export: bool = False):
        """ "Compute index record data as JSON."""
        # `sudo` because the recomputation can be triggered from everywhere
        # (eg: an update of a product in the stock) and is not granted
        # that the user triggering it has access to all required records
        # (eg: se.backend or related records needed to compute index values).
        # All in all, this is safe because the index data should always
        # be the same no matter the access rights of the user triggering this.

        for record in self.sudo():
            if not record.record:
                record.state = "to_delete"
                _logger.error(
                    "There is something wrong, the record do not exists "
                    "flag the binding to be deleted"
                )
                continue

            record = self._contextualize(record)
            index = record.index_id

            old_data = record.data
            try:
                with self.env.cr.savepoint():
                    record.data = index.model_serializer.serialize(record.record)
                    record.date_recomputed = fields.Datetime.now()
            except Error as pg_error:
                # PG error could make the cursor unusable
                raise pg_error
            except Exception as e:
                record.state = "recompute_error"
                stack = traceback.format_exc()
                error = f"{e} \n\n {stack}"
                record.error = error
                _logger.exception(
                    "Error while recomputing the json for %s %s: %s",
                    record.res_model,
                    record.res_id,
                    record.record_id.display_name,
                )
                continue
            try:
                index.json_validator.validate(record.data or {})
            except ValidationError as e:
                record.state = "invalid_data"
                record.error = str(e)
            else:
                if force_export or not compare_json(old_data or {}, record.data or {}):
                    record.state = "to_export"
                else:
                    record.state = "done"
                record.error = ""

    def export_record(self) -> str:
        for _backend, bindings in self.partition("backend_id").items():
            adapter = bindings[0].index_id.se_adapter
            adapter.index([record.get_export_data() for record in bindings])
        self.state = "done"
        return "Exported ids : {}".format(self.ids)

    def delete_record(self) -> str:
        record_ids = self.mapped("res_id")
        for _backend, bindings in self.partition("backend_id").items():
            adapter = bindings[0].index_id.se_adapter
            adapter.delete(bindings.mapped("res_id"))
        self.unlink()
        return "Deleted ids : {}".format(record_ids)

    def recompute_from_owner(self):
        bindings = self.search(
            [
                ("res_model", "=", self._context["active_model"]),
                ("res_id", "in", self._context["active_ids"]),
            ]
        )
        bindings.write({"state": "recomputing"})
        bindings.jobify_recompute_json()

    @api.model_create_multi
    def create(self, vals_list) -> Self:
        """Create a binding and compute its JSON."""
        records = super().create(vals_list)
        records._invalidate_bindings_in_references()
        return records

    def write(self, vals) -> bool:
        """Write a binding and compute its JSON."""
        if "res_model" in vals or "res_id" in vals:
            # invalidate bindings in current references
            self._invalidate_bindings_in_references()
        res = super().write(vals)
        if "res_model" in vals or "res_id" in vals:
            # invalidate bindings in new references
            self._invalidate_bindings_in_references()
        return res

    def unlink(self):
        self._invalidate_bindings_in_references()
        return super().unlink()

    def _invalidate_bindings_in_references(self):
        """Invalidate the binding_ids field on the records referenced by the
        bindings.
        """
        ids_by_model = defaultdict(list)
        for binding in self:
            ids_by_model[binding.res_model].append(binding.res_id)
        for model, ids in ids_by_model.items():
            self.env[model].browse(ids).invalidate_recordset(["se_binding_ids"])
