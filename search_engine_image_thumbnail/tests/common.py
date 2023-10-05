# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import io

from odoo_test_helper import FakeModelLoader
from PIL import Image

from odoo.addons.connector_search_engine.tests.common import TestSeBackendCaseBase
from odoo.addons.fs_image.fields import FSImageValue


class TestSeMultiImageThumbnailCase(TestSeBackendCaseBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.connector_search_engine.tests.models import SeBackend, SeIndex

        from .models import TestFSImage, TestImage, TestImageRelation, TestMultiImage

        cls.loader.update_registry(
            (
                SeIndex,
                SeBackend,
                TestImage,
                TestFSImage,
                TestImageRelation,
                TestMultiImage,
            )
        )
        cls.backend = cls.env["se.backend"].create(
            {"name": "Fake SE", "tech_name": "fake_se", "backend_type": "fake"}
        )

        # models
        cls.test_multi_image_model = cls.env["test.multi.image"]
        cls.test_image_model = cls.env["test.image"]
        cls.test_fsimage_model = cls.env["test.fsimage"]
        cls.test_image_relation = cls.env["test.image.relation"]

        # model ids
        cls.test_multi_image_model_id = cls.env.ref(
            "search_engine_image_thumbnail.model_test_multi_image"
        ).id
        cls.test_image_model_id = cls.env.ref(
            "search_engine_image_thumbnail.model_test_image"
        ).id
        cls.test_fsimage_model_id = cls.env.ref(
            "search_engine_image_thumbnail.model_test_fsimage"
        ).id

        # field ids
        cls.multi_images_field_id = cls.env.ref(
            "search_engine_image_thumbnail.field_test_multi_image__image_ids"
        ).id
        cls.image_field_id = cls.env.ref(
            "search_engine_image_thumbnail.field_test_image__image"
        ).id
        cls.fsimage_field_id = cls.env.ref(
            "search_engine_image_thumbnail.field_test_fsimage__image"
        ).id

        cls.index_multi_image = cls.env["se.index"].create(
            {
                "name": "fake_index",
                "backend_id": cls.backend.id,
                "model_id": cls.test_multi_image_model_id,
            }
        )
        cls.index_image = cls.env["se.index"].create(
            {
                "name": "fake_index",
                "backend_id": cls.backend.id,
                "model_id": cls.test_image_model_id,
            }
        )
        cls.index_fsimage = cls.env["se.index"].create(
            {
                "name": "fake_index",
                "backend_id": cls.backend.id,
                "model_id": cls.test_fsimage_model_id,
            }
        )

        # create some thumbnail sizes (small and medium)
        cls.size_small = cls.env["se.thumbnail.size"].create(
            {
                "name": "small",
                "key": "small",
                "size_x": 5,
                "size_y": 5,
            }
        )
        cls.size_medium = cls.env["se.thumbnail.size"].create(
            {
                "name": "medium",
                "key": "medium",
                "size_x": 10,
                "size_y": 10,
            }
        )

        # create some thumbnail sizes (small and medium for each models)
        cls.test_multi_image_size = cls.env["se.image.field.thumbnail.size"].create(
            {
                "model_id": cls.test_multi_image_model_id,
                "field_id": cls.multi_images_field_id,
                "backend_id": cls.backend.id,
                "size_ids": [(6, 0, [cls.size_small.id, cls.size_medium.id])],
            }
        )
        cls.test_image_size = cls.env["se.image.field.thumbnail.size"].create(
            {
                "model_id": cls.test_image_model_id,
                "field_id": cls.image_field_id,
                "backend_id": cls.backend.id,
                "size_ids": [(6, 0, [cls.size_small.id, cls.size_medium.id])],
            }
        )
        cls.test_fsimage_size = cls.env["se.image.field.thumbnail.size"].create(
            {
                "model_id": cls.test_fsimage_model_id,
                "field_id": cls.fsimage_field_id,
                "backend_id": cls.backend.id,
                "size_ids": [(6, 0, [cls.size_small.id, cls.size_medium.id])],
            }
        )

        # create some PNG images
        cls.image_blank = cls._create_image(20, 20, color="#FFFFFF")
        cls.image_black = cls._create_image(20, 20, color="#000000")

        # create some records
        cls.test_multi_image = cls.test_multi_image_model.create(
            {
                "name": "test",
                "image_ids": [
                    (
                        0,
                        0,
                        {
                            "specific_image": FSImageValue(
                                name="blank.png",
                                value=cls.image_blank,
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
                                value=cls.image_black,
                            ),
                            "sequence": 1,
                        },
                    ),
                ],
            }
        )
        cls.test_image = cls.test_image_model.create(
            {
                "name": "test Image",
                "image": base64.b64encode(cls.image_blank),
            }
        )
        cls.test_fsimage = cls.test_fsimage_model.create(
            {
                "name": "test FSImage",
                "image": FSImageValue(
                    name="blank.png",
                    value=cls.image_blank,
                ),
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    @classmethod
    def _create_image(cls, width, height, color="#4169E1", img_format="PNG"):
        f = io.BytesIO()
        Image.new("RGB", (width, height), color).save(f, img_format)
        f.seek(0)
        return f.read()

    def assert_image_size(self, value: bytes, width, height):
        self.assertEqual(Image.open(io.BytesIO(value)).size, (width, height))
