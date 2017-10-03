# -*- coding: utf-8 -*-
# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons.queue_job.job import job


class SeBinding(models.AbstractModel):
    _name = 'se.binding'

    se_backend_id = fields.Many2one(
        'se.backend',
        related="index_id.backend_id")
    index_id = fields.Many2one(
        'se.index',
        string="Index",
        required=True)
    sync_state = fields.Selection(
        [('to_update', 'To update'),
         ('scheduled', 'Scheduled'),
         ('done', 'Done')],
        default='to_update',
        readonly=True)
    date_modified = fields.Date(readonly=True)
    date_syncronized = fields.Date(readonly=True)

    @job(default_channel='root.search_engine')
    @api.model
    def _scheduler_export(self, batch_size=5000, domain=None, delay=True):
        if domain is None:
            domain = []
        domain.append(('sync_state', '=', 'to_update'))
        records = self.search(domain)
        if delay:
            description = _('Prepare a batch export of indexes')
            records = records.with_delay(description=description)
        return records.export_batch(batch_size, delay=delay)

    @job(default_channel='root.search_engine')
    @api.multi
    def export_batch(self, batch_size=5000, delay=True):
        datas = self.read_group(
            [('id', 'in', self.ids)], ['index_id'], ['index_id'])
        for data in datas:
            bindings = self.search(data['__domain'])
            bindings_count = len(bindings)
            while bindings:
                todo = processing = bindings[0:batch_size]
                bindings = bindings[batch_size:]
                if delay:
                    description = _(
                        "Export %d records of %d for index '%s'") % (
                            len(processing),
                            bindings_count,
                            data['index_id'][1])
                    todo = processing.with_delay(description=description)
                todo.export()
                processing.with_context(connector_no_export=True).write({
                    'sync_state': 'scheduled',
                })

    @job(default_channel='root.search_engine')
    @api.multi
    def export(self):
        for backend in self.mapped('se_backend_id'):
            for index in self.mapped('index_id'):
                bindings = self.filtered(
                    lambda b, backend=backend, index=index:
                    b.se_backend_id == backend and b.index_id == index)
                specific_backend = backend.specific_backend
                with specific_backend.work_on(
                    self._name, records=bindings, index=index
                ) as work:
                    exporter = work.component(usage='se.record.exporter')
                    exporter.run()
