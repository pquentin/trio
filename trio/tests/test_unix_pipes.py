import pytest

from .._unix_pipes import FdStream


async def test_pipe_errors():
    with pytest.raises(ValueError):
        await FdStream(0).receive_some(0)
