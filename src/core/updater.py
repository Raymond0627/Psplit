"""Update checker and downloader for Folio."""

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Callable, Optional, Tuple

from src.version import __version__, GITHUB_REPO


def parse_version_tuple(ver_str: str) -> Tuple[int, ...]:
    """Convert version strings like 'v1.0.0' or '1.9.10' into comparable tuple of ints."""
    clean = re.sub(r'^[vV]', '', ver_str.strip())
    nums = []
    for part in clean.split('.'):
        digits = re.match(r'^\d+', part)
        if digits:
            nums.append(int(digits.group(0)))
        else:
            nums.append(0)
    return tuple(nums)


def is_newer_version(current: str, remote: str) -> bool:
    """Return True if remote version is strictly greater than current version."""
    return parse_version_tuple(remote) > parse_version_tuple(current)


def check_github_update(repo: str = GITHUB_REPO, current_ver: str = __version__) -> Optional[Tuple[str, str, str]]:
    """Check GitHub releases for a newer installer version.
    
    Returns:
        (version_tag, release_notes, download_url) if an update is available, else None.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Folio-Updater",
            "Accept": "application/vnd.github.v3+json",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                return None
            data = json.loads(response.read().decode("utf-8"))

        tag = data.get("tag_name", "")
        notes = data.get("body", "")
        assets = data.get("assets", [])

        # Find .exe asset (prefer Setup or installer .exe)
        download_url = ""
        for asset in assets:
            name = asset.get("name", "").lower()
            if name.endswith(".exe"):
                download_url = asset.get("browser_download_url", "")
                if "setup" in name or "installer" in name:
                    break

        if tag and is_newer_version(current_ver, tag) and download_url:
            return tag, notes, download_url
        return None
    except Exception:
        return None


class UpdateDownloader:
    """Downloads the installer executable with cancellation and progress reporting."""

    def __init__(self, download_url: str, version_tag: str):
        self.download_url = download_url
        self.version_tag = version_tag
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def download(
        self,
        progress_callback: Optional[Callable[[int, float, float], None]] = None,
        finished_callback: Optional[Callable[[str], None]] = None,
        failed_callback: Optional[Callable[[str], None]] = None,
    ):
        temp_dir = Path(tempfile.gettempdir())
        clean_tag = re.sub(r'^[vV]', '', self.version_tag)
        dest_path = temp_dir / f"Folio_Setup_{clean_tag}.exe"

        req = urllib.request.Request(
            self.download_url,
            headers={"User-Agent": "Folio-Updater"}
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as response, open(dest_path, "wb") as out_file:
                total_bytes = int(response.headers.get("Content-Length", 0))
                total_mb = total_bytes / (1024 * 1024) if total_bytes > 0 else 0.0

                downloaded_bytes = 0
                block_size = 65536

                while not self._cancelled:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded_bytes += len(chunk)
                    downloaded_mb = downloaded_bytes / (1024 * 1024)
                    percent = int((downloaded_bytes / total_bytes) * 100) if total_bytes > 0 else 0
                    if progress_callback:
                        progress_callback(percent, downloaded_mb, total_mb)

            if self._cancelled:
                try:
                    dest_path.unlink()
                except Exception:
                    pass
                return

            if finished_callback:
                finished_callback(str(dest_path))

        except Exception as e:
            if failed_callback:
                failed_callback(str(e))


def launch_installer_and_exit(installer_path: str):
    """Launch Inno Setup installer with flags and exit current application cleanly."""
    subprocess.Popen([
        installer_path,
        "/SILENT",
        "/CLOSEAPPLICATIONS",
        "/RESTARTAPPLICATIONS"
    ])
    sys.exit(0)
