# PyInstaller hook: passlib loads hash handlers via dynamic imports.
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("passlib.handlers")
