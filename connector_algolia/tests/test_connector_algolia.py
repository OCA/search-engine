# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo import _
from odoo.addons.queue_job.job import Job


from .common import ConnectorAlgoliaCase
from .common import mock_api
from .models import ResPartner


class TestConnectorAlgolia(ConnectorAlgoliaCase):

    def _init_test_model(self, model_cls):
        registry = self.env.registry
        cr = self.env.cr
        inst = model_cls._build_model(registry, cr)
        model = self.env[model_cls._name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        return inst

    def setUp(self):
        super(TestConnectorAlgolia, self).setUp()
        ir_model_res_partner = self.env['ir.model'].search(
            [('model', '=', 'res.partner')])
        res_lang = self.env['res.lang'].search([], limit=1)
        exporter_id = self.env.ref('base_jsonify.ir_exp_partner')
        self.se_index_model = self.env['se.index']
        self.se_index = self.se_index_model.create({
            'name': 'partner index',
            'backend_id': self.backend.se_backend_id.id,
            'model_id': ir_model_res_partner.id,
            'lang_id': res_lang.id,
            'exporter_id': exporter_id.id
        })
        # init our test model after the creation of the index since this one
        # will be used as default value
        # we must mock the commit to be sure that odoo will not commit when
        # initializing the model
        self.cr.commit = mock.MagicMock()
        self._init_test_model(ResPartner)

    def test_export_all_indexes(self):

        with mock_api(self.env) as mocked_api:
            self.assertFalse(self.se_index.name in mocked_api.index)
            self.se_index_model.export_all_index(delay=False)
            self.assertTrue(self.se_index.name in mocked_api.index)
            index = mocked_api.index[self.se_index.name]
            self.assertEqual(1, len(index._calls))
            method, values = index._calls[0]
            self.assertEqual('add_objects', method)
            self.assertEqual(
                self.env['res.partner'].search_count([]),
                len(values)
            )

    def test_export_jobs(self):
        queue_job_model = self.env['queue.job']
        existing_jobs = queue_job_model.search([])
        with mock_api(self.env) as mocked_api:
            self.assertFalse(self.se_index.name in mocked_api.index)
            self.se_index_model.export_all_index(delay=True)
        # by default the export method create 2 jobs
        # the first one to split the bindings to export into batch
        # the second one to export each batch
        new_jobs = queue_job_model.search([])
        new_job = new_jobs - existing_jobs
        self.assertEqual(1, len(new_job))
        job = Job.load(self.env, new_job.uuid)
        self.assertEqual(
            _('Prepare a batch export of indexes'),
            job.description)
        # at this stage the mocked_api is not yet called
        self.assertFalse(self.se_index.name in mocked_api.index)
        # perform the job
        existing_jobs = new_jobs
        job.perform()
        new_jobs = queue_job_model.search([])
        new_job = new_jobs - existing_jobs
        self.assertEqual(1, len(new_job))
        job = Job.load(self.env, new_job.uuid)
        count = self.env['res.partner'].search_count([])
        self.assertEqual(
            _("Export %d records of %d for index 'partner index'") % (
                count, count),
            job.description)
        self.assertFalse(self.se_index.name in mocked_api.index)
        # the last job is the one performing the export
        job = Job.load(self.env, new_job.uuid)
        with mock_api(self.env) as mocked_api:
            job.perform()
        self.assertTrue(self.se_index.name in mocked_api.index)
