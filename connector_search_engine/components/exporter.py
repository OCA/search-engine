# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class SeExporter(Component):
    _name = "se.exporter"
    _inherit = ["base.se.connector", "base.exporter"]
    _usage = "se.binding.exporter"
    _base_mapper_usage = "se.export.mapper"
    _base_backend_adapter_usage = "se.backend.adapter"

    def _index(self, records):
        """Index the record"""
        return self.backend_adapter.index(records)

    def run(self):
        """Run the synchronization"""
        if self.work.records:
            return self._index(
                [record.get_export_data() for record in self.work.records]
            )

    def export_settings(self, force=True):
        """Run the settings synchronization"""
        return self.backend_adapter.settings(force=force)
