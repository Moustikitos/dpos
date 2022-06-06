import sys
from cx_Freeze import setup, Executable

sys.argv.append("build_exe")


setup(
    name="Ark lite wallet",
    version="1",
    description="Easy way to interact with ark blockchain and its forks",
    executables=[Executable("dposlib/cmd/send.py")],
    options={
        "build_exe": {
            "zip_include_packages": [
                "encodings", "usrv", "base58", "collections",
                "concurrent", "ctypes", "email", "future", "html", "http",
                "json", "logging", "urllib", "xml", "importlib"
            ],
            "excludes": ["test", "unittest", "pydoc_data"],
            "packages": ["dposlib.ark.cold"]
        }
    }
)
