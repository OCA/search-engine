# -*- coding: utf-8 -*-
# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    @api.model
    def export_all_index(self, domain=None, delay=True):
        if domain is None:
            domain = []
        return self.search(domain).export_all(delay=delay)

    @api.multi
    def export_all(self, delay=True):
        for record in self:
            binding_obj = self.env[record.model_id.model]
            bindings = binding_obj.search([('index_id', '=', record.id)])
            bindings.write({'sync_state': 'to_update'})
            binding_obj._scheduler_export(
                domain=[('index_id', '=', record.id)], delay=delay)
        return True
