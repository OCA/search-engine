# Copyright 2021 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools.sql import set_not_null


def migrate(cr, version):
    set_not_null(cr, "se_index", "lang_id")
