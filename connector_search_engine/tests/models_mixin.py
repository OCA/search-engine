# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


class TestMixin(object):
    """Mixin to setup fake models for tests.

    Usage - the model:

        class FakeModel(models.Model, TestMixin):
            _name = 'fake.model'

            name = fields.Char()

    Usage - the test klass:

        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            FakeModel._test_setup_model(cls.env)

        @classmethod
        def tearDownClass(cls):
            FakeModel._test_teardown_model(cls.env)
            super().tearDownClass()
    """

    # Generate xmlids
    # This is needed if you want to load data tied to a test model via xid.
    _test_setup_gen_xid = False
    # If you extend a real model (ie: res.partner) you must enable this
    # to not delete the model on tear down.
    _test_teardown_no_delete = False
    # You can add custom fields to real models (eg: res.partner).
    # In this case you must delete them to leave registry and model clean.
    # This is mandatory for relational fields that link a fake model.
    _test_purge_fields = []

    @classmethod
    def _test_setup_model(cls, env):
        """Initialize it."""
        cls._build_model(env.registry, env.cr)
        env.registry.setup_models(env.cr)
        ctx = dict(env.context, update_custom_fields=True)
        if cls._test_setup_gen_xid:
            ctx['module'] = cls._module
        env.registry.init_models(env.cr, [cls._name], ctx)

    @classmethod
    def _test_teardown_model(cls, env):
        """Cleanup registry and real models."""

        for fname in cls._test_purge_fields:
            model = env[cls._name]
            if fname in model:
                model._pop_field(fname)

        if not getattr(cls, '_test_teardown_no_delete', False):
            del env.registry.models[cls._name]

    def _test_get_model_id(self):
        self.env.cr.execute(
            "SELECT id FROM ir_model WHERE model = %s", (self._name, ))
        res = self.env.cr.fetchone()
        return res[0] if res else None

    def _test_create_ACL(self, **kw):
        model_id = self._test_get_model_id()
        if not model_id:
            self._reflect()
            model_id = self._test_get_model_id()
        if model_id:
            vals = self._test_ACL_values(model_id)
            vals.update(kw)
            self.env['ir.model.access'].create(vals)

    def _test_ACL_values(self, model_id):
        values = {
            'name': 'Fake ACL for %s' % self._name,
            'model_id': model_id,
            'perm_read': 1,
            'perm_create': 1,
            'perm_write': 1,
            'perm_unlink': 1,
            'active': True,
        }
        return values
