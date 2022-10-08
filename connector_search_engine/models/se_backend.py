# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


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
    backend_type = fields.Selection(selection=[], string="Type", required=True)

    index_ids = fields.One2many("se.index", "backend_id")

    @property
    def _server_env_fields(self):
        return {"index_prefix_name": {}}

    @api.onchange("tech_name", "index_prefix_name")
    def _onchange_tech_name(self):
        res = super()._onchange_tech_name()
        if self.index_prefix_name:
            # make sure is normalized
            self.index_prefix_name = self._normalize_tech_name(self.index_prefix_name)
        else:
            self.index_prefix_name = self.tech_name
        return res

    def _handle_tech_name(self, vals):
        res = super()._handle_tech_name(vals)
        if not vals.get("index_prefix_name") and vals.get("tech_name"):
            vals["index_prefix_name"] = vals["tech_name"]
        return res

    def _get_api_credentials(self):
        # TODO: user self.name to retrieve creds from server env
        # TODO: username password etc
        return {}  # pragma: no cover

    @property
    def _record_id_key(self):
        # inherit this method if your search engine use a different key
        # as reference (ex: Algolia use objectID)
        return "id"

    def _validate_record(self, record):
        """Validate record for the specific search engine.

        :param record: a dict representing a record to index
        :return: error message if not validated, None if it's all good.
        """
        if not record:
            return _("The record is empty")
        if not record.get(self._record_id_key):
            # Ensure _record_id_key is set when creating/updating records
            return _("The key `%(record_key)s` is missing in:\n%(record)s") % dict(
                record_key=self._record_id_key,
                record=record,
            )
