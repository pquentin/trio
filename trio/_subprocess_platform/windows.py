import sys
from .. import _subprocess
from .._wait_for_object import WaitForSingleObject

assert sys.platform == "win32"


async def wait_child_exiting(process: "_subprocess.Process") -> None:
    await WaitForSingleObject(int(process._proc._handle))
