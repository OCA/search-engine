# Copyright 2013 Akretion (http://www.akretion.com)
# @author Sébestien Beau <sebastien.beau@akretion.com>
# Copyright 2020 Camptomcap (http://www.camptomcamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SeBackendSpecAbstract(models.AbstractModel):
    _name = "se.backend.spec.abstract"
    _description = "Se Specialized Backend"
    _inherit = "connector.backend"

    # declare a unique name for this search engine service
    # (eg: elasticsearch, algolia, my-super-engine).
    # This can be used by other modules to understand
    # which engine they are dealing with
    _search_engine_name = ""
    # Unique index record key
    _record_id_key = None

    # Delegation inheritance
    se_backend_id = fields.Many2one(
        comodel_name="se.backend",
        ondelete="cascade",
        index=True,
        auto_join=True,
        delegate=True,
        required=True,
    )
    # This must be re-defined here because
    # we want to be able to set the prefix based on the specific search engine.
    index_prefix_name = fields.Char(
        related="se_backend_id.index_prefix_name", readonly=False,
    )

    @property
    def _server_env_fields(self):
        # We need this because calling `super` in the specific backend
        # won't call the property from `se.backend` because of `inherits` behavior.
        return {"index_prefix_name": {}}

    @api.model
    def create(self, vals):
        vals["specific_model"] = self._name
        return super(SeBackendSpecAbstract, self).create(vals)

    def unlink(self):
        se_backend = self.mapped("se_backend_id")
        res = super(SeBackendSpecAbstract, self).unlink()
        # NOTE: this will delete indexes and bindings by cascade
        se_backend.unlink()
        return res

    def _get_api_credentials(self):
        # TODO: user self.name to retrieve creds from server env
        # TODO: username password etc
        return {}  # pragma: no cover

    def _validate_record(self, record):
        """Validate record for the specific search engine.

        :param record: a dict representing a record to index
        :return: error message if not validated, None if it's all good.
        """
        if not record:
            return _("The record is empty")
        if not record.get(self._record_id_key):
            # Ensure _record_id_key is set when creating/updating records
            return _("The key `%s` is missing in:\n%s") % (self._record_id_key, record)
