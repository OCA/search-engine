# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import io

from odoo_test_helper import FakeModelLoader
from PIL import Image

from odoo.addons.connector_search_engine.tests.common import TestSeBackendCaseBase
from odoo.addons.fs_image.fields import FSImageValue


class TestSeMultiImageThumbnailCase(TestSeBackendCaseBase):
    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        from odoo.addons.connector_search_engine.tests.models import SeBackend, SeIndex

        from .models import TestFSImage, TestImage, TestImageRelation, TestMultiImage

        self.loader.update_registry(
            (
                SeIndex,
                SeBackend,
                TestImage,
                TestFSImage,
                TestImageRelation,
                TestMultiImage,
            )
        )
        self.backend = self.env["se.backend"].create(
            {"name": "Fake SE", "tech_name": "fake_se", "backend_type": "fake"}
        )

        # models
        self.test_multi_image_model = self.env["test.multi.image"]
        self.test_image_model = self.env["test.image"]
        self.test_fsimage_model = self.env["test.fsimage"]
        self.test_image_relation = self.env["test.image.relation"]

        # model ids
        self.test_multi_image_model_id = self.env.ref(
            "search_engine_image_thumbnail.model_test_multi_image"
        ).id
        self.test_image_model_id = self.env.ref(
            "search_engine_image_thumbnail.model_test_image"
        ).id
        self.test_fsimage_model_id = self.env.ref(
            "search_engine_image_thumbnail.model_test_fsimage"
        ).id

        # field ids
        self.multi_images_field_id = self.env.ref(
            "search_engine_image_thumbnail.field_test_multi_image__image_ids"
        ).id
        self.image_field_id = self.env.ref(
            "search_engine_image_thumbnail.field_test_image__image"
        ).id
        self.fsimage_field_id = self.env.ref(
            "search_engine_image_thumbnail.field_test_fsimage__image"
        ).id

        self.index_multi_image = self.env["se.index"].create(
            {
                "name": "fake_multi_image_index",
                "backend_id": self.backend.id,
                "model_id": self.test_multi_image_model_id,
            }
        )
        self.index_image = self.env["se.index"].create(
            {
                "name": "fake_image_index",
                "backend_id": self.backend.id,
                "model_id": self.test_image_model_id,
            }
        )
        self.index_fsimage = self.env["se.index"].create(
            {
                "name": "fake_fsimage_index",
                "backend_id": self.backend.id,
                "model_id": self.test_fsimage_model_id,
            }
        )

        # create some thumbnail sizes (small and medium)
        self.size_small = self.env["se.thumbnail.size"].create(
            {
                "name": "small",
                "key": "small",
                "size_x": 5,
                "size_y": 5,
            }
        )
        self.size_medium = self.env["se.thumbnail.size"].create(
            {
                "name": "medium",
                "key": "medium",
                "size_x": 10,
                "size_y": 10,
            }
        )

        # create some thumbnail sizes (small and medium for each models)
        self.test_multi_image_size = self.env["se.image.field.thumbnail.size"].create(
            {
                "model_id": self.test_multi_image_model_id,
                "field_id": self.multi_images_field_id,
                "backend_id": self.backend.id,
                "size_ids": [(6, 0, [self.size_small.id, self.size_medium.id])],
            }
        )
        self.test_image_size = self.env["se.image.field.thumbnail.size"].create(
            {
                "model_id": self.test_image_model_id,
                "field_id": self.image_field_id,
                "backend_id": self.backend.id,
                "size_ids": [(6, 0, [self.size_small.id, self.size_medium.id])],
            }
        )
        self.test_fsimage_size = self.env["se.image.field.thumbnail.size"].create(
            {
                "model_id": self.test_fsimage_model_id,
                "field_id": self.fsimage_field_id,
                "backend_id": self.backend.id,
                "size_ids": [(6, 0, [self.size_small.id, self.size_medium.id])],
            }
        )

        # create some PNG images
        self.image_blank = self._create_image(20, 20, color="#FFFFFF")
        self.image_black = self._create_image(20, 20, color="#000000")

        # create some records
        self.test_multi_image = self.test_multi_image_model.create(
            {
                "name": "test",
                "image_ids": [
                    (
                        0,
                        0,
                        {
                            "specific_image": FSImageValue(
                                name="blank.png",
                                value=self.image_blank,
                            ),
                            "sequence": 2,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "specific_image": FSImageValue(
                                name="black.png",
                                value=self.image_black,
                            ),
                            "sequence": 1,
                        },
                    ),
                ],
            }
        )
        self.test_image = self.test_image_model.create(
            {
                "name": "test Image",
                "image": base64.b64encode(self.image_blank),
            }
        )
        self.test_fsimage = self.test_fsimage_model.create(
            {
                "name": "test FSImage",
                "image": FSImageValue(
                    name="blank.png",
                    value=self.image_blank,
                ),
            }
        )

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()

    @classmethod
    def _create_image(cls, width, height, color="#4169E1", img_format="PNG"):
        f = io.BytesIO()
        Image.new("RGB", (width, height), color).save(f, img_format)
        f.seek(0)
        return f.read()

    def assert_image_size(self, value: bytes, width, height):
        self.assertEqual(Image.open(io.BytesIO(value)).size, (width, height))
