#!/usr/bin/env python3

import shlex
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def main():
    output = subprocess.check_output(
        ["apt-get", "-qq", "--print-uris", "--reinstall", "install", "autopoint"],
        text=True,
    )
    urls = [shlex.split(line)[0] for line in output.splitlines() if line.startswith("'")]
    archive = next((url for url in urls if "/ubuntu/pool/" in url), None)
    if not archive:
        raise RuntimeError("APT did not provide an Ubuntu package URL for autopoint")

    relative_path = archive.split("/ubuntu/", 1)[1]
    endpoints = [("direct archive", archive)]
    mirror_file = Path("/etc/apt/apt-mirrors.txt")
    if not mirror_file.is_file():
        print("Runner mirror list not found: %s" % mirror_file)
    else:
        for line in mirror_file.read_text().splitlines():
            fields = line.split()
            if not fields or fields[0].startswith("#"):
                continue
            mirror = urllib.parse.urlsplit(fields[0])
            if (
                mirror.scheme not in ("http", "https")
                or not mirror.hostname
                or mirror.username
                or mirror.password
                or mirror.query
                or mirror.fragment
            ):
                print("Skipping unsupported or credential-bearing mirror entry")
                continue
            endpoints.append(("runner mirror", fields[0].rstrip("/") + "/" + relative_path))

    for label, url in endpoints:
        print("%s URL: %s" % (label, url))
        for agent, headers in (
            ("Python default", {}),
            ("APT-like", {"User-Agent": "Debian APT-HTTP/1.3"}),
        ):
            request = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    print("%s %s: HTTP %s, server=%s" %
                          (label, agent, response.status, response.headers.get("Server", "unknown")))
            except urllib.error.HTTPError as error:
                with error:
                    print("%s %s: HTTP %s, server=%s" %
                          (label, agent, error.code, error.headers.get("Server", "unknown")))
            except urllib.error.URLError as error:
                print("%s %s: %s" % (label, agent, error.reason))


if __name__ == "__main__":
    main()
