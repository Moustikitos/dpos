
import os
import sys
from cx_Freeze import setup, Executable

sys.argv.append("build_exe")


setup(
    name="Ark lite wallet",
    version="1",
    description="Easy way to interact with ark blockchain and its forks",
    executables=[Executable("dposlib/cmd/send.py", base="console")],
    options={
        "build_exe": {
            "optimize": 2,
            "zip_include_packages": [
                "encodings", "usrv", "base58", "collections",
                "concurrent", "ctypes", "email", "future", "html", "http",
                "json", "logging", "urllib", "xml", "importlib", "certifi",
                "ecpy", "google", "charset_normalizer", "idna", "requests",
                "websocket", "u2flib_host", "ledgerblue", "urllib3"
            ],
            "excludes": ["test", "unittest", "pydoc_data"],
            "packages": [
                "dposlib.ark.cold", "ledgerblue", "urllib3", "queue"
            ]
        }
    }
)

os.system("upx -9 build/exe.win-amd64-3.10/*.dll")
os.system("upx -9 build/exe.win-amd64-3.10/lib/*.dll")
os.system("upx -9 build/exe.win-amd64-3.10/lib/*.pyd")
os.system("upx -9 build/exe.win-amd64-3.10/lib/cSecp256k1/*.dll")
