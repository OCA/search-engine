# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models

from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class SeIndex(models.Model):

    _name = "se.index"
    _description = "Se Index"

    name = fields.Char(compute="_compute_name")
    backend_id = fields.Many2one(
        "se.backend", string="Backend", required=True, ondelete="cascade"
    )
    lang_id = fields.Many2one("res.lang", string="Lang", required=True)
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        domain=lambda self: self._model_id_domain(),
    )
    exporter_id = fields.Many2one("ir.exports", string="Exporter")
    batch_size = fields.Integer(default=5000, help="Batch size for exporting element")
    config_id = fields.Many2one(
        comodel_name="se.index.config",
        string="Config",
        help="Index configuration record",
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

    @api.model
    def _get_model_domain(self):
        _logger.warn("DEPRECATED: use `_model_id_domain`")
        return self._model_id_domain()

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
                processing.with_delay(description=description)._jobify_recompute_json(
                    force_export=force_export
                )
        return True

    @api.depends("lang_id", "model_id", "backend_id.index_prefix_name")
    def _compute_name(self):
        for rec in self:
            backend = rec.backend_id
            if rec.lang_id and rec.model_id and backend.index_prefix_name:
                rec.name = "_".join(
                    [
                        backend.index_prefix_name,
                        backend._normalize_name(rec.model_id.name or ""),
                        rec.lang_id.code,
                    ]
                )
            else:
                rec.name = ""

    def force_batch_export(self):
        self.ensure_one()
        bindings = self.env[self.model_id.model].search([("index_id", "=", self.id)])
        bindings.write({"sync_state": "to_update"})
        self._jobify_batch_export()

    def _jobify_batch_export(self):
        self.ensure_one()
        description = _("Prepare a batch export of index '%s'") % self.name
        self.with_delay(description=description).batch_export()

    @api.model
    def generate_batch_export_per_index(self, domain=None):
        if domain is None:
            domain = []
        for record in self.search(domain):
            record._jobify_batch_export()
        return True

    def _get_domain_for_exporting_binding(self):
        return [("index_id", "=", self.id), ("sync_state", "=", "to_update")]

    @job(default_channel="root.search_engine.prepare_batch_export")
    def batch_export(self):
        self.ensure_one()
        domain = self._get_domain_for_exporting_binding()
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
        """This method will iter on all item in the index of the search engine
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
            for se_binding in adapter.each():
                binding = self.env[index.model_id.model].search(
                    [("id", "=", se_binding[adapter._record_id_key])]
                )
                if not binding:
                    item_ids.append(se_binding[adapter._record_id_key])
            index.with_delay().delete_obsolete_item(item_ids)

    @job(default_channel="root.search_engine")
    def delete_obsolete_item(self, item_ids):
        adapter = self._get_backend_adapter()
        adapter.delete(item_ids)
