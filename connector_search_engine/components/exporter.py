# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class SeExporter(Component):
    _name = "se.exporter"
    _inherit = ["base.se.connector", "base.exporter"]
    _usage = "se.record.exporter"
    _base_mapper_usage = "se.export.mapper"
    _base_backend_adapter_usage = "se.backend.adapter"

    def _index(self, records):
        """ Index the record """
        return self.backend_adapter.index(records)

    def run(self):
        """ Run the synchronization """
        if self.work.records:
            # TODO: this state should be set _after_ the indexing
            # the best will to add an extra state "sync_running"
            # and setting this state here.
            # Then we create a job (with the id of the index search task)
            # and we ask the search engine if it finish or not and
            # when it's finish we set the binding in done
            self.work.records.write({"sync_state": "done"})
            return self._index(
                [record.get_export_data() for record in self.work.records]
            )

    def export_settings(self, force=True):
        """ Run the settings synchronization """
        return self.backend_adapter.settings(force=force)
