import os

def test_pipe_errors():
    fd = 0
    os.close(fd)
