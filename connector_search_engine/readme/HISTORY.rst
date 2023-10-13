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
