#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador V2.6 AUTO TURBO: generación automática por rango de valores y archivos.

IDEA CENTRAL
------------
Los 2048 símbolos base no se tratan como una lista que termina en 2048.
Se repiten por bloques sobre una coordenada absoluta infinita:

    posición_local(g) = ((g - 1) mod 2048) + 1

La palabra depende de la posición local 1..2048, pero la posición absoluta g
puede crecer sin límite. Para pasar de una posición absoluta anterior a la
siguiente posición local generada por la entropía, se elige SIEMPRE la primera
posición absoluta posterior que tenga ese mismo residuo módulo 2048.

ENTROPÍA Y FILTRO
-----------------
Se conserva el mismo modelo de la V1 (128 bits de entropía + checksum SHA-256).
Filtro por rechazo de patrones lineales: órdenes ascendentes o descendentes
con cualquier separación, progresiones de paso fijo y sus cruces del borde 2048↔1.

EXPORTACIÓN MULTI-GRUPO
-----------------------
Permite la generación iterativa de múltiples grupos (N secuencias de 12 palabras),
almacenándolas en un archivo de texto secuencialmente. El motor TURBO reduce trabajo innecesario, agrupa escrituras y usa multiproceso
para la criba de primos, empleando por defecto ~75% de los procesadores lógicos.
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
import time
import bisect
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


APP_NAME = "GeneradorPrimosPalabrasV25TurboMultiCPU"
DATA_FILE = "datos_2048.json"
BLOCK = 2048

WORD_COUNT = 12

# Rendimiento
DEFAULT_CPU_FRACTION = 0.75
DB_COMMIT_EVERY = 2000
FILE_WRITE_BATCH = 4096
MIN_PARALLEL_ORDINAL = 100_000
_WORKER_BASE_PRIMES: tuple[int, ...] = ()

def _forward_distance(a: int, b: int) -> int:
    return (b - a) % BLOCK

def _backward_distance(a: int, b: int) -> int:
    return (a - b) % BLOCK

def is_fixed_step_progression(local_positions: list[int]) -> bool:
    if len(local_positions) != WORD_COUNT:
        return False
    step = (local_positions[1] - local_positions[0]) % BLOCK
    return all(
        (local_positions[i + 1] - local_positions[i]) % BLOCK == step
        for i in range(WORD_COUNT - 1)
    )

def is_ordered_with_arbitrary_gaps(local_positions: list[int]) -> bool:
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
    if len(local_positions) != WORD_COUNT:
        return False
    if is_fixed_step_progression(local_positions):
        return True
    if is_ordered_with_arbitrary_gaps(local_positions):
        return True
    return False


@dataclass(frozen=True)
class Item:
    position: int
    prime: int
    word: str


def base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


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
    path = base_dir() / DATA_FILE
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra {DATA_FILE} junto a la aplicación.")
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = [Item(int(x["position"]), int(x["prime"]), str(x["word"])) for x in raw["items"]]
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


def local_position(absolute_position: int) -> int:
    if absolute_position < 1:
        raise ValueError("La posición absoluta debe ser positiva.")
    return ((absolute_position - 1) % BLOCK) + 1


def block_number(absolute_position: int) -> int:
    if absolute_position < 1:
        raise ValueError("La posición absoluta debe ser positiva.")
    return (absolute_position - 1) // BLOCK


def lift_after(previous_absolute: int, next_local: int) -> int:
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


def lift_local_series(first_absolute: int, local_positions: list[int]) -> list[int]:
    if len(local_positions) != 12:
        raise ValueError("Se esperaban 12 posiciones locales.")
    if local_positions[0] != local_position(first_absolute):
        raise ValueError("La primera posición local no corresponde al inicio absoluto.")
    absolute = [first_absolute]
    for p in local_positions[1:]:
        absolute.append(lift_after(absolute[-1], p))
    if any(b <= a for a, b in zip(absolute, absolute[1:])):
        raise RuntimeError("Error interno: la serie absoluta no es estrictamente creciente.")
    return absolute


def db_connect() -> sqlite3.Connection:
    """
    Una sola conexión por proceso de generación.
    WAL + synchronous NORMAL reduce mucho el coste de registrar grandes lotes.
    """
    db_path = app_data_dir() / "historial_hashes.db"
    con = sqlite3.connect(db_path, timeout=60.0)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA temp_store=MEMORY")
    con.execute("""
        CREATE TABLE IF NOT EXISTS generated (
            phrase_hash TEXT PRIMARY KEY,
            first_absolute_position TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    con.commit()
    return con


def checksum4(entropy_bytes: bytes) -> int:
    return hashlib.sha256(entropy_bytes).digest()[0] >> 4


def indexes_from_entropy(entropy_int: int) -> tuple[list[int], int]:
    entropy_bytes = entropy_int.to_bytes(16, "big")
    cs = checksum4(entropy_bytes)
    combined = (entropy_int << 4) | cs
    indexes = [
        (combined >> (11 * (11 - i))) & 0x7FF
        for i in range(12)
    ]
    return indexes, cs


def phrase_is_valid(indexes: list[int]) -> bool:
    if len(indexes) != 12 or any(not (0 <= i < BLOCK) for i in indexes):
        return False
    combined = 0
    for idx in indexes:
        combined = (combined << 11) | idx
    cs = combined & 0xF
    entropy_int = combined >> 4
    entropy_bytes = entropy_int.to_bytes(16, "big")
    return cs == checksum4(entropy_bytes)


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
    if n < 1:
        raise ValueError("La posición debe ser positiva.")
    m = n + 1  # primo impar n = primo ordinario n+1
    small = [2, 3, 5, 7, 11, 13]
    if m < len(small):
        return small[m] + 10
    x = float(m)
    return int(math.ceil(x * (math.log(x) + math.log(math.log(x))))) + 32


def _sieve_segment_bytes(low: int, high: int, base_primes: tuple[int, ...]) -> bytearray:
    """Criba sólo impares en [low, high], ambos impares."""
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

    return seg


def _init_sieve_worker(base_primes: tuple[int, ...]) -> None:
    global _WORKER_BASE_PRIMES
    _WORKER_BASE_PRIMES = base_primes


def _count_segment_worker(task: tuple[int, int, int]) -> tuple[int, int]:
    idx, low, high = task
    seg = _sieve_segment_bytes(low, high, _WORKER_BASE_PRIMES)
    return idx, seg.count(1)


def _extract_segment_worker(
    task: tuple[int, int, int, tuple[int, ...]]
) -> tuple[int, dict[int, int]]:
    """
    local_ordinals: ordinal 1-based de los primos DENTRO del segmento.
    """
    idx, low, high, local_ordinals = task
    wanted = set(local_ordinals)
    seg = _sieve_segment_bytes(low, high, _WORKER_BASE_PRIMES)
    out: dict[int, int] = {}

    ordinal = 0
    for i, flag in enumerate(seg):
        if flag:
            ordinal += 1
            if ordinal in wanted:
                out[ordinal] = low + 2 * i
                if len(out) == len(wanted):
                    break

    return idx, out


def _make_segments(upper: int, workers: int) -> list[tuple[int, int, int]]:
    """
    Crea suficientes segmentos para repartir trabajo entre todos los procesos,
    sin hacerlos tan pequeños que el coste IPC domine.
    """
    total_width = max(1, upper - 2)
    desired_segments = max(1, workers * 8)
    span = math.ceil(total_width / desired_segments)
    span = max(500_000, min(8_000_000, span))
    if span % 2:
        span += 1

    segments = []
    low = 3
    idx = 0
    while low <= upper:
        high = min(upper, low + span - 1)
        if high % 2 == 0:
            high -= 1
        if high < low:
            break
        segments.append((idx, low, high))
        idx += 1
        low = high + 2
    return segments


def odd_primes_at_positions_serial(
    target_positions: list[int],
    progress=None
) -> dict[int, int]:
    """Versión optimizada de un solo proceso para rangos pequeños."""
    targets = sorted(set(int(x) for x in target_positions))
    if not targets or targets[0] < 1:
        raise ValueError("Las posiciones objetivo deben ser enteros positivos.")

    target_set = set(targets)
    max_target = targets[-1]
    upper = upper_bound_for_odd_prime_position(max_target)

    root = math.isqrt(upper)
    base_primes = tuple(p for p in simple_primes_upto(root) if p >= 3)

    found: dict[int, int] = {}
    ordinal = 0
    segments = _make_segments(upper, 1)

    for done, (_idx, low, high) in enumerate(segments, start=1):
        seg = _sieve_segment_bytes(low, high, base_primes)
        for i, flag in enumerate(seg):
            if flag:
                ordinal += 1
                if ordinal in target_set:
                    found[ordinal] = low + 2 * i
                    if len(found) == len(target_set):
                        return found
        if progress:
            progress("Criba 1 CPU", done, len(segments))

    if len(found) != len(target_set):
        raise RuntimeError("No se localizaron todas las posiciones primas.")
    return found


def odd_primes_at_positions_parallel(
    target_positions: list[int],
    workers: int,
    progress=None
) -> dict[int, int]:
    """
    Criba paralela de dos pasadas.

    1) Todos los procesos cuentan primos por segmento.
    2) Con los acumulados ya conocemos en qué segmentos caen las posiciones
       pedidas y sólo esos segmentos se vuelven a cribar para extraer los valores.

    De esta forma se usan varios núcleos reales de CPU (procesos, no threads,
    para evitar el GIL de CPython).
    """
    targets = sorted(set(int(x) for x in target_positions))
    if not targets or targets[0] < 1:
        raise ValueError("Las posiciones objetivo deben ser enteros positivos.")

    max_target = targets[-1]
    workers = max(1, int(workers))

    # En rangos pequeños, lanzar procesos tarda más que resolverlo en local.
    if workers <= 1 or max_target < MIN_PARALLEL_ORDINAL:
        return odd_primes_at_positions_serial(targets, progress=progress)

    upper = upper_bound_for_odd_prime_position(max_target)
    root = math.isqrt(upper)
    base_primes = tuple(p for p in simple_primes_upto(root) if p >= 3)
    segments = _make_segments(upper, workers)

    # Si el rango sólo produce un segmento, no hay nada que paralelizar.
    if len(segments) < 2:
        return odd_primes_at_positions_serial(targets, progress=progress)

    counts = [0] * len(segments)

    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(
        max_workers=workers,
        mp_context=ctx,
        initializer=_init_sieve_worker,
        initargs=(base_primes,),
    ) as executor:

        futures = {
            executor.submit(_count_segment_worker, seg): seg[0]
            for seg in segments
        }

        done_count = 0
        for future in as_completed(futures):
            idx, count = future.result()
            counts[idx] = count
            done_count += 1
            if progress:
                progress("Criba paralela 1/2", done_count, len(segments))

        cumulative = []
        running = 0
        for count in counts:
            running += count
            cumulative.append(running)

        if running < max_target:
            # La cota analítica debería ser suficiente; dejamos un error explícito
            # antes que devolver un resultado incorrecto.
            raise RuntimeError(
                f"Cota insuficiente: se contaron {running} primos impares "
                f"y se necesitaba la posición {max_target}."
            )

        segment_wants: dict[int, list[int]] = {}
        target_meta: dict[int, tuple[int, int]] = {}

        for target in targets:
            seg_idx = bisect.bisect_left(cumulative, target)
            previous = cumulative[seg_idx - 1] if seg_idx > 0 else 0
            local_ordinal = target - previous
            segment_wants.setdefault(seg_idx, []).append(local_ordinal)
            target_meta[target] = (seg_idx, local_ordinal)

        extract_futures = {}
        for seg_idx, wanted in segment_wants.items():
            _idx, low, high = segments[seg_idx]
            task = (seg_idx, low, high, tuple(sorted(set(wanted))))
            fut = executor.submit(_extract_segment_worker, task)
            extract_futures[fut] = seg_idx

        extracted_by_segment: dict[int, dict[int, int]] = {}
        done_extract = 0
        for future in as_completed(extract_futures):
            seg_idx, found_local = future.result()
            extracted_by_segment[seg_idx] = found_local
            done_extract += 1
            if progress:
                progress(
                    "Criba paralela 2/2",
                    done_extract,
                    len(extract_futures)
                )

    result = {}
    for target, (seg_idx, local_ordinal) in target_meta.items():
        result[target] = extracted_by_segment[seg_idx][local_ordinal]

    return result


def build_candidate_fast(
    first_absolute: int,
    items: list[Item],
    con: sqlite3.Connection
) -> dict:
    """
    Misma lógica de generación que V2.4, pero reutiliza la conexión SQLite y no
    hace COMMIT/COUNT por cada frase.
    """
    if first_absolute < 1:
        raise ValueError("La posición absoluta inicial debe ser un entero positivo.")

    first_local = local_position(first_absolute)
    first_index = first_local - 1

    while True:
        random_tail = secrets.randbits(117)
        entropy_int = (first_index << 117) | random_tail
        indexes, cs = indexes_from_entropy(entropy_int)

        # indexes_from_entropy construye directamente el checksum correcto.
        if indexes[0] != first_index:
            raise RuntimeError("Error interno: el primer índice no coincide.")

        local_positions = [idx + 1 for idx in indexes]
        if is_forbidden_linear_pattern(local_positions):
            continue

        selected = [items[idx] for idx in indexes]
        words = [x.word for x in selected]
        base_primes = [x.prime for x in selected]
        phrase = " ".join(words)
        phrase_hash = hashlib.sha256(phrase.encode("utf-8")).hexdigest()

        cur = con.execute(
            "INSERT OR IGNORE INTO generated"
            "(phrase_hash, first_absolute_position, created_at) "
            "VALUES (?, ?, ?)",
            (
                phrase_hash,
                str(first_absolute),
                datetime.now(timezone.utc).isoformat()
            )
        )
        if cur.rowcount == 1:
            break

    absolute_positions = lift_local_series(first_absolute, local_positions)

    return {
        "first_absolute": first_absolute,
        "first_local": first_local,
        "entropy_hex": entropy_int.to_bytes(16, "big").hex(),
        "checksum_bits": f"{cs:04b}",
        "local_positions": local_positions,
        "absolute_positions": absolute_positions,
        "blocks": [block_number(g) for g in absolute_positions],
        "base_primes": base_primes,
        "words": words,
        "phrase": phrase,
        "local_count": 0,  # se completa al final del lote
    }




# ---------------------- GENERACIÓN AUTOMÁTICA POR RANGO ---------------------

def safe_filename_component(text: str) -> str:
    value = "".join(
        ch if (ch.isalnum() or ch in "-_") else "_"
        for ch in str(text).strip()
    )
    value = value.strip("_")
    return value or "secuencias"


def generate_automatic_range(
    start_value: int,
    end_value: int,
    groups_per_value: int,
    groups_per_file: int,
    destination_dir: Path,
    prefix: str,
    items: list[Item],
    stop_event=None,
    progress=None,
    runtime_state=None,
) -> dict:
    """
    Generación automática por rango.

    CAMBIO V2.7:
    - NO envía ningún evento de interfaz por cada frase.
    - La GUI sólo recibe eventos al iniciar/completar un archivo y al completar
      un valor.
    - runtime_state es un diccionario compartido de muy bajo coste que permite
      a Tkinter consultar un pulso interno del motor sin crear millones de
      eventos gráficos.
    - SQLite y el control de hashes duplicados permanecen activos.
    """
    start_value = int(start_value)
    end_value = int(end_value)
    groups_per_value = int(groups_per_value)
    groups_per_file = int(groups_per_file)
    destination_dir = Path(destination_dir)

    if start_value < 1:
        raise ValueError("El valor inicial debe ser un entero positivo.")
    if end_value < start_value:
        raise ValueError("El valor final debe ser mayor o igual que el inicial.")
    if groups_per_value < 1:
        raise ValueError("Los grupos totales por valor deben ser al menos 1.")
    if groups_per_file < 1:
        raise ValueError("Los grupos por archivo deben ser al menos 1.")

    destination_dir.mkdir(parents=True, exist_ok=True)

    clean_prefix = safe_filename_component(prefix)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    session_dir = destination_dir / (
        f"{clean_prefix}_{start_value}_a_{end_value}_{timestamp}"
    )
    session_dir.mkdir(parents=True, exist_ok=False)

    manifest_path = session_dir / "MANIFIESTO.tsv"

    value_count = end_value - start_value + 1
    total_groups_planned = value_count * groups_per_value
    files_per_value = math.ceil(groups_per_value / groups_per_file)
    total_files_planned = value_count * files_per_value

    generated_total = 0
    files_created = 0
    completed_values = 0
    last_candidate = None
    stopped = False

    width = max(6, len(str(end_value)))

    def pulse(**kwargs):
        """
        Actualiza estado interno SIN llamar a Tkinter.
        El hilo GUI lo consulta una vez por segundo.
        """
        if runtime_state is None:
            return

        runtime_state["last_activity"] = time.perf_counter()

        for key, value in kwargs.items():
            runtime_state[key] = value

    con = None

    try:
        con = db_connect()

        initial_db_count = con.execute(
            "SELECT COUNT(*) FROM generated"
        ).fetchone()[0]

        pulse(
            phase="generation",
            generated_total=0,
            total_groups_planned=total_groups_planned,
            session_dir=str(session_dir),
        )

        with manifest_path.open(
            "w",
            encoding="utf-8",
            buffering=1024 * 1024
        ) as manifest:

            manifest.write(
                "valor\tparte\tarchivo\tgrupos_generados\t"
                "primer_grupo_global\tultimo_grupo_global\t"
                "primera_posicion_absoluta\t"
                "siguiente_posicion_absoluta\testado\n"
            )

            for value in range(start_value, end_value + 1):
                if stop_event is not None and stop_event.is_set():
                    stopped = True
                    break

                current_abs = value
                generated_for_value = 0
                part = 1

                while generated_for_value < groups_per_value:
                    if stop_event is not None and stop_event.is_set():
                        stopped = True
                        break

                    requested_in_file = min(
                        groups_per_file,
                        groups_per_value - generated_for_value
                    )

                    filename = (
                        f"{clean_prefix}_valor_{value:0{width}d}"
                        f"_parte_{part:04d}.txt"
                    )

                    filepath = session_dir / filename

                    first_global = generated_total + 1
                    first_absolute_for_file = current_abs
                    generated_in_file = 0
                    write_buffer: list[str] = []

                    pulse(
                        phase="generation",
                        current_value=value,
                        current_part=part,
                        current_file=filename,
                        generated_total=generated_total,
                        generated_for_value=generated_for_value,
                    )

                    # Un único evento GUI al INICIAR cada archivo.
                    if progress is not None:
                        progress({
                            "kind": "file_start",
                            "value": value,
                            "part": part,
                            "filename": filename,
                            "generated_total": generated_total,
                            "total_groups_planned": total_groups_planned,
                            "generated_for_value": generated_for_value,
                            "groups_per_value": groups_per_value,
                            "groups_in_this_file": requested_in_file,
                            "files_created": files_created,
                            "total_files_planned": total_files_planned,
                            "session_dir": str(session_dir),
                        })

                    with filepath.open(
                        "w",
                        encoding="utf-8",
                        buffering=1024 * 1024
                    ) as out:

                        for _ in range(requested_in_file):
                            if stop_event is not None and stop_event.is_set():
                                stopped = True
                                break

                            candidate = build_candidate_fast(
                                current_abs,
                                items,
                                con
                            )

                            last_candidate = candidate
                            write_buffer.append(candidate["phrase"])

                            generated_total += 1
                            generated_for_value += 1
                            generated_in_file += 1

                            # Mantiene exactamente la regla secuencial V2.5.
                            current_abs = (
                                candidate["absolute_positions"][-1] + 1
                            )

                            if len(write_buffer) >= FILE_WRITE_BATCH:
                                out.write("\n".join(write_buffer))
                                out.write("\n")
                                write_buffer.clear()

                            # SQLite se mantiene exactamente como requisito.
                            if generated_total % DB_COMMIT_EVERY == 0:
                                con.commit()

                                # Pulso interno sin crear eventos Tkinter.
                                pulse(
                                    phase="generation",
                                    current_value=value,
                                    current_part=part,
                                    current_file=filename,
                                    generated_total=generated_total,
                                    generated_for_value=generated_for_value,
                                )

                        if write_buffer:
                            out.write("\n".join(write_buffer))
                            out.write("\n")

                    if generated_in_file == 0:
                        try:
                            filepath.unlink()
                        except Exception:
                            pass
                        break

                    files_created += 1

                    last_global = generated_total
                    state = (
                        "DETENIDO"
                        if stopped and generated_in_file < requested_in_file
                        else "COMPLETO"
                    )

                    manifest.write(
                        f"{value}\t"
                        f"{part}\t"
                        f"{filename}\t"
                        f"{generated_in_file}\t"
                        f"{first_global}\t"
                        f"{last_global}\t"
                        f"{first_absolute_for_file}\t"
                        f"{current_abs}\t"
                        f"{state}\n"
                    )
                    manifest.flush()

                    pulse(
                        phase="generation",
                        current_value=value,
                        current_part=part,
                        current_file=filename,
                        generated_total=generated_total,
                        generated_for_value=generated_for_value,
                    )

                    # Un único evento GUI al COMPLETAR cada archivo.
                    if progress is not None:
                        progress({
                            "kind": "file",
                            "value": value,
                            "part": part,
                            "generated_total": generated_total,
                            "total_groups_planned": total_groups_planned,
                            "generated_for_value": generated_for_value,
                            "groups_per_value": groups_per_value,
                            "groups_in_this_file": generated_in_file,
                            "files_created": files_created,
                            "total_files_planned": total_files_planned,
                            "filepath": str(filepath),
                            "session_dir": str(session_dir),
                        })

                    part += 1

                    if stopped:
                        break

                if stopped:
                    break

                completed_values += 1

                pulse(
                    phase="generation",
                    current_value=value,
                    generated_total=generated_total,
                    generated_for_value=groups_per_value,
                )

                if progress is not None:
                    progress({
                        "kind": "value",
                        "value": value,
                        "completed_values": completed_values,
                        "value_count": value_count,
                        "generated_total": generated_total,
                        "total_groups_planned": total_groups_planned,
                        "files_created": files_created,
                        "total_files_planned": total_files_planned,
                        "session_dir": str(session_dir),
                    })

        con.commit()

        final_db_count = con.execute(
            "SELECT COUNT(*) FROM generated"
        ).fetchone()[0]

        pulse(
            phase="generation_finished",
            generated_total=generated_total,
            files_created=files_created,
        )

        return {
            "session_dir": str(session_dir),
            "manifest_path": str(manifest_path),
            "start_value": start_value,
            "end_value": end_value,
            "groups_per_value": groups_per_value,
            "groups_per_file": groups_per_file,
            "value_count": value_count,
            "completed_values": completed_values,
            "total_groups_planned": total_groups_planned,
            "generated_total": generated_total,
            "total_files_planned": total_files_planned,
            "files_created": files_created,
            "stopped": stopped,
            "initial_db_count": initial_db_count,
            "final_db_count": final_db_count,
            "last_candidate": last_candidate,
        }

    finally:
        if con is not None:
            try:
                con.commit()
            except Exception:
                pass

            try:
                con.close()
            except Exception:
                pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Generador V2.7 AUTO TURBO — Motor desacoplado de Tkinter")
        self.geometry("1260x900")
        self.minsize(1080, 780)

        try:
            self.items = load_items()
        except Exception as exc:
            messagebox.showerror("Error de datos", str(exc))
            self.destroy()
            return

        self.logical_cpus = max(1, os.cpu_count() or 1)

        self.min_cpu_workers = (
            1
            if self.logical_cpus == 1
            else (self.logical_cpus // 2) + 1
        )

        self.default_cpu_workers = min(
            self.logical_cpus,
            max(
                self.min_cpu_workers,
                int(math.ceil(
                    self.logical_cpus * DEFAULT_CPU_FRACTION
                ))
            )
        )

        # Parámetros automáticos.
        self.start_value_var = tk.StringVar(value="1")
        self.end_value_var = tk.StringVar(value="10")
        self.groups_per_value_var = tk.StringVar(value="1000")
        self.groups_per_file_var = tk.StringVar(value="1000")
        self.prefix_var = tk.StringVar(value="secuencias")
        self.destination_var = tk.StringVar()

        self.cpu_workers_var = tk.StringVar(
            value=str(self.default_cpu_workers)
        )

        # Estado.
        self.initial_info_var = tk.StringVar()
        self.plan_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Listo")
        self.current_value_var = tk.StringVar(value="-")
        self.current_file_var = tk.StringVar(value="-")
        self.current_value_progress_var = tk.StringVar(value="0 / 0")
        self.overall_progress_var = tk.StringVar(value="0 / 0")
        self.output_dir_var = tk.StringVar(value="-")

        # Última serie, para mantener la parte visual del V2.5.
        self.entropy_var = tk.StringVar()
        self.checksum_var = tk.StringVar()
        self.count_var = tk.StringVar()
        self.phrase_var = tk.StringVar()

        self.current_result = None
        self.generating = False
        self.stop_event = threading.Event()

        # V2.7: cronómetros independientes y pulso real del motor.
        self.generation_timer_var = tk.StringVar(value="00:00:00")
        self.prime_timer_var = tk.StringVar(value="Pendiente")
        self.engine_heartbeat_var = tk.StringVar(value="Motor detenido")

        self.runtime_state = {
            "phase": "idle",
            "last_activity": None,
        }

        self.current_phase = "idle"
        self.generation_phase_started = None
        self.prime_phase_started = None
        self.generation_elapsed_final = 0.0
        self.prime_elapsed_final = 0.0
        self.heartbeat_job = None

        self._build_ui()
        self._refresh_plan()

    def _build_ui(self):
        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Generador V2.7 AUTO TURBO — Generación automática por archivos",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        ttk.Label(
            main,
            text=(
                "Configura una sola vez el valor inicial y final, cuántos grupos "
                "de 12 palabras debe producir cada valor y cuántos grupos tendrá "
                "cada archivo. El programa crea todos los TXT automáticamente. "
                "Cuando termina el total correspondiente a un valor, pasa al "
                "siguiente valor (+1) hasta alcanzar el valor final inclusive."
            ),
            wraplength=1180,
            justify="left"
        ).pack(anchor="w", pady=(4, 12))

        # -------------------------------------------------------------
        # Plan de generación
        # -------------------------------------------------------------
        plan = ttk.LabelFrame(
            main,
            text="1. Plan de generación automática",
            padding=10
        )
        plan.pack(fill="x")

        ttk.Label(
            plan,
            text="Valor inicial:"
        ).grid(row=0, column=0, sticky="w")

        start_entry = ttk.Entry(
            plan,
            textvariable=self.start_value_var,
            width=14
        )
        start_entry.grid(
            row=0,
            column=1,
            padx=(8, 22),
            sticky="w"
        )

        ttk.Label(
            plan,
            text="Valor final (inclusive):"
        ).grid(row=0, column=2, sticky="w")

        end_entry = ttk.Entry(
            plan,
            textvariable=self.end_value_var,
            width=14
        )
        end_entry.grid(
            row=0,
            column=3,
            padx=(8, 22),
            sticky="w"
        )

        ttk.Label(
            plan,
            text="Grupos totales por valor:"
        ).grid(row=0, column=4, sticky="w")

        groups_value_entry = ttk.Entry(
            plan,
            textvariable=self.groups_per_value_var,
            width=14
        )
        groups_value_entry.grid(
            row=0,
            column=5,
            padx=(8, 22),
            sticky="w"
        )

        ttk.Label(
            plan,
            text="Grupos por archivo:"
        ).grid(row=0, column=6, sticky="w")

        groups_file_entry = ttk.Entry(
            plan,
            textvariable=self.groups_per_file_var,
            width=14
        )
        groups_file_entry.grid(
            row=0,
            column=7,
            padx=(8, 0),
            sticky="w"
        )

        ttk.Label(
            plan,
            text="Prefijo automático:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(10, 0)
        )

        ttk.Entry(
            plan,
            textvariable=self.prefix_var,
            width=24
        ).grid(
            row=1,
            column=1,
            columnspan=2,
            padx=(8, 22),
            pady=(10, 0),
            sticky="w"
        )

        ttk.Label(
            plan,
            text="CPU para criba final:"
        ).grid(
            row=1,
            column=3,
            sticky="e",
            pady=(10, 0)
        )

        ttk.Spinbox(
            plan,
            from_=self.min_cpu_workers,
            to=self.logical_cpus,
            textvariable=self.cpu_workers_var,
            width=6
        ).grid(
            row=1,
            column=4,
            padx=(8, 8),
            pady=(10, 0),
            sticky="w"
        )

        ttk.Label(
            plan,
            text=(
                f"de {self.logical_cpus} CPU lógicas · "
                f"recomendado {self.default_cpu_workers}"
            )
        ).grid(
            row=1,
            column=5,
            columnspan=3,
            pady=(10, 0),
            sticky="w"
        )

        for variable in (
            self.start_value_var,
            self.end_value_var,
            self.groups_per_value_var,
            self.groups_per_file_var,
            self.prefix_var,
        ):
            variable.trace_add(
                "write",
                lambda *_args: self._refresh_plan()
            )

        # -------------------------------------------------------------
        # Carpeta
        # -------------------------------------------------------------
        folder_frame = ttk.LabelFrame(
            main,
            text="2. Carpeta de destino",
            padding=10
        )
        folder_frame.pack(
            fill="x",
            pady=(12, 0)
        )

        ttk.Entry(
            folder_frame,
            textvariable=self.destination_var,
            state="readonly"
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Button(
            folder_frame,
            text="Seleccionar carpeta…",
            command=self.select_destination
        ).pack(
            side="left",
            padx=(8, 0)
        )

        ttk.Label(
            folder_frame,
            text=(
                "Se creará automáticamente una subcarpeta nueva para "
                "cada ejecución, evitando sobrescribir archivos anteriores."
            )
        ).pack(
            anchor="w",
            side="bottom",
            fill="x",
            pady=(8, 0)
        )

        # -------------------------------------------------------------
        # Resumen del plan
        # -------------------------------------------------------------
        summary = ttk.LabelFrame(
            main,
            text="3. Resumen",
            padding=10
        )
        summary.pack(
            fill="x",
            pady=(12, 0)
        )

        ttk.Label(
            summary,
            textvariable=self.initial_info_var
        ).pack(anchor="w")

        ttk.Label(
            summary,
            textvariable=self.plan_var,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(5, 0))

        # -------------------------------------------------------------
        # Botones
        # -------------------------------------------------------------
        buttons = ttk.Frame(main)
        buttons.pack(
            fill="x",
            pady=(12, 0)
        )

        self.generate_btn = ttk.Button(
            buttons,
            text="INICIAR GENERACIÓN AUTOMÁTICA",
            command=self.on_generate
        )
        self.generate_btn.pack(side="left")

        self.stop_btn = ttk.Button(
            buttons,
            text="Detener",
            command=self.on_stop,
            state="disabled"
        )
        self.stop_btn.pack(
            side="left",
            padx=(8, 0)
        )

        # -------------------------------------------------------------
        # Progreso
        # -------------------------------------------------------------
        progress_frame = ttk.LabelFrame(
            main,
            text="4. Progreso automático",
            padding=10
        )
        progress_frame.pack(
            fill="x",
            pady=(12, 0)
        )

        info = ttk.Frame(progress_frame)
        info.pack(fill="x")

        ttk.Label(
            info,
            text="Valor actual:"
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            info,
            textvariable=self.current_value_var,
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=0,
            column=1,
            padx=(8, 30),
            sticky="w"
        )

        ttk.Label(
            info,
            text="Archivo actual:"
        ).grid(row=0, column=2, sticky="w")

        ttk.Label(
            info,
            textvariable=self.current_file_var
        ).grid(
            row=0,
            column=3,
            padx=(8, 0),
            sticky="w"
        )

        ttk.Label(
            info,
            text="Progreso de este valor:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            info,
            textvariable=self.current_value_progress_var
        ).grid(
            row=1,
            column=1,
            padx=(8, 30),
            pady=(6, 0),
            sticky="w"
        )

        ttk.Label(
            info,
            text="Progreso total:"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            pady=(6, 0)
        )

        ttk.Label(
            info,
            textvariable=self.overall_progress_var
        ).grid(
            row=1,
            column=3,
            padx=(8, 0),
            pady=(6, 0),
            sticky="w"
        )

        ttk.Label(
            progress_frame,
            text="Valor actual"
        ).pack(anchor="w", pady=(10, 2))

        self.value_progress = ttk.Progressbar(
            progress_frame,
            mode="determinate"
        )
        self.value_progress.pack(fill="x")

        ttk.Label(
            progress_frame,
            text="Proceso completo"
        ).pack(anchor="w", pady=(8, 2))

        self.overall_progress = ttk.Progressbar(
            progress_frame,
            mode="determinate"
        )
        self.overall_progress.pack(fill="x")

        ttk.Label(
            progress_frame,
            text="Carpeta creada:"
        ).pack(anchor="w", pady=(8, 0))

        ttk.Label(
            progress_frame,
            textvariable=self.output_dir_var,
            wraplength=1160,
            justify="left"
        ).pack(anchor="w")

        timers = ttk.Frame(progress_frame)
        timers.pack(fill="x", pady=(10, 0))

        ttk.Label(
            timers,
            text="Cronómetro generación:"
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            timers,
            textvariable=self.generation_timer_var,
            font=("Consolas", 11, "bold")
        ).grid(row=0, column=1, padx=(8, 28), sticky="w")

        ttk.Label(
            timers,
            text="Cronómetro primos:"
        ).grid(row=0, column=2, sticky="w")

        ttk.Label(
            timers,
            textvariable=self.prime_timer_var,
            font=("Consolas", 11, "bold")
        ).grid(row=0, column=3, padx=(8, 28), sticky="w")

        ttk.Label(
            timers,
            text="Pulso del motor:"
        ).grid(row=0, column=4, sticky="w")

        ttk.Label(
            timers,
            textvariable=self.engine_heartbeat_var,
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=5, padx=(8, 0), sticky="w")

        ttk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(8, 0))

        # -------------------------------------------------------------
        # Última serie generada
        # -------------------------------------------------------------
        phrase_box = ttk.LabelFrame(
            main,
            text="5. Última serie de 12 palabras generada",
            padding=10
        )
        phrase_box.pack(
            fill="x",
            pady=(12, 8)
        )

        ttk.Entry(
            phrase_box,
            textvariable=self.phrase_var,
            state="readonly"
        ).pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Button(
            phrase_box,
            text="Copiar",
            command=self.copy_phrase
        ).pack(
            side="left",
            padx=(8, 0)
        )

        meta = ttk.Frame(main)
        meta.pack(fill="x", pady=(2, 0))

        ttk.Label(
            meta,
            text="Entropía (hex):"
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            meta,
            textvariable=self.entropy_var
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(8, 20)
        )

        ttk.Label(
            meta,
            text="Checksum:"
        ).grid(row=0, column=2, sticky="w")

        ttk.Label(
            meta,
            textvariable=self.checksum_var
        ).grid(
            row=0,
            column=3,
            sticky="w",
            padx=(8, 20)
        )

        ttk.Label(
            meta,
            text="Frases únicas registradas:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(5, 0)
        )

        ttk.Label(
            meta,
            textvariable=self.count_var
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=(8, 20),
            pady=(5, 0)
        )

    def _parse_plan(self, show_errors=False):
        try:
            start = int(
                self.start_value_var.get().strip()
            )
            end = int(
                self.end_value_var.get().strip()
            )
            groups_per_value = int(
                self.groups_per_value_var.get().strip()
            )
            groups_per_file = int(
                self.groups_per_file_var.get().strip()
            )

            if start < 1:
                raise ValueError(
                    "El valor inicial debe ser positivo."
                )

            if end < start:
                raise ValueError(
                    "El valor final debe ser mayor o igual "
                    "que el valor inicial."
                )

            if groups_per_value < 1:
                raise ValueError(
                    "Los grupos totales por valor deben ser al menos 1."
                )

            if groups_per_file < 1:
                raise ValueError(
                    "Los grupos por archivo deben ser al menos 1."
                )

            return (
                start,
                end,
                groups_per_value,
                groups_per_file
            )

        except Exception as exc:
            if show_errors:
                messagebox.showwarning(
                    "Plan inválido",
                    str(exc)
                )
            return None

    def _refresh_plan(self):
        parsed = self._parse_plan(
            show_errors=False
        )

        if not parsed:
            self.initial_info_var.set(
                "Completa los parámetros con valores enteros válidos."
            )
            self.plan_var.set("")
            return

        (
            start,
            end,
            groups_per_value,
            groups_per_file
        ) = parsed

        local = local_position(start)
        item = self.items[local - 1]
        block = block_number(start)

        self.initial_info_var.set(
            f"Valor inicial {start}: local {local} · "
            f"bloque {block} · palabra «{item.word}» · "
            f"primo base {item.prime}"
        )

        values = end - start + 1
        files_per_value = math.ceil(
            groups_per_value
            / groups_per_file
        )
        total_files = (
            values
            * files_per_value
        )
        total_groups = (
            values
            * groups_per_value
        )

        remainder = (
            groups_per_value
            % groups_per_file
        )

        last_file_text = (
            f"{remainder} grupos en el último archivo"
            if remainder
            else "todos los archivos completos"
        )

        self.plan_var.set(
            f"{values:,} valor(es) · "
            f"{total_groups:,} grupos totales · "
            f"{files_per_value:,} archivo(s) por valor · "
            f"{total_files:,} archivos previstos · "
            f"{last_file_text}"
        )

    def select_destination(self):
        directory = filedialog.askdirectory(
            title="Selecciona la carpeta donde guardar toda la generación"
        )

        if directory:
            self.destination_var.set(
                directory
            )

    @staticmethod
    def _format_elapsed(seconds: float) -> str:
        seconds = max(0, int(seconds))
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _start_heartbeat(self):
        if self.heartbeat_job is not None:
            try:
                self.after_cancel(self.heartbeat_job)
            except Exception:
                pass
            self.heartbeat_job = None

        self._tick_heartbeat()

    def _tick_heartbeat(self):
        now = time.perf_counter()

        if self.current_phase == "generation":
            if self.generation_phase_started is not None:
                elapsed = now - self.generation_phase_started
                self.generation_timer_var.set(
                    self._format_elapsed(elapsed)
                )

            last_activity = self.runtime_state.get("last_activity")

            if last_activity is None:
                self.engine_heartbeat_var.set(
                    "● MOTOR ACTIVO"
                )
            else:
                age = max(0.0, now - last_activity)
                self.engine_heartbeat_var.set(
                    f"● MOTOR ACTIVO · último pulso {age:.1f}s"
                )

        elif self.current_phase == "primes":
            self.generation_timer_var.set(
                self._format_elapsed(
                    self.generation_elapsed_final
                )
            )

            if self.prime_phase_started is not None:
                elapsed = now - self.prime_phase_started
                self.prime_timer_var.set(
                    self._format_elapsed(elapsed)
                )

            last_activity = self.runtime_state.get("last_activity")

            if last_activity is None:
                self.engine_heartbeat_var.set(
                    "● PRIMOS ACTIVOS"
                )
            else:
                age = max(0.0, now - last_activity)
                self.engine_heartbeat_var.set(
                    f"● PRIMOS ACTIVOS · último pulso {age:.1f}s"
                )

        elif self.current_phase == "done":
            self.generation_timer_var.set(
                self._format_elapsed(
                    self.generation_elapsed_final
                )
            )

            self.prime_timer_var.set(
                self._format_elapsed(
                    self.prime_elapsed_final
                )
                if self.prime_elapsed_final > 0
                else "No ejecutado"
            )

            self.engine_heartbeat_var.set(
                "■ PROCESO FINALIZADO"
            )
            self.heartbeat_job = None
            return

        elif self.current_phase == "stopped":
            self.engine_heartbeat_var.set(
                "■ PROCESO DETENIDO"
            )
            self.heartbeat_job = None
            return

        else:
            self.engine_heartbeat_var.set(
                "Motor detenido"
            )
            self.heartbeat_job = None
            return

        self.heartbeat_job = self.after(
            1000,
            self._tick_heartbeat
        )

    def on_generate(self):
        if self.generating:
            return

        parsed = self._parse_plan(
            show_errors=True
        )

        if not parsed:
            return

        destination = (
            self.destination_var.get().strip()
        )

        if not destination:
            messagebox.showwarning(
                "Falta carpeta",
                "Selecciona una carpeta de destino."
            )
            return

        try:
            workers = int(
                self.cpu_workers_var.get()
            )

            if not (
                self.min_cpu_workers
                <= workers
                <= self.logical_cpus
            ):
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "CPU inválida",
                f"Selecciona entre {self.min_cpu_workers} y "
                f"{self.logical_cpus} procesos."
            )
            return

        (
            start,
            end,
            groups_per_value,
            groups_per_file
        ) = parsed

        prefix = self.prefix_var.get().strip()

        values = end - start + 1
        total_groups = (
            values
            * groups_per_value
        )

        if not messagebox.askyesno(
            "Confirmar generación automática",
            f"Valores: {start} → {end} inclusive\n"
            f"Grupos por valor: {groups_per_value:,}\n"
            f"Grupos por archivo: {groups_per_file:,}\n"
            f"Grupos totales: {total_groups:,}\n\n"
            "La interfaz sólo se actualizará por archivo. "
            "El cronómetro y el pulso interno indicarán que "
            "el motor continúa trabajando."
        ):
            return

        self.generating = True
        self.stop_event.clear()

        self.generate_btn.configure(
            state="disabled"
        )
        self.stop_btn.configure(
            state="normal"
        )

        self.current_value_var.set(
            str(start)
        )
        self.current_file_var.set("-")
        self.current_value_progress_var.set(
            f"0 / {groups_per_value:,}"
        )
        self.overall_progress_var.set(
            f"0 / {total_groups:,}"
        )
        self.output_dir_var.set(
            "Creando carpeta de sesión…"
        )

        self.value_progress["maximum"] = max(
            1,
            groups_per_value
        )
        self.value_progress["value"] = 0

        self.overall_progress["maximum"] = max(
            1,
            total_groups
        )
        self.overall_progress["value"] = 0

        # Reinicio de cronómetros.
        self.generation_elapsed_final = 0.0
        self.prime_elapsed_final = 0.0
        self.generation_timer_var.set("00:00:00")
        self.prime_timer_var.set("Pendiente")

        self.runtime_state.clear()
        self.runtime_state.update({
            "phase": "generation",
            "last_activity": time.perf_counter(),
        })

        self.current_phase = "generation"
        self.generation_phase_started = time.perf_counter()
        self.prime_phase_started = None

        self.status_var.set(
            "Generación de archivos en curso…"
        )
        self._start_heartbeat()

        def progress(payload):
            # Ahora sólo se llama al iniciar/completar archivos o valores.
            self.after(
                0,
                lambda p=payload: self._update_progress(
                    p
                )
            )

        def worker():
            try:
                generation_started = (
                    self.generation_phase_started
                    or time.perf_counter()
                )

                result = generate_automatic_range(
                    start_value=start,
                    end_value=end,
                    groups_per_value=groups_per_value,
                    groups_per_file=groups_per_file,
                    destination_dir=Path(destination),
                    prefix=prefix,
                    items=self.items,
                    stop_event=self.stop_event,
                    progress=progress,
                    runtime_state=self.runtime_state,
                )

                generation_elapsed = (
                    time.perf_counter()
                    - generation_started
                )

                self.generation_elapsed_final = (
                    generation_elapsed
                )
                result["generation_elapsed"] = (
                    generation_elapsed
                )
                result["prime_elapsed"] = 0.0

                last_candidate = result[
                    "last_candidate"
                ]

                if (
                    last_candidate is not None
                    and not result["stopped"]
                ):
                    # Fase 2: cálculo de los 12 primos absolutos.
                    prime_started = time.perf_counter()

                    self.prime_phase_started = prime_started
                    self.current_phase = "primes"

                    self.runtime_state.update({
                        "phase": "primes",
                        "last_activity": prime_started,
                    })

                    self.after(
                        0,
                        lambda: self.status_var.set(
                            "ARCHIVOS GENERADOS · "
                            "Calculando los 12 primos absolutos finales…"
                        )
                    )

                    def prime_progress(
                        phase,
                        done,
                        total
                    ):
                        self.runtime_state[
                            "last_activity"
                        ] = time.perf_counter()

                        if total <= 0:
                            return

                        pct = min(
                            100,
                            int(done * 100 / total)
                        )

                        self.after(
                            0,
                            lambda ph=phase, p=pct: self.status_var.set(
                                f"ARCHIVOS GENERADOS · "
                                f"{ph} · {p}% · "
                                f"CPU {workers}/{self.logical_cpus}"
                            )
                        )

                    primes_map = (
                        odd_primes_at_positions_parallel(
                            last_candidate[
                                "absolute_positions"
                            ],
                            workers=workers,
                            progress=prime_progress
                        )
                    )

                    last_candidate[
                        "absolute_primes"
                    ] = [
                        primes_map[g]
                        for g in last_candidate[
                            "absolute_positions"
                        ]
                    ]

                    prime_elapsed = (
                        time.perf_counter()
                        - prime_started
                    )

                    self.prime_elapsed_final = (
                        prime_elapsed
                    )
                    result["prime_elapsed"] = (
                        prime_elapsed
                    )

                total_elapsed = (
                    result["generation_elapsed"]
                    + result["prime_elapsed"]
                )
                result["total_elapsed"] = total_elapsed

                self.after(
                    0,
                    lambda r=result: self._generation_done(
                        r
                    )
                )

            except Exception as exc:
                self.after(
                    0,
                    lambda error=exc: self._generation_error(
                        error
                    )
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()


    def on_stop(self):
        if self.generating:
            self.stop_event.set()
            self.status_var.set(
                "Deteniendo de forma segura al terminar "
                "el grupo actual…"
            )

    def _update_progress(self, payload: dict):
        kind = payload.get("kind")

        session_dir = payload.get(
            "session_dir"
        )

        if session_dir:
            self.output_dir_var.set(
                session_dir
            )

        if kind == "file_start":
            value = payload["value"]
            filename = payload["filename"]

            self.current_value_var.set(
                str(value)
            )
            self.current_file_var.set(
                filename
            )

            self.status_var.set(
                f"Generando archivo {filename} · "
                f"motor activo…"
            )

        elif kind == "file":
            value = payload["value"]
            generated_for_value = payload[
                "generated_for_value"
            ]
            groups_per_value = payload[
                "groups_per_value"
            ]
            generated_total = payload[
                "generated_total"
            ]
            total_groups = payload[
                "total_groups_planned"
            ]
            filepath = payload.get(
                "filepath",
                ""
            )

            self.current_value_var.set(
                str(value)
            )

            if filepath:
                self.current_file_var.set(
                    Path(filepath).name
                )

            # Las barras saltan una vez por archivo completo.
            self.value_progress["maximum"] = max(
                1,
                groups_per_value
            )
            self.value_progress["value"] = (
                generated_for_value
            )

            self.overall_progress["maximum"] = max(
                1,
                total_groups
            )
            self.overall_progress["value"] = (
                generated_total
            )

            self.current_value_progress_var.set(
                f"{generated_for_value:,} / "
                f"{groups_per_value:,}"
            )
            self.overall_progress_var.set(
                f"{generated_total:,} / "
                f"{total_groups:,}"
            )

            pct = (
                generated_total
                * 100.0
                / max(1, total_groups)
            )

            self.status_var.set(
                f"Archivo completado · valor {value} · "
                f"progreso total {pct:.2f}%"
            )

        elif kind == "value":
            value = payload["value"]
            completed_values = payload[
                "completed_values"
            ]
            value_count = payload[
                "value_count"
            ]

            self.status_var.set(
                f"Valor {value} completado · "
                f"{completed_values}/{value_count} "
                f"valores finalizados · "
                f"pasando al siguiente…"
            )


    def _generation_done(
        self,
        result: dict
    ):
        self.generating = False

        self.generate_btn.configure(
            state="normal"
        )
        self.stop_btn.configure(
            state="disabled"
        )

        self.output_dir_var.set(
            result["session_dir"]
        )

        last_candidate = result.get(
            "last_candidate"
        )

        if last_candidate is not None:
            self.current_result = last_candidate
            self.phrase_var.set(
                last_candidate["phrase"]
            )
            self.entropy_var.set(
                last_candidate["entropy_hex"]
            )
            self.checksum_var.set(
                last_candidate["checksum_bits"]
            )
            self.count_var.set(
                str(result["final_db_count"])
            )

        generation_elapsed = float(
            result.get(
                "generation_elapsed",
                0.0
            )
        )
        prime_elapsed = float(
            result.get(
                "prime_elapsed",
                0.0
            )
        )
        total_elapsed = float(
            result.get(
                "total_elapsed",
                generation_elapsed + prime_elapsed
            )
        )

        self.generation_elapsed_final = (
            generation_elapsed
        )
        self.prime_elapsed_final = (
            prime_elapsed
        )

        if result["stopped"]:
            self.current_phase = "stopped"

            self.generation_timer_var.set(
                self._format_elapsed(
                    generation_elapsed
                )
            )
            self.prime_timer_var.set(
                "No ejecutado"
            )

            self.status_var.set(
                f"Proceso detenido · "
                f"{result['generated_total']:,} grupos · "
                f"{result['files_created']:,} archivos."
            )

            messagebox.showinfo(
                "Proceso detenido",
                f"La generación se ha detenido de forma segura.\n\n"
                f"Grupos generados: "
                f"{result['generated_total']:,}\n"
                f"Archivos creados: "
                f"{result['files_created']:,}\n"
                f"Tiempo del generador: "
                f"{self._format_elapsed(generation_elapsed)}\n\n"
                f"Carpeta:\n{result['session_dir']}\n\n"
                f"Manifiesto:\n{result['manifest_path']}"
            )

        else:
            self.current_phase = "done"

            self.value_progress["value"] = (
                result["groups_per_value"]
            )
            self.overall_progress["value"] = (
                result["total_groups_planned"]
            )

            self.generation_timer_var.set(
                self._format_elapsed(
                    generation_elapsed
                )
            )
            self.prime_timer_var.set(
                self._format_elapsed(
                    prime_elapsed
                )
            )

            self.status_var.set(
                f"FINALIZADO · "
                f"{result['generated_total']:,} grupos · "
                f"{result['files_created']:,} archivos"
            )

            messagebox.showinfo(
                "Generación automática finalizada",
                f"Valores completados: "
                f"{result['completed_values']:,} / "
                f"{result['value_count']:,}\n"
                f"Grupos generados: "
                f"{result['generated_total']:,}\n"
                f"Archivos creados: "
                f"{result['files_created']:,}\n\n"
                f"Tiempo generación de archivos: "
                f"{self._format_elapsed(generation_elapsed)}\n"
                f"Tiempo cálculo 12 primos finales: "
                f"{self._format_elapsed(prime_elapsed)}\n"
                f"Tiempo total: "
                f"{self._format_elapsed(total_elapsed)}\n\n"
                f"Carpeta:\n{result['session_dir']}\n\n"
                f"Manifiesto:\n{result['manifest_path']}"
            )

        # Actualiza inmediatamente el estado final de los cronómetros.
        self._tick_heartbeat()


    def _generation_error(
        self,
        exc: Exception
    ):
        self.generating = False

        self.generate_btn.configure(
            state="normal"
        )
        self.stop_btn.configure(
            state="disabled"
        )

        self.current_phase = "stopped"
        self.engine_heartbeat_var.set(
            "■ ERROR / MOTOR DETENIDO"
        )

        self.status_var.set(
            "Error crítico"
        )

        messagebox.showerror(
            "Error",
            f"{type(exc).__name__}: {exc}"
        )

    def copy_phrase(self):
        phrase = self.phrase_var.get().strip()

        if not phrase:
            return

        self.clipboard_clear()
        self.clipboard_append(phrase)
        self.update()

        messagebox.showinfo(
            "Copiado",
            "La última serie se ha copiado "
            "al portapapeles."
        )

def main():
    mp.freeze_support()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
