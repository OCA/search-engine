# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mock
from odoo import api, models
from odoo.addons.component.tests.common import SavepointComponentCase


class TestSeBackend(models.Model):
    _name = 'test.se.backend'
    _inherit = 'se.backend.spec.abstract'
    _description = 'Unit Test SE Backend'

    def init(self):
        self.env['se.backend'].register_spec_backend(self)

    def _register_hook(self):
        self.env['se.backend'].register_spec_backend(self)


class TestSeBackendCase(SavepointComponentCase):
    """
    Tests With a fake Se Backend
    """

    def _init_test_model(self, model_cls):
        """
        Function to init/create a new Odoo Model during unit test.
        Based on base_kanban_stage/test/test_base_kanban_abstract.py
        :param model_cls: Odoo Model class
        :return: instance of model (empty)
        """
        registry = self.env.registry
        registry.enter_test_mode()
        cr = self.env.cr
        model_cls._build_model(registry, cr)
        model = self.env[model_cls._name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        return self.env[model_cls._name]

    def setUp(self):
        super(TestSeBackendCase, self).setUp()
        # To load a new Model, we have to use a new cursor and env.
        # Because there is a commit on the model._auto_init()
        # Based on base_kanban_stage/test/test_base_kanban_abstract.py
        # self.registry.enter_test_mode()
        # self.old_cursor = self.cr
        # self.cr = self.registry.cursor()
        self.cr.commit = mock.MagicMock()
        self.env = api.Environment(self.cr, self.uid, {})
        self._init_test_model(TestSeBackend)
        self.se_backend = self.env['test.se.backend'].create({
            'specific_model': 'test.se.backend',
        })

    def tearDown(self):
        self.registry.leave_test_mode()
        super(TestSeBackendCase, self).tearDown()
