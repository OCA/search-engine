This addon indexes and searches records into an OpenSearch_ cluster, using
the ``opensearch-py`` low level client. It is independent from
`connector_elasticsearch`: OpenSearch's client library is a fork of the
Elasticsearch one taken before their APIs diverged, so the two addons look
similar, but each is free to follow its own client library's evolution
without breaking the other.

Compared to talking to an OpenSearch cluster through `connector_elasticsearch`
and its Elasticsearch-compatibility layer, this addon brings:

* gzip compression of the HTTP payloads exchanged with the cluster
  (configurable per backend), reducing bandwidth usage on bulk indexing.
* a bulk delete that relies on OpenSearch's own handling of "document
  already absent" instead of a hand-rolled exception filter.
* an `each` (full index scan) that uses the ``opensearch-py`` scan helper,
  which clears its scroll context once exhausted instead of leaving it
  open until it expires.

.. _OpenSearch: https://opensearch.org/
