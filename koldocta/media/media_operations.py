# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/koldocta/license


import arrow
import magic
import hashlib
import logging
import requests
from bson import ObjectId
from io import BytesIO
from flask import json
import base64
from koldocta.errors import KoldoctaApiError

logger = logging.getLogger(__name__)


def hash_file(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def get_file_name(file):
    return hash_file(file, hashlib.sha256())


def download_file_from_url(url):
    rv = requests.get(url, timeout=15)
    if rv.status_code not in (200, 201):
        raise KoldoctaApiError.internalError('Failed to retrieve file from URL: %s' % url)

    mime = magic.from_buffer(rv.content, mime=True).decode('UTF-8')
    ext = mime.split('/')[1]
    name = str(ObjectId()) + ext
    return BytesIO(rv.content), name, mime


def download_file_from_encoded_str(encoded_str):
    content = encoded_str.split(';base64,')
    mime = content[0].split(':')[1]
    ext = content[0].split('/')[1]
    name = str(ObjectId()) + ext
    content = base64.b64decode(content[1])
    return BytesIO(content), name, mime


def process_file_from_stream(content, content_type=None):
    content_type = content_type or content.content_type
    content = BytesIO(content.read())
    if 'application/' in content_type:
        content_type = magic.from_buffer(content.getvalue(), mime=True).decode('UTF-8')
        content.seek(0)
    file_type, ext = content_type.split('/')
    try:
        metadata = process_file(content, file_type)
    except OSError:  # error from PIL when image is supposed to be an image but is not.
        raise KoldoctaApiError.internalError('Failed to process file')
    file_name = get_file_name(content)
    content.seek(0)
    metadata = encode_metadata(metadata)
    metadata.update({'length': json.dumps(len(content.getvalue()))})
    return file_name, content_type, metadata


def encode_metadata(metadata):
    return dict((k.lower(), json.dumps(v)) for k, v in metadata.items())


def decode_metadata(metadata):
    return dict((k.lower(), decode_val(v)) for k, v in metadata.items())


def decode_val(string_val):
    """Format dates that elastic will try to convert automatically."""
    val = json.loads(string_val)
    try:
        arrow.get(val, 'YYYY-MM-DD')  # test if it will get matched by elastic
        return str(arrow.get(val))
    except (Exception):
        return val


def process_file(content, type):
    """
    Retrieves the media file metadata
    :param BytesIO content: content stream
    :param str type: type of media file
    :return: dict metadata related to media file.
    """
    if type == 'image':
        return process_image(content)
    if type in ('audio', 'video'):
        return process_video(content)
    return {}


def process_video(content):
    """
    Retrieves the video/audio metadata
    :param BytesIO content: content stream
    :return: dict video/audio metadata
    """
    content.seek(0)
    meta = get_meta(content)
    content.seek(0)
    return meta


def get_meta(content):
    pass


def process_image(content):
    """
    Retrieves the image metadata
    :param BytesIO content: content stream
    :return: dict image metadata
    """
    content.seek(0)
    meta = get_meta(content)
    content.seek(0)
    return meta
