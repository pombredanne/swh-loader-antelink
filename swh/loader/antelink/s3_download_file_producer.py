# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import sys

from swh.loader.antelink.db import Db


def list_s3_files(db_url, limit=None):
    db = Db.connect(db_url)
    with db.transaction() as cur:
        for path in db.read_content_s3_not_in_sesi_nor_in_swh(limit=limit,
                                                              cur=cur):
            yield path[0]


if __name__ == '__main__':
    db_url = "%s" % sys.argv[1]
    if len(sys.argv) > 2:
        limit = int(sys.argv[2])
    else:
        limit = None

    from swh.scheduler.celery_backend.config import app
    from swh.loader.antelink import tasks  # noqa

    for path in list_s3_files(db_url, limit):
        app.tasks['swh.loader.antelink.tasks.AntelinkS3DownloaderTsk'].delay(
            path)
