import pytest

from .._unix_pipes import FdStream


async def test_pipe_errors():
    fd = FdStream(0)
    fd._fd_holder._raw_close()
