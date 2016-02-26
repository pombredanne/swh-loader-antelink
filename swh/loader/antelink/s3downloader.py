# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


import logging
import os
import boto3

from swh.core import config


def download_file(bucket, s3path, path):
    """Download the s3path file to path."""
    bucket.download_file(s3path, path)


class AntelinkS3Downloader(config.SWHConfig):
    """A bulk loader for downloading some file from s3.

    """
    DEFAULT_CONFIG = {
        'bucket': ('string', 'antelink-object-storage'),
        'destination_path': ('string', '/home/storage/antelink/s3/'),
    }

    def __init__(self, config):
        self.config = config

        dest_path = self.config['destination_path']
        if not dest_path.endswith('/'):
            self.config['destination_path'] = dest_path + '/'

        s3path = self.config['bucket']
        if s3path.endswith('/'):
            self.config['bucket'] = s3path.rstrip('/')

        self.log = logging.getLogger(
            'swh.antelink.loader.AntelinkS3Downloader')

    def process(self, paths):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.config['bucket'])

        for s3path in paths:
            # expects no prefix / in s3path
            localpath = self.config['destination_path'] + s3path

            try:
                if os.path.exists(localpath):
                    self.log.warn('%s exists! Skipping.' % localpath)
                    continue
                else:
                    self.log.info('%s -> %s' % (s3path, localpath))
                    os.makedirs(os.path.dirname(localpath), exist_ok=True)
                    bucket.download_file(s3path, localpath)

            except Exception as e:
                self.log.error('Problem during retrieval of %s: %s' %
                               (localpath, e))
