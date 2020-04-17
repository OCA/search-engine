# -*- coding: utf-8 -*-
# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import mock
import urlparse

from odoo import tools
from odoo.modules.module import get_resource_path

from odoo.addons.component.tests.common import SavepointComponentCase

# mute `test_queue_job_no_delay` logging
logging.getLogger("odoo.addons.queue_job.models.base").setLevel("CRITICAL")


def load_xml(env, module, filepath):
    with mock.patch.object(env.cr.__class__, "commit"):
        tools.convert_file(
            env.cr,
            module,
            get_resource_path(module, filepath),
            {},
            mode="init",
            noupdate=False,
            kind="test",
        )


class TestSeBackendCaseBase(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestSeBackendCaseBase, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,  # speed up tests
                # TODO: requires https://github.com/OCA/queue/pull/114
                test_queue_job_no_delay=True,  # no jobs thanks
            )
        )

    @classmethod
    def _load_fixture(cls, fixture, module="connector_search_engine"):
        load_xml(cls.env, module, "tests/fixtures/%s" % fixture)

    @staticmethod
    def parse_path(url):
        return urlparse.urlparse(url).path
