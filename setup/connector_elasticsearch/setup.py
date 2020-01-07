import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'external_dependencies_override': {
            'python': {
                'elasticsearch': 'elasticsearch>=7.0.0,<8.0.0',
            }
        }
    }
)
