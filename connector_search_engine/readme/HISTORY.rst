16.0.0.1.7 (2023-12-15)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Ensure that the record's model is compatible with the index's model before
  adding a new record to the index.

  Before this change, the index would silently ignore records that were not
  compatible with the index's model. This could lead to unexpected behavior and
  errors when the record was later used to be serialized to JSON and exported to
  a search engine. (`#177 <https://github.com/OCA/search-engine/issues/177>`_)
- Lower memory consumption by disabling prefetch for the field 'data' on the binding model.

  The field 'data' is a json field that is not used in the view or common management
  operations of the binding model. This json field can be very large. By disabling
  the prefetch, we avoid to overload the database and Odoo with useless data. (`#179 <https://github.com/OCA/search-engine/issues/179>`_)


16.0.0.1.4 (2023-11-29)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Fix error when calling the methods *export_record* or *delete_record* from
  the *se.binding* model when called on a recordset with items from different
  *se.backend*.

  The *export* and *delete* methods involves the use of a *Backend Adapter* to
  communicate with the target search engine. We then need to process the bindings
  by backend to call the correct adapter and ensure at same time a batch process
  of the requested operation for all the records linked to the same backend. (`#173 <https://github.com/OCA/search-engine/issues/173>`_)


16.0.0.1.2 (2023-11-28)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Add missing description on the "se.binding.state.updater" model. As well as
  ensuring consistency in the model definition, this change removes a
  warning message from the server logs at registry load time.

  Prevent warning message in server logs when running tests. (`#172 <https://github.com/OCA/search-engine/issues/172>`_)


16.0.0.1.1 (2023-10-13)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Fixes cache issue with the *se_binding_ids* field on the *s.indexable.record*
  model. When a binding is created or updated or deleted, the cache for the
  *se_binding_ids* field for referenced records is now invalidated. That way,
  the next time the field is accessed after such an operation, the value is
  recomputed to reflect the change. (`#163 <https://github.com/OCA/search-engine/issues/163>`_)


16.0.0.1.0 (2023-10-13)
~~~~~~~~~~~~~~~~~~~~~~~

**Features**

- A new action **Update state** is now available on *Search Engine Record* objects.
  This action allows you to update the state of selected records on the tree view.

  Add a smart button to quickly access to the bound records from the
  *Search Engine Backend* and *Search Engine Record* views. (`#162 <https://github.com/OCA/search-engine/issues/162>`__)


**Bugfixes**

- Fix Search Engine Binding form view. The fields data and error are now
  properly displayed and fit the width of the form.

  Makes the Odoo's admin user a member of the *Search Engine Connector Manager* group. (`#162 <https://github.com/OCA/search-engine/issues/162>`__)


12.0.x.y.z (YYYY-MM-DD)
~~~~~~~~~~~~~~~~~~~~~~~

TODO
