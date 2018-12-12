# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mock
from odoo import models
from odoo.addons.component.tests.common import SavepointComponentCase
from odoo.addons.component.core import Component


class TestSeBackend(models.Model):
    _name = 'test.se.backend'
    _inherit = 'se.backend.spec.abstract'
    _description = 'Unit Test SE Backend'

    def init(self):
        self.env['se.backend'].register_spec_backend(self)

    def _register_hook(self):
        self.env['se.backend'].register_spec_backend(self)


class TestSeAdapter(Component):
    _name = "test.se.adapter"
    _inherit = 'base.backend.adapter'
    _usage = 'se.backend.adapter'
    _collection = 'test.se.backend'
    _called = []

    def index(self, datas):
        self._called.append(('index', datas))

    def delete(self, binding_ids):
        self._called.append(('delete', binding_ids))

    def clear(self):
        self._called.append(('clear', None))


class TestSeBackendCase(SavepointComponentCase):
    """
    Tests With a fake Se Backend
    """

    @classmethod
    def _init_test_model(cls, model_cls):
        """
        Function to init/create a new Odoo Model during unit test.
        Based on base_kanban_stage/test/test_base_kanban_abstract.py
        :param model_cls: Odoo Model class
        :return: instance of model (empty)
        """
        registry = cls.env.registry
        cr = cls.env.cr
        model_cls._build_model(registry, cr)
        model = cls.env[model_cls._name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        return cls.env[model_cls._name]

    @classmethod
    def setUpClass(cls):
        super(TestSeBackendCase, cls).setUpClass()
        cls.env.cr.commit = mock.MagicMock()
        cls._init_test_model(TestSeBackend)
        TestSeAdapter._build_component(cls._components_registry)

    def setUp(self):
        super(TestSeBackendCase, self).setUp()
        self.se_backend = self.env['test.se.backend'].create({
            'specific_model': 'test.se.backend',
        })
        self._adapter_called = TestSeAdapter._called = []

    @classmethod
    def tearDownClass(cls):
        # The cursor have been not commited as it have been mocked
        # so there is not table 'test_se_backend' in the DB
        # but the registry have been polluted by the class test.se.backend
        # To avoid having error message (missing table 'test.se.backend' when
        # running the test on several module
        # We flag this class as an abstract class
        # so odoo will do not care that the table do not exist
        cls.env.registry['test.se.backend']._abstract = True
        super(TestSeBackendCase, cls).tearDownClass()
