import os

def test_pipe_errors():
    fd = 0
    # Store original state, and ensure non-blocking mode is enabled
    _original_is_blocking = os.get_blocking(fd)
    os.set_blocking(fd, False)

    os.set_blocking(fd, _original_is_blocking)
    os.close(fd)
