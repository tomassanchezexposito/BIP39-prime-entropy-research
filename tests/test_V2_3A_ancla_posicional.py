#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas de regresión para Generador V2.3-A."""

from __future__ import annotations

import importlib.util
import json
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
MODULE_PATH = REPO_ROOT / "src" / "v2_3_anchor_12_words" / "Generador_V2_3A_Ancla_Posicional_Bidireccional.py"
MAPPING_PATH = REPO_ROOT / "src" / "datos_2048.json"

spec = importlib.util.spec_from_file_location("gen_anchor", MODULE_PATH)
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

# 1) Vector BIP-39 de entropía cero.
indexes, cs = m.indexes_from_entropy(0)
words = [items[i].word for i in indexes]
assert words == ["abandon"] * 11 + ["about"]
assert m.phrase_is_valid(indexes)

# 2) Exhaustivo: todos los 2048 índices pueden fijarse en slots 1..11.
rng = random.Random(987654321)
for slot in range(1, 12):
    for target in range(2048):
        entropy, idxs, checksum, attempts = m.entropy_with_forced_word(
            target, slot, randbits=rng.getrandbits
        )
        assert idxs[slot - 1] == target
        assert m.phrase_is_valid(idxs)
        assert attempts == 1

# 3) Exhaustivo: todos los 2048 índices pueden fijarse en slot 12.
#    Se usa PRNG determinista SOLO para pruebas; producción usa secrets.
rng12 = random.Random(1357911)
slot12_attempts = []
for target in range(2048):
    entropy, idxs, checksum, attempts = m.entropy_with_forced_word(
        target, 12, randbits=rng12.getrandbits
    )
    assert idxs[11] == target
    assert m.phrase_is_valid(idxs)
    slot12_attempts.append(attempts)

# 4) 2.400 pruebas de levantamiento bidireccional.
rng_lift = random.Random(20260907)
lift_tests = 0
for slot in range(1, 13):
    anchor_local = 86  # apple
    anchor_absolute = anchor_local + 2048 * (slot + 20)
    for _ in range(200):
        local_positions = [rng_lift.randint(1, 2048) for _ in range(12)]
        local_positions[slot - 1] = anchor_local
        absolute = m.lift_local_series_anchored(
            anchor_absolute, local_positions, slot
        )
        assert absolute[slot - 1] == anchor_absolute
        assert all(b > a for a, b in zip(absolute, absolute[1:]))
        assert [m.local_position(g) for g in absolute] == local_positions
        lift_tests += 1

# 5) Primos ordinales básicos.
prime_map = m.odd_primes_at_positions([1, 2, 3, 10, 100])
assert prime_map == {1: 3, 2: 5, 3: 7, 10: 31, 100: 547}

# 6) Integración build_candidate + SQLite temporal.
tmpdir = Path(tempfile.mkdtemp(prefix="v23a_test_db_"))
m.app_data_dir = lambda: tmpdir

anchor6 = 86 + 2048 * 24
c6 = m.build_candidate(anchor6, 6, items)
assert c6["words"][5] == "apple"
assert c6["absolute_positions"][5] == anchor6
assert c6["local_positions"][5] == 86
assert m.phrase_is_valid([p - 1 for p in c6["local_positions"]])
assert all(b > a for a, b in zip(c6["absolute_positions"], c6["absolute_positions"][1:]))

anchor12 = 86 + 2048 * 30
c12 = m.build_candidate(anchor12, 12, items)
assert c12["words"][11] == "apple"
assert c12["absolute_positions"][11] == anchor12
assert m.phrase_is_valid([p - 1 for p in c12["local_positions"]])

# 7) Casos imposibles detectados explícitamente.
try:
    m.build_candidate(1, 2, items)
except ValueError:
    pass
else:
    raise AssertionError("Debe rechazarse ancla absoluta 1 en slot 2.")

try:
    m.build_candidate(100, 12, items)
except ValueError:
    pass
else:
    raise AssertionError("Debe rechazarse slot 12 en primer bloque con filtro V2.3.")

print("OK — todas las pruebas superadas")
print(f"Mapeo validado: {len(items)} registros")
print("Restricciones palabra/slot exhaustivas: 24.576 casos")
print(f"Levantamientos bidireccionales aleatorios: {lift_tests}")
print(
    "Slot 12 — intentos de checksum (prueba determinista): "
    f"media={sum(slot12_attempts)/len(slot12_attempts):.2f}, "
    f"max={max(slot12_attempts)}"
)
print("Integración SQLite temporal: OK")
