# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector.backend import Backend
from openerp.addons.connector_se.backend import se


algolia = Backend(parent=se)
""" Algolia Backend"""

algolia = Backend(parent=algolia, version='algolia_v1')
""" Algolia Backend"""
