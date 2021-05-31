import os
from pathlib import Path

def set_workspacerc(bucket, s3_access, s3_secret, s3_region, endpoint):

    home = str(Path.home())

    wsrc_file = os.path.join(home, '.workspacerc')

    if os.path.exists(wsrc_file):

        os.remove(wsrc_file)

    wsrc_content = f"""
WS_SERVICE_URL="{endpoint}"
WS_REGION="{s3_region}"
WS_ACCESS_KEY_ID="{s3_access}"
WS_SECRET_ACCESS_KEY="{s3_secret}"
WS_BUCKET="{bucket}"

PDE_SERVICE_URL="http://localhost:9000"
PDE_REGION="us-west-1"
PDE_ACCESS_KEY_ID="minioadmin"
PDE_SECRET_ACCESS_KEY="minioadmin"
"""

    with open(wsrc_file, "w") as wsrc:
        wsrc.write(wsrc_content)


