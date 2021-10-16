import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-search-engine",
    description="Meta package for oca-search-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-connector_algolia',
        'odoo10-addon-connector_elasticsearch',
        'odoo10-addon-connector_search_engine',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 10.0',
    ]
)
