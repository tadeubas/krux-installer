# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
download_stable_zip_sha256_screen.py
"""
import time
from threading import Thread
from functools import partial
from kivy.app import App
from kivy.clock import Clock
from src.app.screens.base_screen import BaseScreen
from src.app.screens.base_download_screen import BaseDownloadScreen
from src.utils.downloader.sha256_downloader import Sha256Downloader


class DownloadStableZipSha256Screen(BaseDownloadScreen):
    """DownloadStableZipSha256Screen download the sha256sum file for official krux zip release"""

    def __init__(self, **kwargs):
        super().__init__(
            wid="download_stable_zip_sha256_screen",
            name="DownloadStableZipSha256Screen",
            **kwargs,
        )
        self.to_screen = "DownloadStableZipSigScreen"

    def update(self, *args, **kwargs):
        """Update screen with version key"""
        if kwargs.get("key") == "version":
            self.version = kwargs.get("value")
            self.downloader = Sha256Downloader(
                version=kwargs.get("value"),
                destdir=App.get_running_app().config.get("destdir", "assets"),
            )

            def on_progress(data: bytes):
                len1 = self.downloader.downloaded_len
                len2 = self.downloader.content_len
                p = len1 / len2
                self.ids[f"{self.id}_label_progress"].text = "\n".join(
                    [
                        f"[size=100sp][b]{p * 100.00:.2f}%[/b][/size]",
                        f"[size=16sp]{len1} of {len2} B[/size]",
                    ]
                )

                # When finish, change the label, wait some seconds
                # and then change screen
                if p == 1.00:
                    self.ids[f"{self.id}_label_info"].text = "\n".join(
                        [
                            f"{self.downloader.destdir}/krux-{self.version}.zip.sha256.txt downloaded",
                        ]
                    )
                    time.sleep(2.1)  # 2.1 remember 21000000
                    self.trigger()

            self.downloader.on_write_to_buffer = on_progress

            self.ids[f"{self.id}_label_info"].text = "\n".join(
                [
                    "Downloading",
                    f"[color=#00AABB][ref={self.downloader.url}]{self.downloader.url}[/ref][/color]",
                    ""
                    f"to {self.downloader.destdir}/krux-{self.version}.zip.sha256.txt",
                ]
            )
