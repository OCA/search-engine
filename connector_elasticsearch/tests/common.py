# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

import mock


class Indices(object):
    def __init__(self, index):
        self.elasticindex = index

    def exists(self, index):
        return False

    def create(self, index, body=None, params=None):  # pylint: disable=W8106
        # disabled error w8106 because since this is a mock class
        # I don't need to call super model's create
        self.elasticindex[index] = {"body": body, "params": params}
        return True

    def delete(self, index, ignore):
        res = {"acknowledged": True}
        return res


class ElasticsearchMock(object):
    def __init__(self):
        self.ipAddress = None
        self.port = None
        self.index = {}
        self.indices = Indices(self.index)
        # self.login = None
        # self.secret = None

    def ping(self):
        return True

    def delete(self):
        return True


class HelpersMock(object):
    def __init__(self):
        self.ipAddress = None
        self.port = None

    def bulk(self, es, dataforbulk):
        return [len(dataforbulk), []]


@contextmanager
def mock_api(env):
    helpers_mock = HelpersMock()
    elasticsearch_mock = ElasticsearchMock()

    def get_elasticmock_interface(servers):
        elasticsearch_mock.host = servers[0].get("host")
        elasticsearch_mock.port = servers[0].get("port")
        return elasticsearch_mock

    with mock.patch(
        "elasticsearch.Elasticsearch", get_elasticmock_interface
    ), mock.patch("elasticsearch.helpers", helpers_mock):
        yield elasticsearch_mock
