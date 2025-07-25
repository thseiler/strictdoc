import os
import platform
import sys


class SDocRuntimeEnvironment:
    def __init__(self, path_to_init: str) -> None:
        assert isinstance(path_to_init, str), path_to_init

        # FIXME: Delete me.
        self.path_to_init = path_to_init
        # https://stackoverflow.com/a/55556360/598057
        self.is_nuitka = "__compiled__" in globals()
        self.is_py_installer = (
            getattr(sys, "frozen", False) and not self.is_nuitka
        )

        # "frozen" attribute is set to True by PyInstaller, and it looks like
        # Nuitka does the same.
        self.is_binary_dist: bool = (
            getattr(sys, "frozen", False) or self.is_nuitka
        )

        if self.is_binary_dist:  # pragma: no cover
            # When it is a binary distribution, we don't have a Python package
            # file structure but only a binary with surrounding libraries and
            # data files (Jinja HTML files, CSS, JS, ...).
            path_to_main = os.path.abspath(sys.argv[0])
            path_to_main_dir = os.path.dirname(os.path.abspath(path_to_main))

            # Nuitka.
            if self.is_nuitka:
                self.path_to_strictdoc = path_to_main_dir
            # PyInstaller
            else:
                self.path_to_strictdoc = (
                    sys._MEIPASS  # type: ignore[attr-defined]
                )
        else:
            self.path_to_strictdoc = os.path.abspath(
                os.path.join(path_to_init, "..", "..")
            )
        assert os.path.isdir(self.path_to_strictdoc), self.path_to_strictdoc
        assert os.path.isabs(self.path_to_strictdoc), (
            "Path to strictdoc's package path must be an absolute path: "
            f"{self.path_to_strictdoc}"
        )

        self.is_debug_mode: bool = False

    def is_windows(self) -> bool:
        return platform.system() == "Windows"

    def is_github_ci_windows(self) -> bool:
        return self.is_windows() and os.environ.get("GITHUB_ACTIONS") == "true"

    def get_static_files_path(self) -> str:
        if self.is_binary_dist:  # pragma: no cover
            return os.path.join(self.path_to_strictdoc, "_static")
        return os.path.join(
            self.path_to_strictdoc, "strictdoc/export/html/_static"
        )

    def get_extra_static_files_path(self) -> str:
        if self.is_binary_dist:  # pragma: no cover
            return os.path.join(self.path_to_strictdoc, "_static_extra")
        return os.path.join(
            self.path_to_strictdoc, "strictdoc/export/html/_static_extra"
        )

    def get_path_to_rst_templates(self) -> str:
        if self.is_py_installer:  # pragma: no cover
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            bundle_dir = (
                sys._MEIPASS  # type: ignore[attr-defined]
            )
            return os.path.join(bundle_dir, "templates/rst")
        if self.is_nuitka:  # pragma: no cover
            return os.path.join(self.path_to_strictdoc, "templates/rst")
        # Normal Python
        return os.path.join(
            self.path_to_strictdoc, "strictdoc", "export", "rst", "templates"
        )

    def get_path_to_html_templates(self) -> str:
        if self.is_py_installer:  # pragma: no cover
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            bundle_dir = (
                sys._MEIPASS  # type: ignore[attr-defined]
            )
            return os.path.join(bundle_dir, "templates/html")
        if self.is_nuitka:  # pragma: no cover
            return os.path.join(self.path_to_strictdoc, "templates/html")
        # Normal Python.
        path_to_html_templates = os.path.join(
            self.path_to_strictdoc, "strictdoc", "export", "html", "templates"
        )
        assert os.path.isdir(path_to_html_templates), path_to_html_templates
        assert os.path.isabs(path_to_html_templates), path_to_html_templates
        return path_to_html_templates
