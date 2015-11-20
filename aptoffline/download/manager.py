from tempfile import mkdtemp
from functools import partial

from ..util import is_cached
from aptoffline.packages import requests
from aptoffline.packages.requests.auth import (HTTPBasicAuth,
                                               HTTPDigestAuth)
from shutil import rmtree, copy
from logging import getLogger

import os
import sys

if sys.version_info.major == 2:
    from aptoffline.packages.concurrent.futures import (
        ThreadPoolExecutor, as_completed)
else:
    from concurrent.futures import (ThreadPoolExecutor, as_completed)


class UnsupportedAuthType(Exception):

    def __init__(self, auth):
        super(UnsupportedAuthType, self).__init__(
            self, ('Auth Type requested by server: {}'
                   ' is unsupported').format(auth))


class DownloadManager(object):

    def __init__(self, cache_dir=None, proxy=None, timeout=None):
        self._cache = cache_dir

        kwargs = {'stream': True}

        if timeout is not None:
            kwargs['timeout'] = timeout

        if proxy is not None:
            kwargs['proxies'] = {'http': proxy, 'https': proxy}

        self.tempdir = mkdtemp()
        self.req = partial(requests.get, **kwargs)
        self.log = getLogger('apt-offline')

    def _in_cache(self, item, validate=True):
        if not item.file.endswith('.deb') or not self._cache:
            return

        fpath = is_cached(self._cache, item, validate)
        if fpath:
            copy(fpath, self.tmpdir)
            return True

        return False

    def _download(self, item, validate=True):
        if self._in_cache(item, validate):
            return

        resp = None
        if hasattr(item, 'user') and hasattr(item, 'passwd'):
            # process with basic if not try digest auth
            url = item.url.replace(item.user + ':' + item.passwd + '@', '')
            resp = self.req(url, auth=HTTPBasicAuth(item.user,
                                                    item.passwd))
            if resp.status_code == 401:
                # Lets try Digest auth
                resp = self.req(url, auth=HTTPDigestAuth(item.user,
                                                         item.passwd))
                if resp.status_code == 401:
                    raise UnsupportedAuthType(
                        resp.headers['WWW-Authenticate'])
        else:
            resp = self.req(item.url)

        with open(os.path.join(self.tempdir, item.file), 'wb') as fd:
            for chunk in resp.iter_content(chunk_size=1024):
                fd.write(chunk)

    def start(self, items, validate, threads=1):
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_downloads = {executor.submit(self._download, item,
                                                validate): item for item in
                                items}

            for f in as_completed(future_downloads):
                pass

    def __del__(self):
        rmtree(self.tempdir)
