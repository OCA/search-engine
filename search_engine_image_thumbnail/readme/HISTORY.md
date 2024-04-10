## 16.0.1.0.5 (2024-04-10)

#### Bugfixes

- Add new config parameter on the search engine backend to allow the user
  to specify if the serialization of a record should fail if thumbnails are
  requested but no thumbnail sizes are defined for the model and field for
  which it' requested. Defaults to False (i.e. don't fail). ([#176](https://github.com/OCA/search-engine/issues/176))


## 16.0.1.0.4 (2024-04-09)

#### Bugfixes

- *Fixes image sizes lookups.*

  When serializing a record and generating thumbnails, the thumbnail sizes are looked
  up on the index. Prior to this change, only sizes defined for the model
  associated with the current index were looked up. This means that if you tried
  to serialize a nested record that had an image field that was defined on a different
  model, the thumbnail size was not found and an error was thrown. The lookup method
  takes now the record for which the thumbnail is being generated as an argument, so
  that the correct model can be used to look up the thumbnail size. You still need
  to define the thumbnail sizes for each model serialized in the index.


  *Fixes UI error when creating a new thumbnail size.*

  When creating a new record, the UI was throwing an error. This was due to the
  computations of the domain to apply to restrict the choices of the possible
  image fields. When the record is new, no model is set, so the domain for the
  field must be empty. This is now handled correctly. ([#174](https://github.com/OCA/search-engine/issues/174))
