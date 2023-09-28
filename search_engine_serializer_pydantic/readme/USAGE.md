When you define a serializer based on a Pydantic model, your serializer class must
inherit from `PydanticModelSerializer` and implement the method `get_model_class` to
take advantage of the functionality provided by this module.

Example:

```python

from typing import Type
from pydantic import BaseModel

from odoo.addons.search_engine_serialize_pydantic.tools.serializer import (
    PydanticModelSerializer,
)


class MyModel(BaseModel):
    name: str
    description: str

    def record_to_model(self, record: Model) -> dict:
        return cls(
            name=record.name,
            description=record.description,
        )

class MyModelSerializer(PydanticModelSerializer):
    def get_model_class(self) -> Type[MyModel]:
        return MyModel

    def serialize(self, record: Model) -> dict:
        model: MyModel = self.get_model_class().record_to_model(record)
        return model.model_dump()

```
