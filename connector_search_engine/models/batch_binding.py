# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class BatchBinding(models.AbstractModel):
    _name = "batch.binding"

    sync_state = fields.Selection([
        ('to_update', 'To update'),
        ('scheduled', 'Scheduled'),
        ('done', 'Done'),
        ], default='to_update',
        readonly=True)
    date_modified = fields.Date(readonly=True)
    date_syncronized = fields.Date(readonly=True)
