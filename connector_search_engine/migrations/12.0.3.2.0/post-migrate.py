# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for backend in env["se.backend"].search([("tech_name", "=", False)]):
        backend.tech_name = backend.name
        _logger.info(
            "Backend '%s' `tech_name` set equal to its name. "
            "Please consider changing the name to a normalized name. "
            "This will require indexes renaming.",
            backend.name,
        )
