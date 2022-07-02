
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

to_upxify = []

for root, dirs, names in os.walk(os.path.dirname(__file__) + "/build"):
    to_upxify.extend(
        [
            os.path.join(root, n) for n in names
            if os.path.splitext(n)[-1] in [".dll", ".pyd"] and "exe." in root
        ]
    )

for i in range(0, len(to_upxify), 10):
    os.system("upx -9 " + " ".join(to_upxify[i:i+10]))
