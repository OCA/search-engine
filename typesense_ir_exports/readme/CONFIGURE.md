You need to have typesense search engine running and successfully connected to odoo.

Make sure to have `connector_search_engine` and `connector_typesense` modules installed.

## SE Index Config

Transition to: Search Engine > Configuration > Index configurations

Make sure to have this search index configuration in a new record:

    - Name: give it a unigue name
    - Body Str:

```json
{
  "name": "ts_products_collection",
  "fields": [
    {
      "name": "id",
      "type": "string"
    },
    {
      "name": "name",
      "type": "string"
    },
    {
      "name": ".*",
      "type": "auto",
      "optional": true
    }
  ],
  "enable_nested_fields": true
}
```

## SE Backend

Transition to: Search Engine > Configuration > Backends

Create a backend record, and create an index line with values:

    - Model: select the model you want to index
    - Serializer Type: Exporter
    - Exporter: select or create a new one and set
        - Resource: model technical name you want to index
        - Index lines: each line a technical name of the field of interest
    - Config: select or create the config se index record mentioned above

You can create and manage exporter templates through a button in the tree view once you
click on the exporter or the button under the `exporter_id` field in the se.index form
view.

## Media

![Backend Configuration](../static/img/backend.png){width=300}

![Exporter Dialog Button in Tree View](../static/img/exporter_dialog_button.png){width=300}

![Exporter Form View View](../static/img/exporter_form_view.png){width=300}

![Exporter Dialog](../static/img/exporter_dialog.png){width=300}
