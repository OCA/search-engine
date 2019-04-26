# -*- coding: utf-8 -*-
import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addons={
        'external_dependencies_override': {
            'python': {
                'algoliasearch': 'algoliasearch>=1.0.0,<2.0.0',
            }
        }
    }
)
