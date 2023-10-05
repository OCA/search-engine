# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import OrderedDict

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.connector_search_engine.models.se_index import SeIndex
from odoo.addons.fs_base_multi_image.models.fs_image_relation_mixin import (
    FsImageRelationMixin,
)
from odoo.addons.fs_image.fields import FSImageValue
from odoo.addons.fs_image_thumbnail.models.fs_image_thumbnail_mixin import (
    FsImageThumbnailMixin,
)

from .se_thumbnail_size import SeThumbnailSize


class SeIndexableRecord(models.AbstractModel):
    _inherit = "se.indexable.record"

    def _get_or_create_thumbnails_for_multi_images(
        self, index: SeIndex, field_name: str
    ) -> OrderedDict[
        FsImageRelationMixin, list[tuple[SeThumbnailSize, FsImageThumbnailMixin]]
    ]:
        """Create a thumbnail for a multi image field.

        :param index: The index where the record should be added
        :param field_name: The name of the field
        :return:  a ordered dictionary where the key is the original image
            relation and the value is a list of tuple(se.thumbnail.size, se.thumbnail)
            (The order of the dict is the order of the images in the original Odoo record)

        """
        self.ensure_one()
        thumbnail_sizes_by_size = self._get_thumbnail_sizes_by_size_for_field(
            index, field_name
        )
        images: FsImageRelationMixin = self[field_name]
        if not isinstance(images, FsImageRelationMixin):
            raise SystemError(
                "This code is designed to work with FsImageRelationMixin fields"
            )
        se_tumbnail_model = self._get_thumbnail_model()
        thumbnails_by_image = se_tumbnail_model.get_or_create_thumbnails(
            *images.mapped("image"),
            sizes=thumbnail_sizes_by_size.keys(),
            base_name=self._get_image_url_key(index, field_name)
        )
        res = OrderedDict[
            FsImageRelationMixin, list[tuple[SeThumbnailSize, FsImageThumbnailMixin]]
        ]()
        for image in images:
            res[image] = [
                (
                    thumbnail_sizes_by_size[(thumbnail.size_x, thumbnail.size_y)],
                    thumbnail,
                )
                for thumbnail in thumbnails_by_image.get(image.image, [])
            ]
        return res

    def _get_or_create_thumbnails_for_image(
        self, index: SeIndex, field_name: str
    ) -> list[tuple[SeThumbnailSize, FsImageThumbnailMixin]]:
        """Create a thumbnail for an image field.

        :param index: The index where the record should be added
        :param field_name: The name of the field. (should be a fields.Image or FSImage) field
        :return:  a list of tuple(se.thumbnail.size, fs.image.thumbnail.mixi)
        """
        thumbnail_sizes_by_size = self._get_thumbnail_sizes_by_size_for_field(
            index, field_name
        )
        image = self[field_name]
        field = self._fields[field_name]
        if isinstance(field, fields.Image):
            attachment = self._get_attachement_for_image_field(field_name)
            if attachment:
                image = FSImageValue(attachment)
        if not image:
            return []
        assert isinstance(image, FSImageValue)

        se_tumbnail_model = self._get_thumbnail_model()
        thumbnails_by_image = se_tumbnail_model.get_or_create_thumbnails(
            image,
            sizes=thumbnail_sizes_by_size.keys(),
            base_name=self._get_image_url_key(index, field_name),
        )
        thumbnails = thumbnails_by_image.get(image, [])
        return [
            (
                thumbnail_sizes_by_size[(thumbnail.size_x, thumbnail.size_y)],
                thumbnail,
            )
            for thumbnail in thumbnails
        ]

    def _get_thumbnail_sizes_by_size_for_field(
        self, index: SeIndex, field_name: str
    ) -> SeThumbnailSize:
        """Return a recordset of thumbnail size for the given field_name.

        :param index: The index where the record should be added
        :param field_name: The name of the field
        :return: a dictionary where the key is typle (size_x, size_y) and the
            value is the thumbnail size record
        """
        self.ensure_one()
        sizes = index._get_thumbnail_sizes(field_name)
        if not sizes:
            raise UserError(
                _(
                    "No thumbnail sizes defined for %(model)s.%(field)s",
                    field=field_name,
                    model=self._name,
                )
            )
        return {(size.size_x, size.size_y): size for size in sizes}

    def _get_image_url_key(self, index: SeIndex, field_name: str):
        """Return the key used to build the image url.

        :param index: The index where the record should be added
        :param field_name: The name of the field for which we want to build the
            thumbnaul image url key
        :return: a string
        """
        self.ensure_one()
        return self.display_name

    def _get_attachement_for_image_field(self, field_name: str):
        """Return the attachement for the given image field.

        :param field_name: The name of the field
        :return: a recordset of ir.attachment
        """
        self.ensure_one()
        domain = [
            ("res_model", "=", self._name),
            ("res_field", "=", field_name),
            ("res_id", "=", self.id),
        ]
        return self.env["ir.attachment"].sudo().search(domain)

    def _get_thumbnail_model(self):
        """
        :return: the se.thumbnail model to use to store generated thumbnails
        """
        return self.env["se.thumbnail"]
