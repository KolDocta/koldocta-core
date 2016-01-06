
import io
import bson
import flask
import unittest

from koldocta.upload import bp
from koldocta.storage.desk_media_storage import KoldoctaGridFSMediaStorage
from eve.io.mongo import Mongo

from mock import Mock


class GridFSMediaStorageTestCase(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config['SERVER_NAME'] = 'localhost'
        self.app.data = Mongo(self.app)   
        self.app.config['DOMAIN'] = {'upload': {}}
        self.media = KoldoctaGridFSMediaStorage(self.app)
        self.app.register_blueprint(bp)

    def test_media_id(self):
        filename = 'some-file'
        media_id = self.media.media_id(filename)
        self.assertIsInstance(media_id, bson.ObjectId)
        self.assertEqual(media_id, self.media.media_id(filename))

    def test_url_for_media(self):
        _id = self.media.media_id('test')
        with self.app.app_context():
            url = self.media.url_for_media(_id)
        self.assertEqual('http://localhost/upload/%s/raw' % _id, url)

    def test_put_media_with_id(self):
        data = io.StringIO(u"test data")
        filename = 'x'

        gridfs = Mock()
        gridfs.put = Mock(return_value='y')
        self.media._fs['MONGO'] = gridfs
        _id = bson.ObjectId()

        with self.app.app_context():
            self.media.put(data, filename, 'text/plain', _id=str(_id))

        kwargs = {
            'content_type': 'text/plain',
            'filename': filename,
            'metadata': None,
            '_id': _id,
        }

        gridfs.put.assert_called_once_with(data, **kwargs)
