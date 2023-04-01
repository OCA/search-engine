# Copyright 2013 Akretion (http://www.akretion.com)
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
import math
import sys

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SeBinding(models.Model):
    _name = "se.binding"
    _description = "Search Engine Record"

    backend_id = fields.Many2one(
        "se.backend", related="index_id.backend_id", string="Search Engine Backend"
    )
    index_id = fields.Many2one(
        "se.index",
        string="Index",
        required=True,
        # TODO: shall we use 'restrict' here to preserve existing data?
        ondelete="cascade",
    )
    state = fields.Selection(
        [
            ("to_recompute", "To recompute"),
            ("recomputing", "Recomputing"),
            ("to_export", "To export"),
            ("exporting", "Exporting"),
            ("done", "Done"),
            ("invalid_data", "Invalid Data"),
            ("to_delete", "To Delete"),
            ("deleting", "Deleting"),
        ],
        default="to_recompute",
        compute="_compute_state",
        store=True,
        readonly=False,
    )
    date_recomputed = fields.Datetime(readonly=True)
    date_syncronized = fields.Datetime(readonly=True)
    data = fields.Serialized()
    data_display = fields.Text(
        compute="_compute_data_display",
        help="Include this in debug mode to be able to inspect index data.",
    )
    validation_error = fields.Text()
    res_id = fields.Integer()
    res_model = fields.Selection(selection=lambda s: s._get_indexable_model_selection())

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

    def _compute_state(self):
        # TODO add the logic for invalidating the state
        # automatically based on the exporter
        pass

    @property
    def record_id(self):
        return self.env[self.res_model].browse(self.res_id).exists()

    @api.depends("data")
    def _compute_data_display(self):
        for rec in self:
            rec.data_display = json.dumps(rec.data, sort_keys=True, indent=4)

    def get_export_data(self):
        """Public method to retrieve export data."""
        return self.data

    def _get_binding_to_process(self, bindings, batch_size):
        return bindings[0:batch_size], bindings[batch_size:]  # noqa: E203

    def _jobify_get_job_description(self, processing_count):
        # We check if we are currently handling an exception in order
        # to change the job description.
        (current_exception, current_exception_value, __) = sys.exc_info()
        if current_exception:
            return _(
                "Batch of %(processing_count)s items for %(model_name)s. "
                "Previous batch raised %(exception_name)s: %(exception_value)s."
            ) % dict(
                processing_count=processing_count,
                model_name=self._name,
                exception_name=current_exception.__name__,
                exception_value=current_exception_value,
            )
        else:
            return _(
                "Batch task of %(processing_count)s for "
                "recomputing %(model_name)s json"
            ) % dict(
                processing_count=processing_count,
                model_name=self._name,
            )

    def jobify_recompute_json(self, force_export=False, batch_size=500):
        # The job creation with tracking is very costly. So disable it.
        bindings = self.with_context(tracking_disable=True)
        while bindings:
            processing, bindings = self._get_binding_to_process(bindings, batch_size)
            description = self._jobify_get_job_description(len(processing))
            processing.with_delay(description=description).recompute_json(
                force_export=force_export
            )

    def recompute_json(self, force_export=False):
        try:
            with self.env.cr.savepoint():
                return self._recompute_json(force_export=force_export)
        except Exception as e:
            # If the batch fails, retry with a half len batch:
            if len(self) > 1:
                self.jobify_recompute_json(
                    force_export=force_export,
                    batch_size=math.ceil(len(self) / 2),
                )
                return _(
                    "Job have been splited due to failling element.\nError: {}"
                ) % str(e)
            # We can't systematically reraise here, if we do the new jobs
            # will be discarded.
            raise

    def _work_by_index(self, active=True):
        self = self.exists()
        for backend in self.mapped("backend_id"):
            for index in self.mapped("index_id"):
                bindings = self.filtered(
                    lambda b, backend=backend, index=index: b.backend_id == backend
                    and b.index_id == index
                )
                with backend.work_on(self._name, records=bindings, index=index) as work:
                    yield work

    def _recompute_json(self, force_export=False):
        """Compute index record data as JSON."""
        # `sudo` because the recomputation can be triggered from everywhere
        # (eg: an update of a product in the stock) and is not granted
        # that the user triggering it has access to all required records
        # (eg: se.backend or related records needed to compute index values).
        # All in all, this is safe because the index data should always
        # be the same no matter the access rights of the user triggering this.

        index2serializer = {}
        index2validator = {}
        for index in self.index_id:
            index2serializer[index] = index.get_serializer()
            index2validator[index] = index.get_validator()

        for record in self.sudo():
            if not record.record_id.exists():
                record.state = "to_delete"
                _logger.error(
                    "There is something wrong, the record do not exists "
                    "flag the binding to be deleted"
                )
                continue

            # force the lang if needed
            if record.index_id.lang_id:
                record = record.with_context(lang=self.index_id.lang_id.code)

            record.data = index2serializer[index].serialize(record.record_id)
            record.date_recomputed = fields.Datetime.now()
            try:
                index2validator[index].validate(record.data)
            except ValidationError as e:
                record.state = "invalid_data"
                record.validation_error = str(e)
            else:
                record.state = "to_export"
                record.validation_error = ""

    def export_record(self):
        adapter = self.index_id._get_adapter()
        adapter.index([record.get_export_data() for record in self])
        self.state = "done"
        return "Exported ids : {}".format(self.ids)

    def delete_record(self):
        adapter = self.index_id._get_adapter()
        record_ids = self.mapped("res_id")
        adapter.delete(record_ids)
        self.unlink()
        return "Deleted ids : {}".format(record_ids)
