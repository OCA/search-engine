# -*- coding: utf-8 -*-
# © 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging
from datetime import datetime
from openerp import fields, models

_logger = logging.getLogger(__name__)


class NosqlBackend(models.Model):
    _name = 'nosql.backend'
    _description = 'Nosql Backend'
    _inherit = 'connector.backend'
    _backend_type = 'nosql'

    def _select_versions(self):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return []

    version = fields.Selection(
        '_select_versions',
        required=True)
    location = fields.Char(required=True)
    username = fields.Char()
    password = fields.Char()
    index_ids = fields.One2many(
        'nosql.index',
        'backend_id',
        string='Index')

    def output_recorder(self):
        """ Utility method to output a file containing all the recorded
        requests / responses with Solr.  Used to generate test data.
        Should be called with ``erppeek`` for instance.
        """
        from .unit.backend_adapter import output_recorder
        import os
        import tempfile
        fmt = '%Y-%m-%d-%H-%M-%S'
        timestamp = datetime.now().strftime(fmt)
        filename = 'output_%s_%s' % (self._cr.dbname, timestamp)
        path = os.path.join(tempfile.gettempdir(), filename)
        output_recorder(path)
        return path


class NosqlIndex(models.Model):
    _name = 'nosql.index'
    _description = 'Nosql Index'

    name = fields.Char(required=True)
    backend_id = fields.Many2one(
        'nosql.backend',
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
        string='Exporter',
        required=True)


class NosqlBinding(models.AbstractModel):
    _name = 'nosql.binding'

    backend_id = fields.Many2one('nosql.backend')
    sync_state = fields.Selection([
        ('to_update', 'To update'),
        ('scheduled', 'Scheduled'),
        ('done', 'Done'),
        ], default='to_update',
        readonly=True)
    date_modified = fields.Date(readonly=True)
    date_syncronized = fields.Date(readonly=True)
