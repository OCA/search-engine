Use Exporter (ir.exports) as serializer for connector_typesense

Each ir.exports records is converted into JSON and JSON data get indexed into the Search Engine.

Data can be String, Integer, Float, Lists, and Relations in the form of Object.

Thnaks to the dynamic Schema configuration we can add new fields or remove without breaking the Schema.

Binary data like images are sent as string, but better if we use external filestore to use images related external urls.
