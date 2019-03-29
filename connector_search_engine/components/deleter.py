# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2018 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class SeDeleter(Component):
    _name = "se.deleter"
    _inherit = ["base.se.connector", "base.deleter"]
    _usage = "record.exporter.deleter"
    _base_backend_adapter_usage = "se.backend.adapter"

    def run(self):
        """
        Run the synchronization, delete the record on the backend
        :param records: recordset
        :return: bool
        """
        self.work.records.write({"sync_state": "done"})
        record_ids = [x.record_id.id for x in self.work.records]
        if record_ids:
            return self.backend_adapter.delete(record_ids)
