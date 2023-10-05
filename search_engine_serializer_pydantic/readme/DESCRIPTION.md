This module is a technical module that define a new abstract class named
`PydandicModelSerializer` that inherit from
`odoo.addons.connector_search_engine.tools.serializer.ModelSerializer`

This new class define a new abstract method `get_model_class`. This method is used by
the index to get the Pydantic model class to use to generate the json schema.

On the index form, if the serializer is a `PydanticModelSerializer`, a field is
displayed to display the related json schema and therefore provide documentation about
the fields exported and their characteristics.
