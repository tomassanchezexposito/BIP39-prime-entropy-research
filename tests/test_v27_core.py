"""Deterministic core tests for the V2.7 research generator.

These tests intentionally exercise pure transformations only. They do not
generate or search for wallet credentials.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "src" / "Generador_V2_7_AUTO_Turbo_Cronometros.py"


def load_v27_module():
    """Load the historical V2.7 module without starting its Tkinter GUI.

    The module is inserted into ``sys.modules`` before execution because
    Python's ``dataclasses`` implementation may resolve postponed string
    annotations through the defining module namespace during import.
    """
    module_name = "v27_generator"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {MODULE_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    return module


@pytest.fixture(scope="module")
def v27():
    """Return the imported V2.7 module for deterministic tests."""
    return load_v27_module()


@pytest.mark.parametrize(
    ("absolute_position", "expected"),
    [
        (1, 1),
        (2048, 2048),
        (2049, 1),
        (4096, 2048),
        (4097, 1),
    ],
)
def test_local_position_wraps_every_2048(v27, absolute_position: int, expected: int) -> None:
    assert v27.local_position(absolute_position) == expected


@pytest.mark.parametrize("absolute_position", [0, -1, -100])
def test_local_position_rejects_non_positive_values(v27, absolute_position: int) -> None:
    with pytest.raises(ValueError):
        v27.local_position(absolute_position)


@pytest.mark.parametrize(
    ("absolute_position", "expected"),
    [
        (1, 0),
        (2048, 0),
        (2049, 1),
        (4096, 1),
        (4097, 2),
    ],
)
def test_block_number_is_zero_based(v27, absolute_position: int, expected: int) -> None:
    assert v27.block_number(absolute_position) == expected


def test_zero_entropy_bip39_indexes_and_checksum(v27) -> None:
    """128 zero entropy bits yield checksum 0011 and final BIP-39 index 3."""
    indexes, checksum = v27.indexes_from_entropy(0)

    assert len(indexes) == 12
    assert indexes == ([0] * 11) + [3]
    assert checksum == 0b0011
