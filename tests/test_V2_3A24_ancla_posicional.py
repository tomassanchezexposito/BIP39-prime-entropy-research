#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas de regresión para Generador V2.3-A24."""

from __future__ import annotations

import importlib.util
import json
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
MODULE_PATH = REPO_ROOT / "src" / "v2_3_anchor_24_words" / "Generador_V2_3A24_Ancla_Posicional_Bidireccional.py"
MAPPING_PATH = REPO_ROOT / "src" / "datos_2048.json"

spec = importlib.util.spec_from_file_location("gen_anchor_24", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("No se pudo cargar el módulo.")
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

raw = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
items = [
    m.Item(int(x["position"]), int(x["prime"]), str(x["word"]))
    for x in raw["items"]
]
m.validate_items(items)

# 1) Vector BIP-39 de entropía cero para 24 palabras.
indexes, cs = m.indexes_from_entropy(0)
words = [items[i].word for i in indexes]
assert words == ["abandon"] * 23 + ["art"]
assert cs == 0x66
assert m.phrase_is_valid(indexes)

# 2) Filtro estructural generalizado a 24 posiciones.
assert m.is_fixed_step_progression([1 + 2 * i for i in range(24)])
assert m.is_forbidden_linear_pattern([1 + 2 * i for i in range(24)])
assert m.is_ordered_with_arbitrary_gaps(list(range(1, 25)))

# 3) Exhaustivo: todos los 2048 índices pueden fijarse en slots 1..23.
rng = random.Random(987654321)
for slot in range(1, 24):
    for target in range(2048):
        entropy, idxs, checksum, attempts = m.entropy_with_forced_word(
            target, slot, randbits=rng.getrandbits
        )
        assert idxs[slot - 1] == target
        assert m.phrase_is_valid(idxs)
        assert attempts == 1

# 4) Exhaustivo: todos los 2048 índices pueden fijarse en slot 24.
rng24 = random.Random(1357911)
slot24_attempts = []
for target in range(2048):
    entropy, idxs, checksum, attempts = m.entropy_with_forced_word(
        target, 24, randbits=rng24.getrandbits
    )
    assert idxs[23] == target
    assert m.phrase_is_valid(idxs)
    slot24_attempts.append(attempts)

# 5) 2.400 levantamientos bidireccionales.
rng_lift = random.Random(20260907)
lift_tests = 0
for slot in range(1, 25):
    anchor_local = 86  # apple
    anchor_absolute = anchor_local + 2048 * (slot + 30)
    for _ in range(100):
        local_positions = [rng_lift.randint(1, 2048) for _ in range(24)]
        local_positions[slot - 1] = anchor_local
        absolute = m.lift_local_series_anchored(
            anchor_absolute, local_positions, slot
        )
        assert absolute[slot - 1] == anchor_absolute
        assert all(b > a for a, b in zip(absolute, absolute[1:]))
        assert [m.local_position(g) for g in absolute] == local_positions
        lift_tests += 1

# 6) Primos ordinales básicos.
prime_map = m.odd_primes_at_positions([1, 2, 3, 10, 100])
assert prime_map == {1: 3, 2: 5, 3: 7, 10: 31, 100: 547}

# 7) Integración build_candidate + SQLite temporal.
tmpdir = Path(tempfile.mkdtemp(prefix="v23a24_test_db_"))
m.app_data_dir = lambda: tmpdir

for slot, blocks in [(1, 10), (12, 35), (23, 50), (24, 60)]:
    anchor = 86 + 2048 * blocks
    candidate = m.build_candidate(anchor, slot, items)
    assert candidate["words"][slot - 1] == "apple"
    assert candidate["absolute_positions"][slot - 1] == anchor
    assert candidate["local_positions"][slot - 1] == 86
    assert len(candidate["words"]) == 24
    assert len(candidate["entropy_hex"]) == 64
    assert len(candidate["checksum_bits"]) == 8
    assert m.phrase_is_valid([p - 1 for p in candidate["local_positions"]])
    assert all(
        b > a
        for a, b in zip(
            candidate["absolute_positions"],
            candidate["absolute_positions"][1:],
        )
    )

# 8) Casos imposibles detectados.
try:
    m.build_candidate(1, 2, items)
except ValueError:
    pass
else:
    raise AssertionError("Debe rechazarse ancla absoluta 1 en slot 2.")

try:
    m.build_candidate(100, 24, items)
except ValueError:
    pass
else:
    raise AssertionError("Debe rechazarse slot 24 en primer bloque con filtro V2.3.")

print("OK — todas las pruebas superadas")
print(f"Mapeo validado: {len(items)} registros")
print("Restricciones palabra/slot exhaustivas: 49.152 casos")
print(f"Levantamientos bidireccionales aleatorios: {lift_tests}")
print(
    "Slot 24 — intentos de checksum (PRNG determinista de prueba): "
    f"media={sum(slot24_attempts)/len(slot24_attempts):.2f}, "
    f"max={max(slot24_attempts)}, min={min(slot24_attempts)}"
)
print("Integración slots 1, 12, 23 y 24 + SQLite temporal: OK")
