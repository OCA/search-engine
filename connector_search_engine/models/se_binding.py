# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.job import job


class SeBinding(models.AbstractModel):
    _name = "se.binding"
    _se_model = True
    _description = "Search Engine Binding"

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
        ],
        default="new",
        readonly=True,
    )
    date_modified = fields.Date(readonly=True)
    date_syncronized = fields.Date(readonly=True)
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

    @api.model
    def create(self, vals):
        record = super(SeBinding, self).create(vals)
        record._jobify_recompute_json()
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

    def unlink(self):
        for record in self:
            if record.sync_state == "new" or (
                record.sync_state == "done" and not record.active
            ):
                continue
            if record.active:
                raise UserError(
                    _("You cannot delete the binding '%s', unactivate it " "first.")
                    % record.name
                )
            else:
                raise UserError(
                    _(
                        "You cannot delete the binding '%s', "
                        "wait until it's synchronized."
                    )
                    % record.name
                )
        return super(SeBinding, self).unlink()

    @job(default_channel="root.search_engine.recompute_json")
    def _jobify_recompute_json(self, force_export=False):
        description = _("Recompute %s json and check if need update" % self._name)
        # The job creation with tracking is very costly. So disable it.
        for record in self.with_context(tracking_disable=True):
            record.with_delay(description=description).recompute_json(
                force_export=force_export
            )

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
    @job(default_channel="root.search_engine.recompute_json")
    def recompute_json(self, force_export=False):
        """Compute index record data as JSON."""
        # `sudo` because the recomputation can be triggered from everywhere
        # (eg: an update of a product in the stock) and is not granted
        # that the user triggering it has access to all required records
        # (eg: se.backend or related records needed to compute index values).
        # All in all, this is safe because the index data should always
        # be the same no matter the access rights of the user triggering this.
        for work in self.sudo()._work_by_index():
            mapper = work.component(usage="se.export.mapper")
            lang = work.index.lang_id.code
            for record in work.records.with_context(lang=lang):
                data = mapper.map_record(record).values()
                if record.data != data or force_export:
                    vals = {"data": data}
                    if record.sync_state in ("done", "new"):
                        vals["sync_state"] = "to_update"
                    record.write(vals)

    @job(default_channel="root.search_engine")
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
        for work in self._work_by_index():
            exporter = work.component(usage="se.record.exporter")
            exporter.run()
            export_ids += work.records.ids
        for work in self._work_by_index(active=False):
            deleter = work.component(usage="record.exporter.deleter")
            deleter.run()
            delete_ids += work.records.ids
        return "Exported ids : {}\nDeleted ids : {}".format(export_ids, delete_ids)
