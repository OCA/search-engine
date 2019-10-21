# -*- coding: utf-8 -*-
# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class SeBackend(models.Model):

    _name = "se.backend"
    _description = "Se Backend"
    _inherit = "connector.backend"

    # We can't leave this field required in database, because of strange
    # behaviors with name field defined already on connector.backend, which is
    # inherited by both se.backend and se.backend.spec.abstract.
    # In next version, the field is removed from connector.backend, so we
    # do not have this issue. Also a related field have been added on
    # se.backend.spec.abstract, this field is also removed in next version
    name = fields.Char(required=False)
    specific_model = fields.Selection(
        string="Type", selection="_select_specific_model", required=True, readonly=True
    )
    index_ids = fields.One2many("se.index", "backend_id")
    specific_backend = fields.Reference(
        string="Specific backend",
        compute="_compute_specific_backend",
        selection="_select_specific_backend",
        readonly=True,
    )

    @api.model
    @tools.ormcache("self")
    def _select_specific_model(self):
        """Retrieve available specific models via matchin prefix.

        You can still override this to inject your own model
        in case you use a 100% custom name for it.
        """
        models = self.env["ir.model"].search(
            [
                ("model", "like", "se.backend.%"),
                ("model", "!=", "se.backend.spec.abstract"),
            ]
        )
        # we check if the model exist in the env
        # indeed during module upgrade the model may not exist yet
        return [(x.model, x.name) for x in models if x.model in self.env]

    @api.model
    @tools.ormcache("self")
    def _select_specific_backend(self):
        """Retrieve available specific backends."""
        res = []
        for model, __ in self._select_specific_model():
            res.extend(
                [
                    ("{},{}".format(model, record.id), record.name)
                    for record in self.env[model].search([])
                ]
            )
        return res

    @api.depends("specific_model")
    @api.multi
    def _compute_specific_backend(self):
        for specific_model in self.mapped("specific_model"):
            recs = self.filtered(
                lambda r, model=specific_model: r.specific_model == model
            )
            backends = self.env[specific_model].search(
                [("se_backend_id", "in", recs.ids)]
            )
            backend_by_rec = {r.se_backend_id: r for r in backends}
            for rec in recs:
                spec_backend = backend_by_rec.get(rec)
                rec.specific_backend = "{},{}".format(
                    spec_backend._name, spec_backend.id
                )
