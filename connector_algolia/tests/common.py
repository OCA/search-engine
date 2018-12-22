# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
from urllib import parse as urlparse
from vcr import VCR


CASSETS_PATH = os.path.join(os.path.dirname(__file__), 'fixtures/cassettes')


class VCRMixin(object):

    @staticmethod
    def get_recorder(**kw):
        defaults = dict(
            record_mode='once',
            cassette_library_dir=CASSETS_PATH,
            path_transformer=VCR.ensure_suffix('.yml'),
            match_on=['method', 'path', 'query'],
            filter_headers=['Authorization'],
            decode_compressed_response=True,
        )
        defaults.update(kw)
        return VCR(**defaults)

    @staticmethod
    def parse_path(url):
        return urlparse.urlparse(url).path

    @staticmethod
    def parse_qs(url):
        return urlparse.parse_qs(urlparse.urlparse(url).query)
