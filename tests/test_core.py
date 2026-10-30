import socket
import threading

import pytest

from portfree import find, is_free, wait_open


def _listen(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port))
    s.listen(1)
    return s


def test_is_free_on_occupied_port():
    s = _listen(0)
    port = s.getsockname()[1]
    try:
        assert is_free(port) is False
    finally:
        s.close()


def test_find_skips_occupied():
    s = _listen(0)
    base = s.getsockname()[1]
    try:
        got = find(base)
        assert got != base
        assert got > base
        assert is_free(got)
    finally:
        s.close()


def test_find_rejects_out_of_range():
    with pytest.raises(ValueError):
        find(70000)


def test_wait_open_times_out():
    with pytest.raises(TimeoutError):
        wait_open(1, timeout=0.3)


def test_wait_open_succeeds():
    # 先占一个端口把号拿到手，再放开，避免和别的测试撞
    s = _listen(0)
    port = s.getsockname()[1]
    s.close()

    holder = {}

    def later():
        import time
        time.sleep(0.3)
        # 必须把 socket 存进 holder。直接 return 的话没有引用，CPython 会
        # 立刻 GC 掉它 -> 端口上没有任何监听者 -> wait_open 必然超时。
        holder["s"] = _listen(port)

    t = threading.Thread(target=later, daemon=True)
    t.start()
    try:
        waited = wait_open(port, timeout=5)
        assert waited >= 0
    finally:
        held = holder.get("s")
        if held is not None:
            held.close()
