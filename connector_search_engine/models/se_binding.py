# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons.queue_job.job import job
from odoo.exceptions import UserError


class SeBinding(models.AbstractModel):
    _name = 'se.binding'
    _se_model = True

    se_backend_id = fields.Many2one(
        'se.backend',
        related="index_id.backend_id")
    index_id = fields.Many2one(
        'se.index',
        string="Index",
        required=True,
        # TODO: shall we use 'restrict' here to preserve existing data?
        ondelete='cascade'
    )
    sync_state = fields.Selection([
        ('new', 'New'),
        ('to_update', 'To update'),
        ('scheduled', 'Scheduled'),
        ('done', 'Done'),
    ],
        default='new',
        readonly=True)
    date_modified = fields.Date(readonly=True)
    date_syncronized = fields.Date(readonly=True)
    data = fields.Serialized()
    active = fields.Boolean(string="Active", default=True)

    def get_export_data(self):
        """Public method to retrieve export data."""
        return self.data

    @api.model
    def create(self, vals):
        record = super(SeBinding, self).create(vals)
        record._jobify_recompute_json()
        return record

    @api.multi
    def write(self, vals):
        if 'active' in vals and not vals['active'] and self.sync_state != 'new':
            vals['sync_state'] = 'to_update'
        record = super(SeBinding, self).write(vals)
        return record

    @api.multi
    def unlink(self):
        for record in self:
            if record.sync_state == 'new' or (
                    record.sync_state == 'done' and not record.active):
                continue
            if record.active:
                raise UserError(_(
                    "You cannot delete the binding '%s', unactivate it first.")
                    % record.name)
            else:
                raise UserError(_(
                    "You cannot delete the binding '%s', wait until it's synchronized.")
                    % record.name)
        result = super(SeBinding, self).unlink()
        return result

    def _jobify_recompute_json(self, force_export=False):
        description = _('Recompute %s json and check if need update'
                        % self._name)
        for record in self:
            record.with_delay(description=description).recompute_json(
                force_export=force_export)

    def _work_by_index(self, active=True):
        self = self.exists()
        for backend in self.mapped('se_backend_id'):
            for index in self.mapped('index_id'):
                bindings = self.filtered(
                    lambda b, backend=backend, index=index:
                    b.se_backend_id == backend and b.index_id == index
                    and b.active == active)
                specific_backend = backend.specific_backend
                with specific_backend.work_on(
                    self._name, records=bindings, index=index
                ) as work:
                    yield work

    # TODO maybe we need to add lock (todo check)
    @job(default_channel='root.search_engine.recompute_json')
    def recompute_json(self, force_export=False):
        for work in self._work_by_index():
            mapper = work.component(usage='se.export.mapper')
            lang = work.index.lang_id.code
            for record in work.records.with_context(lang=lang):
                data = mapper.map_record(record).values()
                if record.data != data or force_export:
                    vals = {'data': data}
                    if record.sync_state in ('done', 'new'):
                        vals['sync_state'] = 'to_update'
                    record.write(vals)

    @job(default_channel='root.search_engine')
    @api.multi
    def synchronize(self):
        export_ids = []
        delete_ids = []
        for work in self._work_by_index():
            exporter = work.component(usage='se.record.exporter')
            exporter.run()
            export_ids += work.records.ids
        for work in self._work_by_index(active=False):
            deleter = work.component(usage='record.exporter.deleter')
            deleter.run()
            delete_ids += work.records.ids
        return "Exported ids : %s\nDeleted ids : %s" % (export_ids, delete_ids)
