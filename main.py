import os
import proxy_manager.models as pm_models
import time


os.system(
    "gnome-terminal -- " + f"bash -c 'python3 manage.py proxy_fetch_cycle;' exec bash"
)
os.system(
    "gnome-terminal -- "
    + f"bash -c 'python3 manage.py proxy_validate_cycle;' exec bash"
)
os.system("python3 manage.py start_website_update 'webnovelpub' 5;")
