import os
from pandemie.deployment.deployment import deploy

os.chdir("./pandemie/deployment")
deploy()
