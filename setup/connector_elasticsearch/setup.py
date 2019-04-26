# -*- coding: utf-8 -*-
import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addons={
        'external_dependencies_override': {
            'python': {
                'elasticsearch': 'elasticsearch>=6.0.0,<7.0.0',
            }
        }
    }
)
