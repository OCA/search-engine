16.0.0.3.0
~~~~~~~~~~

* elasticsearch v8 compatibility: The connector now supports Elasticsearch
  v8.*.* versions.

12.0.?.?.? (unreleased)
~~~~~~~~~~~~~~~~~~~~~~~

* connector_elasticsearch: Makes the config on index required only if the
  index is linked to an elastisearch backend. This change allows the usage
  of algolia search engine at the same time as elasticsearch.
