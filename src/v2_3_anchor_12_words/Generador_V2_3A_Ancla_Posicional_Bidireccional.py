#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador V2.3-A — ancla posicional bidireccional para 12 palabras BIP-39.

OBJETIVO
--------
La V2.3 original fijaba la palabra derivada de la posición absoluta introducida
como PRIMERA palabra del grupo. Esta variante permite indicar además en qué
posición del grupo (1..12) debe aparecer esa palabra.

Ejemplo conceptual:
    posición absoluta ancla = g
    posición dentro del grupo = 5

La palabra de g debe aparecer como palabra #5. Las posiciones absolutas #1..#4
se levantan HACIA ATRÁS (siempre positivas y estrictamente menores que g) y las
#6..#12 se levantan HACIA DELANTE (siempre estrictamente mayores que g).

REGLA LOCAL/ABSOLUTA
--------------------
    posición_local(g) = ((g - 1) mod 2048) + 1

La palabra depende de la posición local 1..2048. La posición absoluta sigue
siendo la coordenada ordinal del primo impar (1 -> 3, 2 -> 5, ...).

BIP-39 Y ENTROPÍA
-----------------
12 palabras codifican 132 bits: 128 bits de entropía + 4 bits de checksum.

- Si la palabra ancla ocupa una posición 1..11, sus 11 bits pertenecen por
  completo al campo de entropía. Se fijan exactamente esos 11 bits y los otros
  117 bits proceden de secrets.randbits(117).

- Si la palabra ancla ocupa la posición 12, el índice de 11 bits contiene
  7 bits de entropía + 4 bits de checksum. Se fijan los 7 bits de entropía
  correspondientes y se generan los otros 121 bits con CSPRNG; se usa rechazo
  hasta que el checksum SHA-256 coincida con los 4 bits finales del índice
  solicitado. La probabilidad esperada de aceptación por intento es ~1/16.

IMPORTANTE:
- La coordenada absoluta, los primos, el filtro estructural y SQLite NO añaden
  entropía criptográfica.
- El filtro V2.3 sigue siendo una regla de rechazo determinista.
- SQLite evita repetir LOCALMENTE frases ya registradas por esta instalación.
- Este software es experimental y no está auditado para custodiar activos reales.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import secrets
import sqlite3
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
import tkinter as tk
from tkinter import ttk, messagebox


# Se conserva el APP_NAME de V2.3 para reutilizar el mismo historial local.
# La migración de esquema es aditiva y compatible con la V2.3 original.
APP_NAME = "GeneradorPrimosPalabrasV23FiltroLinealTotal"

DATA_FILE_CANDIDATES = ("datos_2048.json", "datos_2048(3).json")
BLOCK = 2048
WORD_COUNT = 12
ENTROPY_BITS = 128
CHECKSUM_BITS = 4
MAX_CHECKSUM_ATTEMPTS = 1_000_000
MAX_CANDIDATE_ATTEMPTS = 500_000


# ---------------------------------------------------------------------------
# Filtro estructural V2.3
# ---------------------------------------------------------------------------

def _forward_distance(a: int, b: int) -> int:
    """Distancia hacia delante módulo 2048."""
    return (b - a) % BLOCK


def _backward_distance(a: int, b: int) -> int:
    """Distancia hacia atrás módulo 2048."""
    return (a - b) % BLOCK


def is_fixed_step_progression(local_positions: list[int]) -> bool:
    """Detecta progresión de paso fijo módulo 2048, incluido paso 0."""
    if len(local_positions) != WORD_COUNT:
        return False
    step = (local_positions[1] - local_positions[0]) % BLOCK
    return all(
        (local_positions[i + 1] - local_positions[i]) % BLOCK == step
        for i in range(WORD_COUNT - 1)
    )


def is_ordered_with_arbitrary_gaps(local_positions: list[int]) -> bool:
    """
    Detecta recorrido local ASC o DESC con cualquier separación y como máximo
    un cruce del borde 2048<->1, igual que la V2.3 original.
    """
    if len(local_positions) != WORD_COUNT:
        return False
    if len(set(local_positions)) != WORD_COUNT:
        return False

    forward = [
        _forward_distance(local_positions[i], local_positions[i + 1])
        for i in range(WORD_COUNT - 1)
    ]
    backward = [
        _backward_distance(local_positions[i], local_positions[i + 1])
        for i in range(WORD_COUNT - 1)
    ]
    ascending = all(d > 0 for d in forward) and sum(forward) < BLOCK
    descending = all(d > 0 for d in backward) and sum(backward) < BLOCK
    return ascending or descending


def is_forbidden_linear_pattern(local_positions: list[int]) -> bool:
    """Filtro maestro V2.3."""
    if len(local_positions) != WORD_COUNT:
        return False
    if is_fixed_step_progression(local_positions):
        return True
    if is_ordered_with_arbitrary_gaps(local_positions):
        return True
    return False


# ---------------------------------------------------------------------------
# Datos base posición -> primo -> palabra
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Item:
    position: int
    prime: int
    word: str


def base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def find_data_file() -> Path:
    for name in DATA_FILE_CANDIDATES:
        p = base_dir() / name
        if p.exists():
            return p
    expected = " o ".join(DATA_FILE_CANDIDATES)
    raise FileNotFoundError(f"No se encuentra {expected} junto a la aplicación.")


def app_data_dir() -> Path:
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA")
        if root:
            p = Path(root) / APP_NAME
        else:
            p = Path.home() / "AppData" / "Local" / APP_NAME
    else:
        p = Path.home() / f".{APP_NAME.lower()}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_items() -> list[Item]:
    path = find_data_file()
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = [
        Item(int(x["position"]), int(x["prime"]), str(x["word"]))
        for x in raw["items"]
    ]
    validate_items(items)
    return items


def is_prime_small(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def validate_items(items: list[Item]) -> None:
    if len(items) != BLOCK:
        raise ValueError(f"Se esperaban {BLOCK} registros y hay {len(items)}.")
    if [x.position for x in items] != list(range(1, BLOCK + 1)):
        raise ValueError("Las posiciones base deben ser exactamente 1..2048.")
    if len({x.word for x in items}) != BLOCK:
        raise ValueError("Las 2048 palabras deben ser únicas.")
    primes = [x.prime for x in items]
    if primes != sorted(primes) or len(set(primes)) != BLOCK:
        raise ValueError("La lista base de primos no es estrictamente creciente y única.")
    if any((p % 2 == 0 or not is_prime_small(p)) for p in primes):
        raise ValueError("Se ha detectado un valor base que no es primo impar.")


# ---------------------------------------------------------------------------
# Coordenadas locales y absolutas
# ---------------------------------------------------------------------------

def local_position(absolute_position: int) -> int:
    """Convierte una posición absoluta positiva en su símbolo local 1..2048."""
    if absolute_position < 1:
        raise ValueError("La posición absoluta debe ser positiva.")
    return ((absolute_position - 1) % BLOCK) + 1


def block_number(absolute_position: int) -> int:
    """Bloque 0 para 1..2048, bloque 1 para 2049..4096, etc."""
    if absolute_position < 1:
        raise ValueError("La posición absoluta debe ser positiva.")
    return (absolute_position - 1) // BLOCK


def lift_after(previous_absolute: int, next_local: int) -> int:
    """Menor g > previous_absolute con local_position(g) == next_local."""
    if previous_absolute < 1:
        raise ValueError("La posición anterior debe ser positiva.")
    if not 1 <= next_local <= BLOCK:
        raise ValueError("La posición local debe estar entre 1 y 2048.")

    k = ((previous_absolute - next_local) // BLOCK) + 1
    if k < 0:
        k = 0
    candidate = next_local + BLOCK * k
    if candidate <= previous_absolute:
        candidate += BLOCK
    return candidate


def lift_before(next_absolute: int, previous_local: int) -> int:
    """
    Mayor g positivo < next_absolute con local_position(g) == previous_local.

    Si no existe una aparición positiva anterior, se lanza ValueError.
    """
    if next_absolute < 1:
        raise ValueError("La posición siguiente debe ser positiva.")
    if not 1 <= previous_local <= BLOCK:
        raise ValueError("La posición local debe estar entre 1 y 2048.")

    k = (next_absolute - 1 - previous_local) // BLOCK
    if k < 0:
        raise ValueError(
            f"No existe una posición absoluta positiva anterior a {next_absolute} "
            f"con posición local {previous_local}."
        )

    candidate = previous_local + BLOCK * k
    if not (1 <= candidate < next_absolute):
        raise RuntimeError("Error interno en el levantamiento hacia atrás.")
    return candidate


def lift_local_series_anchored(
    anchor_absolute: int,
    local_positions: list[int],
    anchor_slot: int,
) -> list[int]:
    """
    Levanta 12 posiciones locales a coordenadas absolutas estrictamente crecientes,
    dejando anchor_absolute exactamente en anchor_slot (1..12).

    Hacia la derecha se usa la primera aparición posterior compatible.
    Hacia la izquierda se usa la primera aparición anterior compatible.
    """
    if len(local_positions) != WORD_COUNT:
        raise ValueError("Se esperaban 12 posiciones locales.")
    if not 1 <= anchor_slot <= WORD_COUNT:
        raise ValueError("La posición de la palabra ancla debe estar entre 1 y 12.")
    if anchor_absolute < 1:
        raise ValueError("La posición absoluta ancla debe ser positiva.")

    a = anchor_slot - 1
    expected_local = local_position(anchor_absolute)
    if local_positions[a] != expected_local:
        raise ValueError(
            "La palabra/index local de la posición indicada no coincide con el ancla absoluta."
        )

    absolute: list[int | None] = [None] * WORD_COUNT
    absolute[a] = anchor_absolute

    # Hacia delante.
    for i in range(a + 1, WORD_COUNT):
        absolute[i] = lift_after(int(absolute[i - 1]), local_positions[i])

    # Hacia atrás.
    for i in range(a - 1, -1, -1):
        absolute[i] = lift_before(int(absolute[i + 1]), local_positions[i])

    result = [int(x) for x in absolute]

    if any(b <= a0 for a0, b in zip(result, result[1:])):
        raise RuntimeError("Error interno: la serie absoluta no es estrictamente creciente.")
    if result[a] != anchor_absolute:
        raise RuntimeError("Error interno: el ancla absoluta se ha desplazado.")
    if any(local_position(g) != lp for g, lp in zip(result, local_positions)):
        raise RuntimeError("Error interno: una posición absoluta no conserva su símbolo local.")

    return result


def backward_is_guaranteed(anchor_absolute: int, anchor_slot: int) -> bool:
    """
    True si, aun en el peor salto local posible (hasta 2048 por paso hacia atrás),
    cualquier combinación de locales podrá levantarse sin cruzar por debajo de 1.
    """
    return anchor_absolute > (anchor_slot - 1) * BLOCK


# ---------------------------------------------------------------------------
# BIP-39: checksum y restricción de una palabra en cualquier slot
# ---------------------------------------------------------------------------

def checksum4(entropy_bytes: bytes) -> int:
    return hashlib.sha256(entropy_bytes).digest()[0] >> 4


def indexes_from_entropy(entropy_int: int) -> tuple[list[int], int]:
    if not 0 <= entropy_int < (1 << ENTROPY_BITS):
        raise ValueError("La entropía debe caber exactamente en 128 bits.")
    entropy_bytes = entropy_int.to_bytes(16, "big")
    cs = checksum4(entropy_bytes)
    combined = (entropy_int << CHECKSUM_BITS) | cs
    indexes = [
        (combined >> (11 * (11 - i))) & 0x7FF
        for i in range(WORD_COUNT)
    ]
    return indexes, cs


def phrase_is_valid(indexes: list[int]) -> bool:
    if len(indexes) != WORD_COUNT or any(not (0 <= i < BLOCK) for i in indexes):
        return False
    combined = 0
    for idx in indexes:
        combined = (combined << 11) | idx
    cs = combined & 0xF
    entropy_int = combined >> CHECKSUM_BITS
    entropy_bytes = entropy_int.to_bytes(16, "big")
    return cs == checksum4(entropy_bytes)


def insert_fixed_11_bits(random117: int, target_index: int, word_slot: int) -> int:
    """
    Construye 128 bits fijando exactamente los 11 bits correspondientes a
    word_slot 1..11 y distribuyendo los 117 bits aleatorios en el resto.

    Esto evita generar 128 bits y sobrescribir 11: la contribución aleatoria
    efectiva de esta etapa son exactamente 117 bits.
    """
    if not 1 <= word_slot <= 11:
        raise ValueError("Esta función sólo admite posiciones 1..11.")
    if not 0 <= target_index < BLOCK:
        raise ValueError("Índice BIP-39 fuera de 0..2047.")
    if not 0 <= random117 < (1 << 117):
        raise ValueError("random117 debe contener como máximo 117 bits.")

    shift = ENTROPY_BITS - 11 * word_slot
    low_width = shift
    low_mask = (1 << low_width) - 1 if low_width else 0
    low = random117 & low_mask
    high = random117 >> low_width

    entropy_int = (
        (high << (low_width + 11))
        | (target_index << low_width)
        | low
    )
    return entropy_int


def entropy_with_forced_word(
    target_index: int,
    word_slot: int,
    randbits: Callable[[int], int] = secrets.randbits,
) -> tuple[int, list[int], int, int]:
    """
    Genera entropía BIP-39 válida condicionada a que target_index aparezca
    exactamente en word_slot.

    Retorna:
        (entropy_int, indexes, checksum4, intentos_checksum)

    Slots 1..11:
        11 bits del índice están dentro de ENT -> 117 bits CSPRNG restantes.

    Slot 12:
        7 bits del índice están en ENT y 4 son checksum. Se generan 121 bits
        CSPRNG por candidato y se rechaza hasta que los 4 bits SHA-256 coincidan.
    """
    if not 0 <= target_index < BLOCK:
        raise ValueError("Índice BIP-39 fuera de 0..2047.")
    if not 1 <= word_slot <= WORD_COUNT:
        raise ValueError("La posición de palabra debe estar entre 1 y 12.")

    if word_slot <= 11:
        random117 = randbits(117)
        if not 0 <= random117 < (1 << 117):
            random117 &= (1 << 117) - 1
        entropy_int = insert_fixed_11_bits(random117, target_index, word_slot)
        indexes, cs = indexes_from_entropy(entropy_int)
        if indexes[word_slot - 1] != target_index:
            raise RuntimeError("Error interno al fijar los 11 bits del índice.")
        return entropy_int, indexes, cs, 1

    # Palabra 12 = 7 bits finales de ENT + 4 bits checksum.
    target_entropy7 = target_index >> 4
    desired_checksum = target_index & 0xF

    for attempt in range(1, MAX_CHECKSUM_ATTEMPTS + 1):
        random121 = randbits(121)
        if not 0 <= random121 < (1 << 121):
            random121 &= (1 << 121) - 1
        entropy_int = (random121 << 7) | target_entropy7
        indexes, cs = indexes_from_entropy(entropy_int)
        if cs == desired_checksum:
            if indexes[11] != target_index:
                raise RuntimeError("Error interno al fijar la palabra 12.")
            return entropy_int, indexes, cs, attempt

    raise RuntimeError(
        "No se encontró un checksum compatible dentro del límite de intentos. "
        "Esto sería extraordinariamente improbable con una fuente aleatoria normal."
    )


def entropy_model_text(word_slot: int) -> str:
    if 1 <= word_slot <= 11:
        return "11 bits fijados por el ancla + 117 bits CSPRNG"
    if word_slot == 12:
        return "7 bits fijados + 121 bits CSPRNG por candidato + checksum 4 bits por rechazo"
    return ""


# ---------------------------------------------------------------------------
# SQLite: historial compatible con V2.3 original
# ---------------------------------------------------------------------------

def db_connect() -> sqlite3.Connection:
    db_path = app_data_dir() / "historial_hashes.db"
    con = sqlite3.connect(db_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS generated (
            phrase_hash TEXT PRIMARY KEY,
            first_absolute_position TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Migración aditiva: V2.3 antigua seguirá funcionando porque estas columnas
    # son opcionales (NULL permitido).
    cols = {row[1] for row in con.execute("PRAGMA table_info(generated)")}
    if "anchor_absolute_position" not in cols:
        con.execute("ALTER TABLE generated ADD COLUMN anchor_absolute_position TEXT")
    if "anchor_word_slot" not in cols:
        con.execute("ALTER TABLE generated ADD COLUMN anchor_word_slot INTEGER")
    con.commit()
    return con


# ---------------------------------------------------------------------------
# Cálculo exacto de primos impares por posición absoluta
# ---------------------------------------------------------------------------

def simple_primes_upto(limit: int) -> list[int]:
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(math.isqrt(limit)) + 1):
        if sieve[p]:
            start = p * p
            sieve[start: limit + 1: p] = b"\x00" * (((limit - start) // p) + 1)
    return [i for i, flag in enumerate(sieve) if flag]


def upper_bound_for_odd_prime_position(n: int) -> int:
    """Cota superior práctica para el primo impar de posición n (1->3)."""
    if n < 1:
        raise ValueError("La posición debe ser positiva.")
    m = n + 1  # se excluye 2
    small = [2, 3, 5, 7, 11, 13]
    if m < len(small):
        return small[m] + 10
    x = float(m)
    return int(math.ceil(x * (math.log(x) + math.log(math.log(x))))) + 32


def odd_primes_at_positions(target_positions: list[int], progress=None) -> dict[int, int]:
    """
    Devuelve {posición_absoluta_de_primo_impar: primo}.
    Criba segmentada con memoria acotada.
    """
    targets = sorted(set(int(x) for x in target_positions))
    if not targets or targets[0] < 1:
        raise ValueError("Las posiciones objetivo deben ser enteros positivos.")

    target_set = set(targets)
    max_target = targets[-1]
    upper = upper_bound_for_odd_prime_position(max_target)

    while True:
        root = math.isqrt(upper)
        base_primes = [p for p in simple_primes_upto(root) if p >= 3]
        found: dict[int, int] = {}
        ordinal = 0

        segment_span = 1_000_000
        low = 3
        while low <= upper and len(found) < len(target_set):
            high = min(upper, low + segment_span - 1)
            if low % 2 == 0:
                low += 1
            if high % 2 == 0:
                high -= 1
            if high < low:
                break

            size = ((high - low) // 2) + 1
            seg = bytearray(b"\x01") * size

            for p in base_primes:
                if p * p > high:
                    break
                start = max(p * p, ((low + p - 1) // p) * p)
                if start % 2 == 0:
                    start += p
                if start > high:
                    continue
                idx = (start - low) // 2
                step = p
                count = ((size - 1 - idx) // step) + 1
                seg[idx::step] = b"\x00" * count

            for i, flag in enumerate(seg):
                if flag:
                    ordinal += 1
                    if ordinal in target_set:
                        found[ordinal] = low + 2 * i
                        if len(found) == len(target_set):
                            break

            if progress:
                progress(min(ordinal, max_target), max_target)
            low = high + 2

        if len(found) == len(target_set):
            return found

        upper = int(upper * 1.25) + 100


# ---------------------------------------------------------------------------
# Generación de candidato con ancla en slot arbitrario
# ---------------------------------------------------------------------------

def build_candidate(
    anchor_absolute: int,
    anchor_slot: int,
    items: list[Item],
    attempt_progress=None,
) -> dict:
    if anchor_absolute < 1:
        raise ValueError("La posición absoluta ancla debe ser un entero positivo.")
    if not 1 <= anchor_slot <= WORD_COUNT:
        raise ValueError("La posición dentro del grupo debe estar entre 1 y 12.")

    # Condición mínima necesaria: hacen falta anchor_slot-1 enteros positivos
    # estrictamente anteriores al ancla.
    if anchor_absolute < anchor_slot:
        raise ValueError(
            f"El ancla absoluta {anchor_absolute} no puede ocupar la posición {anchor_slot}: "
            f"harían falta {anchor_slot - 1} posiciones absolutas positivas anteriores."
        )

    anchor_local = local_position(anchor_absolute)
    target_index = anchor_local - 1

    # Con el filtro V2.3, si el ancla es la palabra 12 y está en el primer
    # bloque, las 12 absolutas quedarían 1..2048 en orden local estricto,
    # patrón que el filtro excluye por diseño.
    if anchor_slot == 12 and anchor_absolute <= BLOCK:
        raise ValueError(
            "Con el filtro lineal V2.3 activo, una ancla en la palabra 12 dentro "
            "del primer bloque (1..2048) no puede producir una serie admitida: "
            "las 12 posiciones locales quedarían estrictamente ascendentes. "
            "Usa una posición absoluta ancla > 2048 o una posición de palabra menor."
        )

    con = db_connect()
    total_checksum_attempts = 0
    boundary_rejections = 0
    filter_rejections = 0
    duplicate_rejections = 0

    try:
        for candidate_attempt in range(1, MAX_CANDIDATE_ATTEMPTS + 1):
            entropy_int, indexes, cs, checksum_attempts = entropy_with_forced_word(
                target_index, anchor_slot
            )
            total_checksum_attempts += checksum_attempts

            if indexes[anchor_slot - 1] != target_index:
                raise RuntimeError("Error interno: la palabra ancla no cae en el slot pedido.")
            if not phrase_is_valid(indexes):
                raise RuntimeError("Error interno de checksum.")

            local_positions = [idx + 1 for idx in indexes]

            if is_forbidden_linear_pattern(local_positions):
                filter_rejections += 1
                continue

            try:
                absolute_positions = lift_local_series_anchored(
                    anchor_absolute, local_positions, anchor_slot
                )
            except ValueError:
                boundary_rejections += 1
                if attempt_progress and candidate_attempt % 1000 == 0:
                    attempt_progress(
                        candidate_attempt, filter_rejections, boundary_rejections, duplicate_rejections
                    )
                continue

            selected = [items[idx] for idx in indexes]
            words = [x.word for x in selected]
            base_primes = [x.prime for x in selected]
            phrase = " ".join(words)
            phrase_hash = hashlib.sha256(phrase.encode("utf-8")).hexdigest()

            try:
                con.execute(
                    """
                    INSERT INTO generated(
                        phrase_hash,
                        first_absolute_position,
                        created_at,
                        anchor_absolute_position,
                        anchor_word_slot
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        phrase_hash,
                        str(absolute_positions[0]),
                        datetime.now(timezone.utc).isoformat(),
                        str(anchor_absolute),
                        anchor_slot,
                    ),
                )
                con.commit()
            except sqlite3.IntegrityError:
                duplicate_rejections += 1
                continue

            count = con.execute("SELECT COUNT(*) FROM generated").fetchone()[0]

            return {
                "anchor_absolute": anchor_absolute,
                "anchor_slot": anchor_slot,
                "anchor_local": anchor_local,
                "target_index": target_index,
                "entropy_hex": entropy_int.to_bytes(16, "big").hex(),
                "checksum_bits": f"{cs:04b}",
                "local_positions": local_positions,
                "absolute_positions": absolute_positions,
                "blocks": [block_number(g) for g in absolute_positions],
                "base_primes": base_primes,
                "words": words,
                "phrase": phrase,
                "local_count": count,
                "candidate_attempts": candidate_attempt,
                "checksum_attempts": total_checksum_attempts,
                "filter_rejections": filter_rejections,
                "boundary_rejections": boundary_rejections,
                "duplicate_rejections": duplicate_rejections,
                "entropy_model": entropy_model_text(anchor_slot),
            }

        raise RuntimeError(
            "Se alcanzó el límite de intentos sin encontrar una frase admisible. "
            "Si el ancla está muy cerca del inicio absoluto y se pide una posición "
            "alta dentro del grupo, aumenta la posición absoluta ancla para disponer "
            "de suficiente espacio hacia atrás."
        )
    finally:
        con.close()


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador V2.3-A — ancla posicional bidireccional")
        self.geometry("1240x860")
        self.minsize(1100, 760)

        try:
            self.items = load_items()
        except Exception as exc:
            messagebox.showerror("Error de datos", str(exc))
            self.destroy()
            return

        self.anchor_absolute_var = tk.StringVar(value="50000")
        self.anchor_slot_var = tk.StringVar(value="1")
        self.anchor_info_var = tk.StringVar()
        self.entropy_model_var = tk.StringVar()
        self.entropy_var = tk.StringVar()
        self.checksum_var = tk.StringVar()
        self.count_var = tk.StringVar()
        self.phrase_var = tk.StringVar()
        self.attempts_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Listo")
        self.current_result = None
        self.generating = False

        self._build_ui()
        self._update_anchor_info()

    def _build_ui(self):
        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Generador V2.3-A — palabra ancla en posición 1..12",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            main,
            text=(
                "Introduce una posición ABSOLUTA positiva. Esa coordenada determina la palabra ancla "
                "por su posición local 1..2048. Elige además en qué lugar del grupo (1..12) debe aparecer. "
                "La entropía se construye condicionando el índice BIP-39 en ese slot; después las coordenadas "
                "absolutas se levantan hacia atrás y hacia delante alrededor del ancla. "
                "El filtro lineal V2.3 y el historial SQLite permanecen activos."
            ),
            wraplength=1190,
            justify="left",
        ).pack(anchor="w", pady=(4, 10))

        input_frame = ttk.Frame(main)
        input_frame.pack(fill="x", pady=(0, 6))

        ttk.Label(input_frame, text="Posición absoluta ancla:").pack(side="left")
        e1 = ttk.Entry(input_frame, textvariable=self.anchor_absolute_var, width=18)
        e1.pack(side="left", padx=(8, 16))
        e1.bind("<KeyRelease>", lambda _e: self._update_anchor_info())
        e1.bind("<Return>", lambda _e: self.on_generate())

        ttk.Label(input_frame, text="Posición dentro del grupo:").pack(side="left")
        slot = ttk.Combobox(
            input_frame,
            textvariable=self.anchor_slot_var,
            values=[str(i) for i in range(1, 13)],
            width=5,
            state="readonly",
        )
        slot.pack(side="left", padx=(8, 16))
        slot.bind("<<ComboboxSelected>>", lambda _e: self._update_anchor_info())

        self.generate_btn = ttk.Button(
            input_frame, text="Generar 12 palabras", command=self.on_generate
        )
        self.generate_btn.pack(side="left", padx=(0, 12))

        info = ttk.Frame(main)
        info.pack(fill="x", pady=(0, 10))
        ttk.Label(info, textvariable=self.anchor_info_var).pack(anchor="w")
        ttk.Label(info, textvariable=self.entropy_model_var).pack(anchor="w", pady=(3, 0))

        table_frame = ttk.Frame(main)
        table_frame.pack(fill="both", expand=True)

        columns = ("n", "local", "baseprime", "absolute", "block", "absprime", "word")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {
            "n": "#",
            "local": "Posición local",
            "baseprime": "Primo base",
            "absolute": "Posición absoluta",
            "block": "Bloque",
            "absprime": "Primo absoluto",
            "word": "Palabra",
        }
        widths = {
            "n": 45,
            "local": 100,
            "baseprime": 105,
            "absolute": 145,
            "block": 80,
            "absprime": 145,
            "word": 190,
        }
        for c in columns:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="center" if c != "word" else "w")
        self.tree.tag_configure("anchor", background="#fff2cc")
        self.tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

        phrase_box = ttk.LabelFrame(main, text="Serie de 12 palabras", padding=10)
        phrase_box.pack(fill="x", pady=(12, 8))
        phrase_entry = ttk.Entry(phrase_box, textvariable=self.phrase_var, state="readonly")
        phrase_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(phrase_box, text="Copiar", command=self.copy_phrase).pack(
            side="left", padx=(8, 0)
        )

        meta = ttk.Frame(main)
        meta.pack(fill="x", pady=(2, 0))
        ttk.Label(meta, text="Entropía (hex):").grid(row=0, column=0, sticky="w")
        ttk.Label(meta, textvariable=self.entropy_var).grid(
            row=0, column=1, sticky="w", padx=(8, 20)
        )
        ttk.Label(meta, text="Checksum:").grid(row=0, column=2, sticky="w")
        ttk.Label(meta, textvariable=self.checksum_var).grid(
            row=0, column=3, sticky="w", padx=(8, 20)
        )

        ttk.Label(meta, text="Frases únicas registradas localmente:").grid(
            row=1, column=0, sticky="w", pady=(5, 0)
        )
        ttk.Label(meta, textvariable=self.count_var).grid(
            row=1, column=1, sticky="w", padx=(8, 20), pady=(5, 0)
        )
        ttk.Label(meta, text="Intentos/rechazos:").grid(
            row=1, column=2, sticky="w", pady=(5, 0)
        )
        ttk.Label(meta, textvariable=self.attempts_var).grid(
            row=1, column=3, sticky="w", padx=(8, 20), pady=(5, 0)
        )

        ttk.Label(meta, text="Estado:").grid(row=2, column=0, sticky="w", pady=(5, 0))
        ttk.Label(meta, textvariable=self.status_var).grid(
            row=2, column=1, columnspan=3, sticky="w", padx=(8, 20), pady=(5, 0)
        )

        ttk.Label(
            main,
            text=(
                "Nota de rigor: no se 'calcula la entropía hacia atrás'. Se genera una entropía BIP-39 "
                "condicionada a que la palabra ancla ocupe el slot elegido; lo que se calcula hacia atrás "
                "y hacia delante son las coordenadas absolutas compatibles con los índices obtenidos. "
                "Si el ancla está muy cerca de 1 y se pide un slot alto, puede no existir suficiente espacio "
                "positivo hacia atrás. Este programa detecta y rechaza esos casos sin inventar coordenadas."
            ),
            wraplength=1190,
            justify="left",
        ).pack(anchor="w", pady=(10, 0))

    def _parse_anchor_absolute(self) -> int | None:
        try:
            p = int(self.anchor_absolute_var.get().strip())
            if p >= 1:
                return p
        except ValueError:
            pass
        return None

    def _parse_anchor_slot(self) -> int | None:
        try:
            s = int(self.anchor_slot_var.get().strip())
            if 1 <= s <= 12:
                return s
        except ValueError:
            pass
        return None

    def _update_anchor_info(self):
        g = self._parse_anchor_absolute()
        slot = self._parse_anchor_slot()

        if g is None:
            self.anchor_info_var.set("Introduce una posición absoluta entera y positiva.")
            self.entropy_model_var.set("")
            return
        if slot is None:
            self.anchor_info_var.set("Selecciona una posición de palabra entre 1 y 12.")
            self.entropy_model_var.set("")
            return

        lp = local_position(g)
        item = self.items[lp - 1]
        b = block_number(g)
        guarantee = (
            "espacio hacia atrás garantizado para cualquier combinación"
            if backward_is_guaranteed(g, slot)
            else "zona cercana al origen: algunas combinaciones pueden no tener predecesores positivos"
        )
        self.anchor_info_var.set(
            f"Ancla: absoluta {g} · local {lp} · bloque {b} · palabra «{item.word}» "
            f"· primo base {item.prime} · debe caer en palabra #{slot}"
        )
        self.entropy_model_var.set(
            f"Modelo: {entropy_model_text(slot)} · {guarantee}"
        )

    def on_generate(self):
        if self.generating:
            return

        anchor_absolute = self._parse_anchor_absolute()
        anchor_slot = self._parse_anchor_slot()
        if anchor_absolute is None:
            messagebox.showwarning(
                "Posición inválida", "Introduce una posición absoluta entera y positiva."
            )
            return
        if anchor_slot is None:
            messagebox.showwarning(
                "Posición inválida", "Selecciona una posición dentro del grupo entre 1 y 12."
            )
            return

        self.generating = True
        self.generate_btn.configure(state="disabled")
        self.status_var.set("Generando entropía condicionada y levantando coordenadas…")

        def attempt_progress(done, filt, boundary, dup):
            self.after(
                0,
                lambda: self.status_var.set(
                    f"Buscando candidato… intentos {done:,} · filtro {filt:,} "
                    f"· borde {boundary:,} · duplicados {dup:,}"
                ),
            )

        def prime_progress(done, total):
            if total > 0:
                pct = min(100, int(done * 100 / total))
                self.after(
                    0, lambda: self.status_var.set(f"Calculando primos absolutos… {pct}%")
                )

        def worker():
            try:
                candidate = build_candidate(
                    anchor_absolute,
                    anchor_slot,
                    self.items,
                    attempt_progress=attempt_progress,
                )
                self.after(
                    0,
                    lambda: self.status_var.set(
                        "Candidato válido. Calculando primos absolutos…"
                    ),
                )
                primes_map = odd_primes_at_positions(
                    candidate["absolute_positions"], progress=prime_progress
                )
                candidate["absolute_primes"] = [
                    primes_map[g] for g in candidate["absolute_positions"]
                ]
                self.after(0, lambda: self._display_result(candidate))
            except Exception as exc:
                self.after(0, lambda e=exc: self._generation_error(e))

        threading.Thread(target=worker, daemon=True).start()

    def _generation_error(self, exc: Exception):
        self.generating = False
        self.generate_btn.configure(state="normal")
        self.status_var.set("Error")
        messagebox.showerror("Error", str(exc))

    def _display_result(self, result: dict):
        self.current_result = result
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i in range(WORD_COUNT):
            tags = ("anchor",) if i + 1 == result["anchor_slot"] else ()
            self.tree.insert(
                "",
                "end",
                values=(
                    i + 1,
                    result["local_positions"][i],
                    result["base_primes"][i],
                    result["absolute_positions"][i],
                    result["blocks"][i],
                    result["absolute_primes"][i],
                    result["words"][i],
                ),
                tags=tags,
            )

        self.phrase_var.set(result["phrase"])
        self.entropy_var.set(result["entropy_hex"])
        self.checksum_var.set(result["checksum_bits"])
        self.count_var.set(str(result["local_count"]))
        self.attempts_var.set(
            f"candidatos {result['candidate_attempts']:,} · checksum {result['checksum_attempts']:,} "
            f"· filtro {result['filter_rejections']:,} · borde {result['boundary_rejections']:,} "
            f"· dup {result['duplicate_rejections']:,}"
        )
        self.status_var.set(
            f"Listo — «{result['words'][result['anchor_slot'] - 1]}» fijada en "
            f"palabra #{result['anchor_slot']} · ancla absoluta {result['anchor_absolute']}"
        )
        self.generating = False
        self.generate_btn.configure(state="normal")

    def copy_phrase(self):
        phrase = self.phrase_var.get().strip()
        if not phrase:
            return
        self.clipboard_clear()
        self.clipboard_append(phrase)
        self.update()
        messagebox.showinfo("Copiado", "La serie de 12 palabras se ha copiado al portapapeles.")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
