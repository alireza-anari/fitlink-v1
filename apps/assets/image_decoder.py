"""Standalone Linux decoder. Sandbox is installed before reading untrusted input."""

import ctypes
import errno
import json
import os
import platform
import resource
import socket
import sys
import warnings
from io import BytesIO

from PIL import (
    Image,
    ImageFile,
    ImageMath,
    ImageOps,
    JpegImagePlugin,
    PngImagePlugin,
    TiffImagePlugin,
)

# JPEG's EXIF DPI probe lazily imports TIFF metadata and pixel helpers. Preload
# dependencies before closing file access, then retain only permitted parsers.
# No TIFF image can enter decode(): its format allowlist is always explicit.
assert JpegImagePlugin and PngImagePlugin and TiffImagePlugin and ImageOps and ImageMath
Image.preinit()
Image.OPEN = {name: Image.OPEN[name] for name in ("JPEG", "PNG")}
ImageFile.LOAD_TRUNCATED_IMAGES = False
Image.MAX_IMAGE_PIXELS = 20_000_000
warnings.simplefilter("error")


class Filter(ctypes.Structure):
    _fields_ = [
        ("code", ctypes.c_ushort),
        ("jt", ctypes.c_ubyte),
        ("jf", ctypes.c_ubyte),
        ("k", ctypes.c_uint),
    ]


class Program(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ushort), ("filters", ctypes.POINTER(Filter))]


def isolate():
    # Only audited Linux amd64 is supported; unsupported kernels/architectures
    # fail closed. No credential or privileged descriptor is inherited.
    if sys.platform != "linux" or platform.machine() != "x86_64":
        raise RuntimeError("Isolation unavailable")
    libc = ctypes.CDLL(None, use_errno=True)
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    if os.getuid() == 0:
        os.setgroups([])
        os.setgid(65534)
        os.setuid(65534)
    if os.getuid() == 0 or os.geteuid() == 0:
        raise RuntimeError("Isolation unavailable")
    os.environ.clear()
    # Strict syscall allowlist: no file open, network, exec, process/thread
    # creation, privilege changes, filesystem mutation, ptrace or io_uring.
    safe = (
        0,
        1,
        3,
        5,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        24,
        25,
        28,
        39,
        60,
        96,
        102,
        104,
        107,
        108,
        158,
        186,
        202,
        218,
        228,
        231,
        234,
        273,
        302,
        318,
        334,
    )
    rules = [
        Filter(0x20, 0, 0, 4),
        Filter(0x15, 1, 0, 0xC000003E),
        Filter(0x06, 0, 0, 0x80000000),
        Filter(0x20, 0, 0, 0),
    ]
    for number in safe:
        rules += [Filter(0x15, 0, 1, number), Filter(0x06, 0, 0, 0x7FFF0000)]
    rules += [Filter(0x06, 0, 0, 0x00050000 | errno.EPERM)]
    array = (Filter * len(rules))(*rules)
    program = Program(len(rules), array)
    if libc.prctl(38, 1, 0, 0, 0) or libc.prctl(22, 2, ctypes.byref(program), 0, 0):
        raise RuntimeError("Isolation unavailable")


def probe():
    results = {"nonroot": os.getuid() != 0 and os.geteuid() != 0}
    for name, operation in (
        ("network_denied", lambda: socket.socket()),
        (
            "write_denied",
            lambda: os.open(
                "/tmp/c03-isolation-probe", os.O_WRONLY | os.O_CREAT, 0o600
            ),
        ),
        ("fork_denied", os.fork),
    ):
        try:
            operation()
            results[name] = False
        except PermissionError:
            results[name] = True
    return results


def decode(data, mime, edge):
    fmt = {"image/png": "PNG", "image/jpeg": "JPEG"}[mime]
    with Image.open(BytesIO(data), formats=[fmt]) as image:
        if image.format != fmt or getattr(image, "n_frames", 1) != 1:
            raise ValueError("Invalid raster")
        w, h = image.size
        if not 1 <= w <= 10000 or not 1 <= h <= 10000 or w * h > 20_000_000:
            raise ValueError("Invalid raster")
        image.verify()
    with Image.open(BytesIO(data), formats=[fmt]) as image:
        image.load()
        # Rebuild pixels into a fresh object: conversion/copy alone carries info.
        mode = (
            "RGBA" if "A" in image.getbands() or "transparency" in image.info else "RGB"
        )
        pixels = image.convert(mode)
        clean = Image.frombytes(mode, pixels.size, pixels.tobytes())
        clean.thumbnail((edge, edge), Image.Resampling.LANCZOS)
        output = BytesIO()
        clean.save(output, format="PNG", compress_level=9)
        result = output.getvalue()
        if len(result) > 10_000_000:
            raise ValueError("Output limit")
        return {"status": "clean", "width": clean.width, "height": clean.height}, result


def main():
    try:
        isolate()
    except Exception:
        return 2
    try:
        if sys.argv[1] == "probe":
            header, output = probe(), b""
        else:
            data = sys.stdin.buffer.read(10_000_001)
            if not data or len(data) > 10_000_000:
                raise ValueError("Input limit")
            header, output = decode(data, sys.argv[1], int(sys.argv[2]))
    except Exception:
        header, output = {"status": "invalid"}, b""
    os.write(1, json.dumps(header).encode() + b"\n")
    # Blocking pipe writes may be partial.
    for offset in range(0, len(output), 65536):
        chunk = memoryview(output)[offset : offset + 65536]
        while chunk:
            chunk = chunk[os.write(1, chunk) :]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
