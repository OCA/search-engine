# Copyright 2023 Kencove (https://kencove.com).
# @author Mohamed Alkobrosli <malkobrosly@kencove.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


class IrExportsResolver:
    """
    The role of this class is to convert data of branches
    into a the form of data that jsonifer module can jsonify.

    I assume that the data coming from ir.exports record is looking like this:
    {
        'fields': [
            {'name': 'name'},
            (
                {'name': 'categ_id'},
                [{'name': 'name'}, {'name': 'sale_ok'}, {'name': 'purchase_ok'}]
            )
        ]
    }

    The final datastructure should look similar to this structure:
    ["id", "name", ("categ_id", ["id", "name", "sale_ok", "purchase_ok"])]
    """

    def __init__(self, parser):
        fields = []
        if parser.get("fields") and isinstance(parser["fields"], list):
            fields = parser["fields"]
        self.resolved_parser = [self.convert(field) for field in fields]

    def get_dict_key(self, field):
        if isinstance(field, dict) and "name" in field:
            return field["name"]
        else:
            return field

    def convert(self, field):
        if isinstance(field, dict):
            return self.get_dict_key(field)
        elif isinstance(field, tuple) and len(field) == 2:
            parent, children = field
            if isinstance(parent, dict):
                return (
                    self.get_dict_key(parent),
                    [self.get_dict_key(child) for child in children],
                )
        else:
            return field
