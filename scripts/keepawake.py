"""Keep VibeSync awake on Streamlit Community Cloud.

Apps there go to sleep after ~12 hours without a visitor, and a plain web request doesn't count as one: the app
only wakes for a real browser. So every few hours this opens the site in headless Chromium like a visitor would,
and if it's asleep, presses "Yes, get this app back up!" and waits for it to start.
"""
import re
import sys

from playwright.sync_api import sync_playwright

URL = "https://vibesync-saianish.streamlit.app/"
WAKE = re.compile(r"get this app back up", re.I)


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(10_000)
        button = page.get_by_role("button", name=WAKE)
        if button.count():
            print("::notice title=keep awake::VibeSync was asleep: waking it up")
            button.first.click()
            page.wait_for_timeout(120_000)                     # let it boot, like a visitor waiting
            asleep = page.get_by_role("button", name=WAKE).count() > 0
            browser.close()
            if asleep:
                print("::error title=keep awake::still asleep after pressing wake")
                return 1
            print("::notice title=keep awake::awake again")
            return 0
        page.wait_for_timeout(45_000)                         # an awake visit: stay a little, so it counts as traffic
        print("::notice title=keep awake::VibeSync is awake")
        browser.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
