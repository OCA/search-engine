# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Connector Search Engine",
    "version": "16.0.0.1.17",
    "author": "Akretion,"
    "ACSONE SA/NV,"
    "Camptocamp,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/search-engine",
    "license": "AGPL-3",
    "category": "Generic Modules",
    "depends": ["queue_job", "mail", "server_environment", "base_partition"],
    "external_dependencies": {"python": ["unidecode", "typing-extensions"]},
    "data": [
        "wizards/se_binding_state_updater.xml",
        "security/connector_search_engine_security.xml",
        "security/se_index_config.xml",
        "security/ir.model.access.csv",
        "views/se_backend.xml",
        "views/se_index.xml",
        "views/se_binding_view.xml",
        "views/se_index_config.xml",
        "views/se_menu.xml",
        "data/ir_cron.xml",
        "data/queue_job_channel_data.xml",
        "data/queue_job_function_data.xml",
        "data/ir_action_data.xml",
    ],
    "installable": True,
}
