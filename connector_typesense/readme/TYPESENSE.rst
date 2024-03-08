typesense
~~~~~~~~~

requirements: to pretty print json, install jq on your system;


in terminal export the API key

.. code-block::

    export TYPESENSE_API_KEY='xyz'
    export TYPESENSE_HOST='http://localhost:8108'

list all collections (indexes):

.. code-block::

    curl -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
      "http://localhost:8108/collections" | jq


retrieve collection details of the products collection (index):

.. code-block::

    curl -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
      -X GET "http://localhost:8108/collections/typesense_backend_1_product_variant_en_us" | jq


list aliases:

.. code-block::
    curl -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
      "http://localhost:8108/aliases" | jq



get alias info:

.. code-block::
    curl -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
      "http://localhost:8108/aliases/typesense_backend_1_product_variant_en_us" | jq




search for all products:

curl -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
"http://localhost:8108/collections/typesense_backend_1_product_variant_en_us/documents/search?q=*" | jq


Typesense GUI
-------------

a nice UI is also available here: https://github.com/bfritscher/typesense-dashboard/releases

