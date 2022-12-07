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


class SeBinding(models.AbstractModel):
    _name = "se.binding"
    _description = "Search Engine Binding"

    # Tech flag to identify model for SE bindings
    _se_model = True
    # Tech flag to identify model for SE bindings
    # that do not require lang specific indexes.
    # This flag does not trigger any automatic machinery.
    # It provides a common key to provide implementers a unified way
    # to check whether their specific binding models need or not lang spec index.
    _se_index_lang_agnostic = False

    se_backend_id = fields.Many2one(
        "se.backend", related="index_id.backend_id", string="Search Engine Backend"
    )
    index_id = fields.Many2one(
        "se.index",
        string="Index",
        required=True,
        # TODO: shall we use 'restrict' here to preserve existing data?
        ondelete="cascade",
    )
    sync_state = fields.Selection(
        [
            ("new", "New"),
            ("to_update", "To update"),
            ("scheduled", "Scheduled"),
            ("done", "Done"),
            ("to_be_checked", "To be checked"),
        ],
        default="new",
        readonly=True,
    )
    date_modified = fields.Datetime(readonly=True)
    date_syncronized = fields.Datetime(readonly=True)
    data = fields.Serialized()
    data_display = fields.Text(
        compute="_compute_data_display",
        help="Include this in debug mode to be able to inspect index data.",
    )
    active = fields.Boolean(string="Active", default=True)

    @api.depends("data")
    def _compute_data_display(self):
        for rec in self:
            rec.data_display = json.dumps(rec.data, sort_keys=True, indent=4)

    def get_export_data(self):
        """Public method to retrieve export data."""
        return self.data

    def _is_indexed(self):
        self.ensure_one()
        if self.sync_state == "new":
            return False
        elif self.sync_state == "done" and not self.active:
            return False
        return True

    @api.model
    def create(self, vals):
        record = super(SeBinding, self).create(vals)
        record.jobify_recompute_json()
        return record

    def write(self, vals):
        not_new = self.browse()
        if "active" in vals and not vals["active"]:
            not_new = self.filtered(lambda x: x.sync_state != "new")
            new_vals = vals.copy()
            new_vals["sync_state"] = "to_update"
            super(SeBinding, not_new).write(new_vals)

        res = super(SeBinding, self - not_new).write(vals)
        return res

    def _prepare_todelete_vals(self):
        self.ensure_one()
        return {
            "index_id": self.index_id.id,
            "binding_id": self.id,
        }

    def unlink(self):
        # Store unlinked binding ids in se.binding.todelete for a later processing
        todelete = self.filtered(lambda rec: rec._is_indexed())
        if todelete:
            todelete_vals_list = [rec._prepare_todelete_vals() for rec in todelete]
            self.env["se.binding.todelete"].sudo().create(todelete_vals_list)
        return super().unlink()

    def _get_binding_to_process(self, bindings, batch_size):
        return bindings[0:batch_size], bindings[batch_size:]  # noqa: E203

    def _jobify_get_job_description(self, processing):
        # We check if we are currently handling an exception in order
        # to change the job description.
        processing_count = len(processing)
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
            description = self._jobify_get_job_description(processing)
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
                return _("Job have been split because of failure.\nError: {}") % str(e)
            # We can't systematically reraise here, if we do the new jobs
            # will be discarded.
            raise

    def _work_by_index(self, active=True):
        self = self.exists()
        for backend in self.mapped("se_backend_id"):
            for index in self.mapped("index_id"):
                bindings = self.filtered(
                    lambda b, backend=backend, index=index: b.se_backend_id == backend
                    and b.index_id == index
                    and b.active == active
                )
                specific_backend = backend.specific_backend
                with specific_backend.work_on(
                    self._name, records=bindings, index=index
                ) as work:
                    yield work

    # TODO maybe we need to add lock (todo check)
    def _recompute_json(self, force_export=False):
        """Compute index record data as JSON."""
        # `sudo` because the recomputation can be triggered from everywhere
        # (eg: an update of a product in the stock) and is not granted
        # that the user triggering it has access to all required records
        # (eg: se.backend or related records needed to compute index values).
        # All in all, this is safe because the index data should always
        # be the same no matter the access rights of the user triggering this.
        result = []
        validation_errors = []
        to_be_checked = []
        for work in self.sudo()._work_by_index():
            mapper = work.component(usage="se.export.mapper")
            for binding in work.records.with_context(
                **self._recompute_json_work_ctx(work)
            ):
                index_record = mapper.map_record(binding).values()
                # Validate data and track items to check
                error = self._validate_record(work, index_record)
                if error:
                    msg = "{}: {}".format(str(binding), error)
                    _logger.error(msg)
                    validation_errors.append(msg)
                    to_be_checked.append(binding.id)
                    # skip record
                    continue
                if binding.data != index_record or force_export:
                    vals = {"data": index_record}
                    if binding.sync_state != "to_update":
                        vals["sync_state"] = "to_update"
                        vals["date_modified"] = fields.Datetime.now()
                    binding.write(vals)
        if validation_errors:
            result.append(_("Validation errors") + "\n" + "\n".join(validation_errors))
        if to_be_checked:
            self.browse(to_be_checked).write({"sync_state": "to_be_checked"})
        return "\n\n".join(result)

    def _recompute_json_work_ctx(self, work):
        ctx = {}
        if work.index.lang_id:
            ctx["lang"] = work.index.lang_id.code
        return ctx

    def _validate_record(self, work, index_record):
        return work.collection._validate_record(index_record)

    def synchronize(self):
        # We volontary do the export and delete in the same transaction
        # we try first to process it into two different process but the code
        # was more complex and it was harder to catch/understand
        # active/inactive case for example:
        #
        # 1. some body bind a product and an export job is created
        # 2. the binding is inactivated
        # 3. when the job runs we must exclude all inactive binding
        #
        # Hence in both export/delete we have to re-filter all bindings
        # using one transaction and one sync method allow to filter only once
        # and to do the right action as we are in a transaction.
        export_ids = []
        delete_ids = []
        for work in self.sudo()._work_by_index():
            exporter = work.component(usage="se.record.exporter")
            exporter.run()
            export_ids += work.records.ids
        for work in self.sudo()._work_by_index(active=False):
            deleter = work.component(usage="record.exporter.deleter")
            deleter.run()
            delete_ids += work.records.ids
        return "Exported ids : {}\nDeleted ids : {}".format(export_ids, delete_ids)
