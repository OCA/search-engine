[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/276/13.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-search-engine-276)
[![Build Status](https://travis-ci.org/OCA/search-engine.svg?branch=13.0)](https://travis-ci.org/OCA/search-engine)
[![codecov](https://codecov.io/gh/OCA/search-engine/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/search-engine)


Search Engine Connector for Odoo
===================================

This project include a generic search engine connector and specific implementation for algolia and elasticsearch.


[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[connector_algolia](connector_algolia/) | 13.0.1.0.0 | Connector For Algolia Search Engine
[connector_search_engine](connector_search_engine/) | 13.0.1.0.0 | Connector Search Engine


Unported addons
---------------
addon | version | summary
--- | --- | ---
[connector_elasticsearch](connector_elasticsearch/) | 12.0.0.1.1 (unported) | Connector For Elasticsearch Search Engine

[//]: # (end addons)


Developement
============

This project uses [black](https://github.com/ambv/black) as code formatting convention, as well as isort and flake8.
To make sure local coding convention are respected before you commit, install [pre-commit](https://github.com/pre-commit/pre-commit>) and run ``pre-commit install`` after cloning the repository.
