# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


import logging
import os
import subprocess

from swh.core import config
from swh.storage import get_storage

from swh.loader.antelink import utils

DRY_RUN = True


def download_s3_file(s3path, path):
    """Download the s3path file to path."""
    cmd = ['aws', 's3', 'cp', s3path, path]
    subprocess.check_output(cmd, universal_newlines=True)


class AntelinkS3Downloader(config.SWHConfig):
    """A bulk loader for downloading some file from s3.

    """
    DEFAULT_CONFIG = {
        'storage_class': ('str', 'remote_storage'),
        'storage_args': ('list[str]', ['http://localhost:5000/']),
        'db_url': ('string', 'service=antelink-swh'),
        'bucket': ('string', 's3://antelink-object-storage'),
        'destination_path': ('string', '/home/storage/antelink/s3/')
    }

    def __init__(self, config):
        self.config = config

        dest_path = self.config['destination_path']
        if not dest_path.endswith('/'):
            self.config['destination_path'] = dest_path + '/'

        s3path = self.config['bucket']
        if not s3path.endswith('/'):
            self.config['bucket'] = s3path + '/'

        self.storage = get_storage(config['storage_class'],
                                   config['storage_args'])

        self.log = logging.getLogger(
            'swh.antelink.loader.AntelinkS3Downloader')

    def process(self, dirpath):
        full_dest_path = self.config['destination_path'] + dirpath
        s3path = self.config['bucket'] + dirpath

        if DRY_RUN:
            print('%s -> %s downloaded (dry run)!' % (s3path, full_dest_path))
            return

        if not os.path.exists(full_dest_path):
            parent_path = os.path.dirname(full_dest_path)
            os.makedirs(parent_path, exist_ok=True)

            download_s3_file(s3path, full_dest_path)

        # todo, inject in swh
        hashdata = utils.compute_hash(full_dest_path)

        try:
            self.storage.content_add([hashdata])
        except Exception as e:
            print(e)
        finally:
            if os.path.exists(full_dest_path):
                os.delete(full_dest_path)
