import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-search-engine",
    description="Meta package for oca-search-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-connector_elasticsearch>=15.0dev,<15.1dev',
        'odoo-addon-connector_search_engine>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
