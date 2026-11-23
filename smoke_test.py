"""Smoke test: render every page x department, assert no exceptions; non-zero exit on failure."""

import sys

from streamlit.testing.v1 import AppTest

from frontend.sidebar import DEPARTMENTS, NAVIGATION_ITEMS

APP = sys.argv[1] if len(sys.argv) > 1 else "app.py"


def main():
    failures = 0

    for nav in NAVIGATION_ITEMS:
        for dept in DEPARTMENTS:
            at = AppTest.from_file(APP, default_timeout=120)
            at.run()
            at.sidebar.radio[0].set_value(nav)
            at.sidebar.selectbox[0].set_value(dept)
            at.run()

            if at.exception:
                failures += 1
                print("FAIL", nav, dept, at.exception[0].message[:160])

    print("failures:", failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
