# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class SeBackend(models.Model):

    _name = "se.backend"
    _description = "Se Backend"
    _inherit = [
        "connector.backend",
        "server.env.techname.mixin",
        "server.env.mixin",
    ]

    name = fields.Char(required=True)
    index_prefix_name = fields.Char(
        help="Prefix for technical indexes tech name. "
        "You could use this to change index names based on current env."
    )
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

    @property
    def _server_env_fields(self):
        return {"index_prefix_name": {}}

    @property
    def search_engine_name(self):
        return self.specific_backend._search_engine_name

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
            res.extend([(model, record.name) for record in self.env[model].search([])])
        return res

    @api.depends("specific_model")
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

    @api.onchange("tech_name", "index_prefix_name")
    def _onchange_tech_name(self):
        super()._onchange_tech_name()
        if self.index_prefix_name:
            # make sure is normalized
            self.index_prefix_name = self._normalize_tech_name(self.index_prefix_name)
        else:
            self.index_prefix_name = self.tech_name

    def _handle_tech_name(self, vals):
        super()._handle_tech_name(vals)
        if not vals.get("index_prefix_name") and vals.get("tech_name"):
            vals["index_prefix_name"] = vals["tech_name"]
