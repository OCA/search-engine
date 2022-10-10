# Copyright 2013 Akretion (http://www.akretion.com)
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
import math
import sys

from odoo import _, api, fields, models

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
    model_id = fields.Many2one(compute="_compute_model_id")

    def _compute_model_id(self):
        # TODO
        pass

    def _compute_state(self):
        # TODO add the logic for invalidating the state
        # automatically based on the exporter
        pass

    @property
    def record_id(self):
        return None

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

    def _convert_to_json(self):
        if self.index_id.lang_id:
            self = self.with_context(lang=self.index_id.lang_id.code)
        # TODO check if we have cache on get_json_parser
        return self.record_id.jsonify(self.index_id.exporter_id.get_json_parser())[0]

    def _validate_data(self):
        return self.backend_id._validate_data(self.data)

    def _recompute_json(self, force_export=False):
        """Compute index record data as JSON."""
        # `sudo` because the recomputation can be triggered from everywhere
        # (eg: an update of a product in the stock) and is not granted
        # that the user triggering it has access to all required records
        # (eg: se.backend or related records needed to compute index values).
        # All in all, this is safe because the index data should always
        # be the same no matter the access rights of the user triggering this.
        for record in self.sudo():
            record.data = record._convert_to_json()
            record.date_recomputed = fields.Datetime.now()
            error = record._validate_data()
            if error:
                record.state = "invalid_data"
                record.validation_error = error
            else:
                record.state = "to_export"
                record.validation_error = ""

    def export_record(self):
        export_ids = []
        for work in self.sudo()._work_by_index():
            exporter = work.component(usage="se.binding.exporter")
            exporter.run()
            export_ids += work.records.ids
            work.records.state = "done"
        return "Exported ids : {}".format(export_ids)

    def delete_record(self):
        delete_ids = []
        for work in self.sudo()._work_by_index():
            deleter = work.component(usage="record.exporter.deleter")
            deleter.run()
            delete_ids += work.records.ids
            work.records.unlink()
        return "Deleted ids : {}".format(delete_ids)
