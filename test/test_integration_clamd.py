"""Integration tests against a real clamd service."""

from pathlib import Path
import os

import pytest

from pyvalve import PyvalveNetwork, PyvalveConnectionError


EICAR = (
    b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$"
    b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
)


def _require_integration_enabled() -> None:
    if os.getenv("PYVALVE_RUN_INTEGRATION") != "1":
        pytest.skip("Set PYVALVE_RUN_INTEGRATION=1 to run clamd integration tests")


async def _build_client() -> PyvalveNetwork:
    host = os.getenv("PYVALVE_CLAMD_HOST", "localhost")
    port = int(os.getenv("PYVALVE_CLAMD_PORT", "3310"))
    timeout = int(os.getenv("PYVALVE_CLAMD_TIMEOUT", "60"))
    client = await PyvalveNetwork(host=host, port=port, timeout=timeout)
    client.set_persistant_connection(False)
    try:
        await client.ping()
    except PyvalveConnectionError as exc:
        pytest.skip(f"clamd is not reachable at {host}:{port}: {exc}")
    return client


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clamd_basic_commands() -> None:
    _require_integration_enabled()
    client = await _build_client()

    pong = await client.ping()
    assert "PONG" in pong

    version = await client.version()
    assert version

    stats = await client.stats()
    assert stats


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clamd_scan_and_instream_detects_eicar(tmp_path: Path) -> None:
    _require_integration_enabled()
    client = await _build_client()

    infected_path = tmp_path / "eicar.com.txt"
    infected_path.write_bytes(EICAR)

    scan_result = await client.scan(str(infected_path))
    assert "FOUND" in scan_result

    with infected_path.open("rb") as fd:
        instream_result = await client.instream(fd)
    assert "FOUND" in instream_result
