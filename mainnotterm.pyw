import sys
import os
import uvicorn
from config import Config

sys.stdout = open(os.path.join(os.path.dirname(__file__), "stdout.log"), "a")
sys.stderr = open(os.path.join(os.path.dirname(__file__), "stderr.log"), "a")

if __name__ == "__main__":
    try:
        from main import _get_real_local_ip
        print(f"Remote control start: http://{_get_real_local_ip()}:{Config.PORT}")
    except Exception:
        pass
    uvicorn.run("main:app", host=Config.WS_SERVER, port=Config.PORT, reload=False, log_level="warning")