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
wipe_screen.py
"""
import threading
import traceback
from functools import partial
from kivy.clock import Clock
from src.utils.flasher.wiper import Wiper
from src.app.screens.base_flash_screen import BaseFlashScreen


class WipeScreen(BaseFlashScreen):
    """Flash screen is where flash occurs"""

    def __init__(self, **kwargs):
        super().__init__(wid="wipe_screen", name="WipeScreen", **kwargs)
        self.please_msg = self.translate("PLEASE DO NOT UNPLUG YOUR DEVICE")
        self.wiper = None
        self.success = False
        self.progress = ""
        self.device = None
        self.fail_msg = ""
        fn = partial(self.update, name=self.name, key="canvas")
        Clock.schedule_once(fn, 0)

    def build_on_data(self):
        """
        Build a streaming IO static method using
        some instance variables for flash procedure
        when KTool.print_callback is called

        (useful for to be used in tests)
        """

        # pylint: disable=unused-argument
        def on_data(*args, **kwargs):
            text = " ".join(str(x) for x in args)
            self.info(text)
            text = WipeScreen.parse_general_output(text)
            text = text.replace(
                "[INFO] Erasing the whole SPI Flash",
                "".join(
                    [
                        "[color=#00ff00]INFO[/color]",
                        "[color=#efcc00] Erasing the whole SPI Flash [/color]",
                    ]
                ),
            )
            text = text.replace(
                "\x1b[31m\x1b[1m[ERROR]\x1b[0m", "[color=#ff0000]ERROR[/color]"
            )
            self.output.append(text)

            if len(self.output) > 10:
                del self.output[:1]

            if "Greeting fail" in text:
                self.fail_msg = text
                self.wiper.ktool.kill()
                self.wiper.ktool.checkKillExit()

            if "SPI Flash erased." in text:
                self.is_done = True
                # pylint: disable=not-callable
                self.done()

            self.ids[f"{self.id}_info"].text = "\n".join(self.output)

        setattr(WipeScreen, "on_data", on_data)

    # pylint: disable=unused-argument
    def on_pre_enter(self, *args):
        """When pre-enter the screen, clear widgets and build texts"""
        self.ids[f"{self.id}_grid"].clear_widgets()
        self.build_on_data()
        self.build_on_done()

        wid = f"{self.id}_info"

        def on_ref_press(*args):
            if args[1] == "Back":
                self.set_screen(name="MainScreen", direction="right")

            if args[1] == "Quit":
                self.quit_app()

        setattr(WipeScreen, f"on_ref_press_{wid}", on_ref_press)

        self.make_subgrid(
            wid=f"{self.id}_subgrid", rows=3, root_widget=f"{self.id}_grid"
        )

        self.make_image(
            wid=f"{self.id}_loader",
            source=self.load_img,
            root_widget=f"{self.id}_subgrid",
        )

        self.make_button(
            row=1,
            wid=f"{self.id}_progress",
            text="".join(
                [
                    f"[b]{self.please_msg}[/b]",
                ]
            ),
            halign="center",
            font_factor=32,
            root_widget=f"{self.id}_subgrid",
            on_press=None,
            on_release=None,
            on_ref_press=on_ref_press,
        )

        self.make_button(
            row=2,
            wid=f"{self.id}_info",
            text="",
            font_factor=72,
            root_widget=f"{self.id}_grid",
            halign="justify",
            on_press=None,
            on_release=None,
            on_ref_press=on_ref_press,
        )

    # pylint: disable=unused-argument
    def on_enter(self, *args):
        """
        Event fired when the screen is displayed and the entering animation is complete.
        """
        self.done = getattr(WipeScreen, "on_done")
        self.wiper.ktool.__class__.print_callback = getattr(WipeScreen, "on_data")
        on_process = partial(self.wiper.wipe, device=self.device)
        self.thread = threading.Thread(name=self.name, target=on_process)

        # if anything wrong happen, show it
        def hook(err):
            if not self.is_done:
                trace = traceback.format_exception(
                    err.exc_type, err.exc_value, err.exc_traceback
                )
                msg = "".join(trace[-2:])
                general_msg = "".join(
                    [
                        "Ensure that you have selected the correct device ",
                        "and that your computer has successfully detected it.",
                    ]
                )

                self.error(msg)
                if "StopIteration" in msg:
                    self.fail_msg = msg
                    self.fail_msg += f"\n\n{general_msg}"
                    not_conn_fail = RuntimeError(f"Wipe failed:\n{self.fail_msg}\n")
                    self.redirect_exception(exception=not_conn_fail)

                elif "Cancel" in msg:
                    self.fail_msg = f"{self.fail_msg}\n\n{general_msg}"
                    greeting_fail = RuntimeError(f"Wipe failed:\n{self.fail_msg}\n")
                    self.redirect_exception(exception=greeting_fail)

                else:
                    self.fail_msg = msg
                    any_fail = RuntimeError(f"Wipe failed:\n{self.fail_msg}\n")
                    self.redirect_exception(exception=any_fail)

        setattr(WipeScreen, "on_except_hook", hook)

        # hook what happened
        threading.excepthook = getattr(WipeScreen, "on_except_hook")
        self.thread.start()

    def update(self, *args, **kwargs):
        """Update screen with firmware key. Should be called before `on_enter`"""
        name = str(kwargs.get("name"))
        key = str(kwargs.get("key"))
        value = kwargs.get("value")

        def on_update():
            if key == "locale":
                self.please_msg = self.translate("PLEASE DO NOT UNPLUG YOUR DEVICE")

            if key == "device":
                setattr(self, "device", value)

            if key == "wiper":
                setattr(self, "wiper", Wiper())
                setattr(getattr(self, "wiper"), "baudrate", value)

        setattr(WipeScreen, "on_update", on_update)
        self.update_screen(
            name=name,
            key=key,
            value=value,
            allowed_screens=(
                "ConfigKruxInstaller",
                "MainScreen",
                "WarningWipeScreen",
                "WipeScreen",
            ),
            on_update=getattr(WipeScreen, "on_update"),
        )
