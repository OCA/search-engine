# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class SeIndex(models.Model):

    _name = "se.index"
    _description = "Se Index"

    name = fields.Char(compute="_compute_name")
    custom_tech_name = fields.Char(
        help="Take control of index technical name. "
        "The final index name is still computed and contains in any case: "
        "backend index name prefix and language if given. "
        "If no custom name is provided, model's normalized name will be used."
    )
    backend_id = fields.Many2one(
        "se.backend", string="Backend", required=True, ondelete="cascade"
    )
    lang_id = fields.Many2one("res.lang", string="Lang", required=False)
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        domain=lambda self: self._model_id_domain(),
        ondelete="cascade",
    )
    exporter_id = fields.Many2one("ir.exports", string="Exporter")
    batch_size = fields.Integer(default=5000, help="Batch size for exporting element")
    config_id = fields.Many2one(
        comodel_name="se.index.config",
        string="Config",
        help="Index configuration record",
    )
    binding_todelete_ids = fields.One2many(
        comodel_name="se.binding.todelete",
        inverse_name="index_id",
        string="Bindings to delete",
        readonly=True,
    )

    @api.model
    def _model_id_domain(self):
        se_model_names = []
        for model in self.env:
            if self.env[model]._abstract or self.env[model]._transient:
                continue
            if hasattr(self.env[model], "_se_model"):
                se_model_names.append(model)
        return [("model", "in", se_model_names)]

    _sql_constraints = [
        (
            "lang_model_uniq",
            "unique(backend_id, lang_id, model_id)",
            "Lang and model of index must be uniq per backend.",
        )
    ]

    @api.onchange("model_id")
    def onchange_model_id(self):
        self.exporter_id = False
        if self.model_id:
            domain = [("resource", "=", self.model_id.model)]
            return {"domain": {"exporter_id": domain}}

    @api.model
    def recompute_all_index(self, domain=None):
        if domain is None:
            domain = []
        return self.search(domain).recompute_all_binding()

    def force_recompute_all_binding(self):
        for record in self:
            record.recompute_all_binding(force_export=True)

    def recompute_all_binding(self, force_export=False, batch_size=500):
        target_models = self.mapped("model_id.model")
        for target_model in target_models:
            indexes = self.filtered(lambda r, m=target_model: r.model_id.model == m)
            bindings = self.env[target_model].search([("index_id", "in", indexes.ids)])
            while bindings:
                processing = bindings[0:batch_size]  # noqa: E203
                bindings = bindings[batch_size:]  # noqa: E203
                description = _("Batch task for generating %s recompute job") % len(
                    processing
                )
                processing.with_delay(description=description).jobify_recompute_json(
                    force_export=force_export
                )
        return True

    @api.depends(
        "custom_tech_name", "lang_id", "model_id", "backend_id.index_prefix_name"
    )
    def _compute_name(self):
        for rec in self:
            if not rec.backend_id:
                # in onchange on concrete views rec is a new Id
                # so we can't calc the right name.
                rec.name = ""
            else:
                rec.name = rec._make_name()

    def _make_name(self):
        """Compute the final name of the index."""
        name = ""
        backend = self.backend_id
        tech_name = self._make_tech_name()
        if tech_name:
            if not backend.index_prefix_name:
                # index_prefix_name should be not empty
                # indeed from the UI the index_prefix_name is alway fill base on
                # tech_name
                # So if it's empty it because we have change some config using
                # server env or using dataencryption module
                # in that case we set the default value to fix everything
                backend._onchange_tech_name()
            bits = [backend.index_prefix_name, tech_name]
            if self.lang_id:
                bits.append(self.lang_id.code)
            name = "_".join(bits)
        return name

    def _make_tech_name(self):
        """Compute the main part of the name of the index."""
        tech_name = self.custom_tech_name or self.model_id.name or ""
        return self.backend_id._normalize_tech_name(tech_name)

    def force_batch_export(self):
        self.ensure_one()
        self._jobify_batch_export(force_export=True)

    def _jobify_batch_export(self, force_export=False):
        self.ensure_one()
        description = _("Prepare a batch export of index '%s'") % self.name
        self.with_delay(description=description).batch_export(force_export)

    @api.model
    def generate_batch_export_per_index(self, domain=None):
        if domain is None:
            domain = []
        for record in self.search(domain):
            record._jobify_batch_export()
        return True

    def _get_domain_for_exporting_binding(self, force_export=False):
        domain = [("index_id", "=", self.id)]
        if not force_export:
            domain.append(("sync_state", "=", "to_update"))
        return domain

    def _batch_export(self, force_export=False):
        self.ensure_one()
        domain = self._get_domain_for_exporting_binding(force_export)
        binding_obj = self.env[self.model_id.model]
        bindings = binding_obj.with_context(active_test=False).search(domain)
        bindings_count = len(bindings)
        while bindings:
            processing = bindings[0 : self.batch_size]  # noqa: E203
            bindings = bindings[self.batch_size :]  # noqa: E203
            description = _("Export %d records of %d for index '%s'") % (
                len(processing),
                bindings_count,
                self.name,
            )
            processing.with_delay(description=description).synchronize()
            processing.with_context(connector_no_export=True).write(
                {"sync_state": "scheduled"}
            )

    def _batch_delete(self):
        self.ensure_one()
        binding_todelete_ids = self.binding_todelete_ids
        binding_todelete_count = len(binding_todelete_ids)
        while binding_todelete_ids:
            processing = binding_todelete_ids[0 : self.batch_size]  # noqa: E203
            binding_todelete_ids = binding_todelete_ids[self.batch_size :]  # noqa: E203
            description = _(
                "Delete %d obsolete records of %d for index '%s'",
                len(processing),
                binding_todelete_count,
                self.name,
            )
            processing.with_delay(description=description).synchronize()

    def batch_export(self, force_export=False):
        self.ensure_one()
        self._batch_export(force_export=force_export)
        self._batch_delete()
        return True

    def _get_backend_adapter(self, backend=None, model=None, index=None, **kw):
        backend = backend or self.backend_id.specific_backend
        model = model or self._name
        index = index or self
        with backend.work_on(model, index=index, **kw) as work:
            return work.component(usage="se.backend.adapter")

    def clear_index(self):
        self.ensure_one()
        adapter = self._get_backend_adapter()
        adapter.clear()
        return True

    def _get_settings(self):
        """
        Override this method is sub modules in order to pass the adequate
        settings (like Facetting, pagination, advanced settings, etc...)
        """
        self.ensure_one()
        return {}

    @api.model
    def export_all_settings(self):
        self.search([]).export_settings()

    def export_settings(self):
        for index in self:
            se_specific_backend = index.backend_id.specific_backend
            with se_specific_backend.work_on(index.model_id.model, index=index) as work:
                exporter = work.component(usage="se.record.exporter")
                exporter.export_settings()

    def resynchronize_all_bindings(self):
        """Force sync between Odoo records and index records.

        This method will iter on all item in the index of the search engine
        if the corresponding binding do not exist on odoo it will create a job
        that delete all this obsolete items.
        You should not use this method for day to day job, it only an helper
        for recovering your index after a dammage.
        You can also drop index but this will introduce downtime, so it's
        better to force a resynchronization"""
        for index in self:
            item_ids = []
            backend = index.backend_id.specific_backend
            adapter = self._get_backend_adapter(backend=backend, index=index)
            binding_model = self.env[index.model_id.model]
            for index_record in adapter.each():
                ext_id = adapter.external_id(index_record)
                binding = binding_model.browse(ext_id).exists()
                if not binding:
                    item_ids.append(ext_id)
            index.with_delay().delete_obsolete_item(item_ids)

    def delete_obsolete_item(self, item_ids):
        adapter = self._get_backend_adapter()
        adapter.delete(item_ids)
        return f"Deleted ids : {item_ids}"
