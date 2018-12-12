# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SeBackend(models.Model):

    _name = 'se.backend'
    _description = 'Se Backend'
    _inherit = 'connector.backend'

    name = fields.Char(required=False)
    specific_model = fields.Selection(
        string='Type',
        selection=[],
        required=True,
        readonly=True
    )
    index_ids = fields.One2many(
        'se.index',
        'backend_id',
    )
    specific_backend = fields.Reference(
        string='Specific backend',
        compute='_compute_specific_backend',
        selection='_get_specific_backend_selection',
        readonly=True,
    )

    @api.model
    def _get_specific_backend_selection(self):
        spec_backend_selection = self._fields['specific_model'].selection
        vals = []
        s = self.with_context(active_test=False)
        for model, descr in spec_backend_selection:
            # We have to check if the table really exist.
            # Because in the case of the user uninstall a connector_XXX module
            # with a new se.backend (so who adds a new element into selection
            # field), no more se.backend will be available (because the
            # selection field still filled with the previous model and Odoo
            # try to load the model).
            # TODO v12: rely on `se.backend.` to retrieve models
            # and fix this table check.
            # if model in s.env and s.env[model]._table_exist():
            if model in s.env:
                records = s.env[model].search([])
                for record in records:
                    vals.append((model, record.id))
        return vals

    @api.model
    def register_spec_backend(self, specific_backend_model):
        """
        This function must be called by specific backend from the
        _requister_hoock method to register it into the allowed specific models
        :param self:
        :param specific_backend_model:
        """
        self._fields['specific_model'].selection.append((
            specific_backend_model._name, specific_backend_model._description))

    @api.depends('specific_model')
    @api.multi
    def _compute_specific_backend(self):
        for specific_model in self.mapped('specific_model'):
            recs = self.filtered(lambda r, model=specific_model:
                                 r.specific_model == model)
            backends = self.env[specific_model].search([
                ('se_backend_id', 'in', recs.ids)])
            backend_by_rec = {r.se_backend_id: r for r in backends}
            for rec in recs:
                spec_backend = backend_by_rec.get(rec)
                rec.specific_backend = '%s,%s' % (
                    spec_backend._name, spec_backend.id)
