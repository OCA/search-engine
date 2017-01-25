# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector_search_engine.unit.mapper import JsonExportMapper
from ..backend import algolia


#@algolia
class JsonExportMapper(JsonExportMapper):

    def _apply(self, map_record, options=None):
        res = super(JsonExportMapper, self)._apply(map_record, options=None)
        res['objectID'] = res['id']
        return res
