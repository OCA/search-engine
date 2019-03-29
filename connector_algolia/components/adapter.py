# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging

from odoo import _
from odoo.addons.component.core import Component
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


try:
    import algoliasearch
except ImportError:  # pragma: no cover
    _logger.debug("Can not import algoliasearch")


class AlgoliaAdapter(Component):
    _name = "algolia.adapter"
    _inherit = ["base.backend.adapter", "algolia.se.connector"]
    _usage = "se.backend.adapter"

    def _get_index(self):
        backend = self.backend_record
        account = backend._get_api_credentials()
        client = algoliasearch.client.Client(
            backend.algolia_app_id, account["password"]
        )
        return client.initIndex(self.work.index.name)

    def index(self, records):
        index = self._get_index()
        # Ensure that the objectID is set because algolia will use it
        # for creating or updating the record
        for data in records:
            if not data.get(self._record_id_key):
                raise UserError(
                    _("The key %s is missing in the data %s")
                    % (self._record_id_key, data)
                )
        index.add_objects(records)

    def delete(self, binding_ids):
        index = self._get_index()
        index.delete_objects(binding_ids)

    def clear(self):
        index = self._get_index()
        index.clear_index()

    def iter(self):
        index = self._get_index()
        return index.browse_all()
