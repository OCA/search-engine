# -*- coding: utf-8 -*-
# © 2013 Akretion (http://www.akretion.com)
# Raphaël Valyi <raphael.valyi@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models


class NosqlBackend(models.Model):
    _inherit = 'nosql.backend'

    def _select_versions(self):
        res = super(NosqlBackend, self)._select_versions()
        res.append(('algolia_v1', 'Algolia V1'))
        return res
