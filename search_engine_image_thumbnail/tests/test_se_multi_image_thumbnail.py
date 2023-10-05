# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestSeMultiImageThumbnailCase


class TestSeMultiImageThumbnail(TestSeMultiImageThumbnailCase):
    def test_thumbnail_size_model_domain(self):
        expected = [
            (
                "model",
                "in",
                ["test.fsimage", "test.image", "test.multi.image"],
            )
        ]
        domain = self.env["se.image.field.thumbnail.size"]._model_id_domain()
        self.assertEqual(domain, expected)

    def test_thumbnail_zise_field_domain(self):
        model_id = self.test_multi_image_model_id
        se_thumbnail_size = self.env["se.image.field.thumbnail.size"].new(
            {"model_id": model_id}
        )
        field_id_domain = se_thumbnail_size.field_id_domain
        self.assertEqual(
            field_id_domain,
            [["name", "in", ["image_ids"]], ["model_id", "=", model_id]],
        )

    def test_multi_image_record_create_thumbnail(self):
        thumbnails = self.test_multi_image._get_or_create_thumbnails_for_multi_images(
            self.index_multi_image, "image_ids"
        )
        # we have 2 images and 2 sizes. We should have 4 thumbnails
        image1 = self.test_multi_image.image_ids[0]
        image2 = self.test_multi_image.image_ids[1]
        self.assertEqual(len(thumbnails), 2)
        self.assertEqual(len(thumbnails[image1]), 2)
        self.assertEqual(len(thumbnails[image2]), 2)
        # check that the size is correct
        for thumbnail_size, thumbnail in thumbnails[image1]:
            self.assert_image_size(
                thumbnail.image.getvalue(),
                width=thumbnail_size.size_x,
                height=thumbnail_size.size_y,
            )
            self.assertEqual(thumbnail_size.size_x, thumbnail.size_x)
            self.assertEqual(thumbnail_size.size_y, thumbnail.size_y)
            self.assertEqual(thumbnail.base_name, self.test_multi_image.display_name)

    def test_image_record_create_thumbnail(self):
        thumbnails = self.test_image._get_or_create_thumbnails_for_image(
            self.index_image, "image"
        )
        # we have 2 images and 2 sizes. We should have 4 thumbnails
        self.assertEqual(len(thumbnails), 2)
        # check that the size is correct
        for thumbnail_size, thumbnail in thumbnails:
            self.assert_image_size(
                thumbnail.image.getvalue(),
                width=thumbnail_size.size_x,
                height=thumbnail_size.size_y,
            )
            self.assertEqual(thumbnail_size.size_x, thumbnail.size_x)
            self.assertEqual(thumbnail_size.size_y, thumbnail.size_y)
            self.assertEqual(thumbnail.base_name, "test-image")

    def test_fsimage_record_create_thumbnail(self):
        thumbnails = self.test_fsimage._get_or_create_thumbnails_for_image(
            self.index_fsimage, "image"
        )
        # we have 2 images and 2 sizes. We should have 4 thumbnails
        self.assertEqual(len(thumbnails), 2)
        # check that the size is correct
        for thumbnail_size, thumbnail in thumbnails:
            self.assert_image_size(
                thumbnail.image.getvalue(),
                width=thumbnail_size.size_x,
                height=thumbnail_size.size_y,
            )
            self.assertEqual(thumbnail_size.size_x, thumbnail.size_x)
            self.assertEqual(thumbnail_size.size_y, thumbnail.size_y)
            self.assertEqual(thumbnail.base_name, "test-fsimage")
