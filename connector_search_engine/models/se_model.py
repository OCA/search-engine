# -*- coding: utf-8 -*-
# © 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging
from openerp import api, fields, models
from openerp.addons.connector.session import ConnectorSession
from ..connector import get_environment
from ..unit.exporter import SeExporter

_logger = logging.getLogger(__name__)


class SeBackend(models.Model):
    _name = 'se.backend'
    _description = 'Se Backend'
    _inherit = 'connector.backend'
    _backend_type = 'se'

    version = fields.Selection([], required=True)
    location = fields.Char()
    username = fields.Char()
    password = fields.Char()
    index_ids = fields.One2many(
        'se.index',
        'backend_id',
        string='Index')


class SeIndex(models.Model):
    _name = 'se.index'
    _description = 'Se Index'

    name = fields.Char(required=True)
    backend_id = fields.Many2one(
        'se.backend',
        string='Backend',
        required=True)
    lang_id = fields.Many2one(
        'res.lang',
        string='Lang',
        required=True)
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True)
    exporter_id = fields.Many2one(
        'ir.exports',
        string='Exporter')

    _sql_constraints = [
        ('lang_model_uniq', 'unique(backend_id, lang_id, model_id)',
         'Lang and model of index must be uniq per backend.'),
    ]

    @api.multi
    def export_all(self):
        for record in self:
            binding_obj = self.env[record.model_id.model]
            bindings = binding_obj.search([('index_id', '=', record.id)])
            bindings.write({'sync_state': 'to_update'})
            binding_obj._scheduler_export(
                domain=[('index_id', '=', record.id)])


class SeBinding(models.AbstractModel):
    _name = 'se.binding'

    se_backend_id = fields.Many2one(
        'se.backend',
        related="index_id.backend_id")
    index_id = fields.Many2one(
        'se.index',
        string="Index",
        required=True)
    sync_state = fields.Selection([
        ('to_update', 'To update'),
        ('scheduled', 'Scheduled'),
        ('done', 'Done'),
        ], default='to_update',
        readonly=True)
    date_modified = fields.Date(readonly=True)
    date_syncronized = fields.Date(readonly=True)

    @api.model
    def _scheduler_export(self, batch_size=5000, domain=None):
        if domain is None:
            domain = []
        domain.append(('sync_state', '=', 'to_update'))
        return self.search(domain).export_with_delay(batch_size)

    @api.multi
    def export_with_delay(self, batch_size=5000):
        session = ConnectorSession(self._cr, self._uid, self._context)
        datas = self.read_group(
            [('id', 'in', self.ids)], ['index_id'], ['index_id'])
        for data in datas:
            bindings = self.search(data['__domain'])
            while bindings:
                processing = bindings[0:batch_size]
                bindings = bindings[batch_size:]
                env = get_environment(session, self._name, data['index_id'][0])
                exporter = env.get_connector_unit(SeExporter)
                export_func = exporter.get_export_func()
                export_func.delay(session, self._name, processing.ids)
                processing.with_context(connector_no_export=True).write({
                    'sync_state': 'scheduled',
                    })
