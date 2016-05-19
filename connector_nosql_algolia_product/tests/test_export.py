# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector_nosql_algolia.tests.common import (
    mock_api,
    SetUpAlgoliaBase,
)
from openerp.addons.connector.tests.common import mock_job_delay_to_direct


class ExportProduct(SetUpAlgoliaBase):

    def setUp(self):
        super(ExportProduct, self).setUp()
        self.index = self.env.ref('connector_nosql_algolia_product.index_1')

    def test_export_product(self):
        path = (
            'openerp.addons.connector_nosql_algolia.'
            'unit.exporter.export_record')
        expected_ids = []
        for xml_id in (3, 4):
            tmpl = self.env.ref(
                'product.product_product_%s_product_template' % xml_id)
            binding = self.env['nosql.product.template'].create({
                'backend_id': self.backend.id,
                'record_id': tmpl.id,
                'index_id': self.index.id,
                })
            expected_ids.append(binding.id)
        with mock_job_delay_to_direct(path), mock_api() as API:
            self.env['nosql.product.template']._scheduler_export()

            # Check that only one index have been call
            self.assertEqual(len(API.index), 1)

            # Check that only right index have been call
            index_name = API.index.keys()[0]
            self.assertEqual(index_name, self.index.name)

            # Check the call done
            calls = API.index[index_name]._calls
            self.assertEqual(len(calls), 1)

            # Check the method call
            method, params = calls[0]
            self.assertEqual(method, 'add_objects')

            # Check the product exported
            exported_ids = [p['objectID'] for p in params]
            self.assertEqual(exported_ids, expected_ids)
