# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


try:
    import algoliasearch
except ImportError:
    _logger.debug('Can not import algoliasearch')


class AlgoliaAdapter(Component):
    _name = "algolia.adapter"
    _inherit = ['base.backend.adapter', 'algolia.se.connector']
    _usage = 'se.backend.adapter'

    def _get_index(self):
        backend = self.backend_record
        account = backend._get_existing_keychain()
        client = algoliasearch.client.Client(
            backend.algolia_app_id, account._get_password())
        return client.initIndex(self.work.index.name)

    def add(self, datas):
        index = self._get_index()
        index.add_objects(datas)

    def delete(self, binding_ids):
        index = self._get_index()
        index.delete_objects(binding_ids)
