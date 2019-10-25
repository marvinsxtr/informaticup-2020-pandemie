import os
import subprocess
from pandemie.tester import AbstractStrategy
from pandemie.web import start_server

if os.name == "nt":
    tool_cmd = "start ../../test/ic20_windows.exe"
else:
    #tool_cmd = "../.././ic20_linux"
    pass


class Tester:
    def __init__(self, strategy):
        if not isinstance(strategy, AbstractStrategy):
            raise ValueError("Strategy is not valid.")

        #os.system(tool_cmd)
        os.chdir("../../test/")
        subprocess.call("./ic20_linux", shell=True)
        start_server(strategy)


class ExampleStrategy(AbstractStrategy):
    def __init__(self):
        super().__init__()

    def solve(self, json_data):
        return '{"type": "endRound"}'


if __name__ == "__main__":
    my_tester = Tester(ExampleStrategy())
