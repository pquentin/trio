import errno
import select
import os

import pytest

from .._core.tests.tutil import gc_collect_harder
from .. import _core, move_on_after
from ..testing import wait_all_tasks_blocked, check_one_way_stream

posix = os.name == "posix"
pytestmark = pytest.mark.skipif(not posix, reason="posix only")
if posix:
    from .._unix_pipes import FdStream
else:
    with pytest.raises(ImportError):
        from .._unix_pipes import FdStream


# Have to use quoted types so import doesn't crash on windows
async def make_pipe() -> "Tuple[FdStream, FdStream]":
    """Makes a new pair of pipes."""
    (r, w) = os.pipe()
    return FdStream(w), FdStream(r)


async def make_clogged_pipe():
    s, r = await make_pipe()
    try:
        while True:
            # We want to totally fill up the pipe buffer.
            # This requires working around a weird feature that POSIX pipes
            # have.
            # If you do a write of <= PIPE_BUF bytes, then it's guaranteed
            # to either complete entirely, or not at all. So if we tried to
            # write PIPE_BUF bytes, and the buffer's free space is only
            # PIPE_BUF/2, then the write will raise BlockingIOError... even
            # though a smaller write could still succeed! To avoid this,
            # make sure to write >PIPE_BUF bytes each time, which disables
            # the special behavior.
            # For details, search for PIPE_BUF here:
            #   http://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html

            # for the getattr:
            # https://bitbucket.org/pypy/pypy/issues/2876/selectpipe_buf-is-missing-on-pypy3
            buf_size = getattr(select, "PIPE_BUF", 8192)
            os.write(s.fileno(), b"x" * buf_size * 2)
    except BlockingIOError:
        pass
    return s, r


async def test_send_pipe():
    r, w = os.pipe()
    async with FdStream(w) as send:
        assert send.fileno() == w
        await send.send_all(b"123")
        assert (os.read(r, 8)) == b"123"

        os.close(r)


async def test_receive_pipe():
    r, w = os.pipe()
    async with FdStream(r) as recv:
        assert (recv.fileno()) == r
        os.write(w, b"123")
        assert (await recv.receive_some(8)) == b"123"

        os.close(w)


async def test_pipes_combined():
    write, read = await make_pipe()
    count = 2**20

    async def sender():
        big = bytearray(count)
        await write.send_all(big)

    async def reader():
        await wait_all_tasks_blocked()
        received = 0
        while received < count:
            received += len(await read.receive_some(4096))

        assert received == count

    async with _core.open_nursery() as n:
        n.start_soon(sender)
        n.start_soon(reader)

    await read.aclose()
    await write.aclose()


async def test_pipe_errors():
    with pytest.raises(TypeError):
        FdStream(None)

    with pytest.raises(ValueError):
        await FdStream(0).receive_some(0)


async def test_del():
    w, r = await make_pipe()
    f1, f2 = w.fileno(), r.fileno()
    del w, r
    gc_collect_harder()

    with pytest.raises(OSError) as excinfo:
        os.close(f1)
    assert excinfo.value.errno == errno.EBADF

    with pytest.raises(OSError) as excinfo:
        os.close(f2)
    assert excinfo.value.errno == errno.EBADF
