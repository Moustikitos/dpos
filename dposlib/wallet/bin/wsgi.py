import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app

if __name__ == "__main__":
	app.app.run()
