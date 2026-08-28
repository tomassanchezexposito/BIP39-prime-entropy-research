#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GENERADOR V3.0 — SERIE INFINITA · FILTRO LINEAL TOTAL REFORZADO
=================================================================

OBJETIVO
--------
Genera 12 palabras usando una serie INFINITA de posiciones de números primos.

La posición LOCAL se cicla dentro de 1..2048, pero la posición ABSOLUTA
puede crecer infinitamente. Esto asegura que la serie de primos siempre avance.

ENTROPÍA
--------
- 128 bits de entropía + 4 bits de checksum SHA-256.
- 2048 símbolos base para mapeo local (ciclan).
- Primera posición absoluta elegida por el usuario.
- Generación criptográfica del resto mediante secrets.

ARQUITECTURA
------------
Regla: gₙ₊₁ es la menor posición absoluta > gₙ que tenga posición local
(gₙ₊₁ mod 2048) igual a la generada por entropía.

Ejemplo:
    g₁ = 1830 (local = 1830)
    Entropía genera local_next = 500
    g₂ = 2548 (porque 2548 mod 2048 = 500 y 2548 > 1830)

FILTRO REFORZADO V3.0
---------------------
Rechazo de:
1. Progresión de paso fijo (módulo 2048)
2. Orden estrictamente ASC o DESC (en posiciones locales)
3. Secuencias consecutivas locales (rango 12 posiciones consecutivas)
4. Patrones lineales en posiciones locales con wrap-around

La serie ABSOLUTA siempre es estrictamente creciente por construcción.
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
import tkinter as tk
from tkinter import ttk, messagebox


APP_NAME = "GeneradorPrimosV30InfinitaFiltroTotalReforzado"
DATA_FILE = "datos_2048.json"
BLOCK = 2048
WORD_COUNT = 12


# ============================================================================
# FILTRO ESTRUCTURAL V3.0 — SERIE INFINITA CON RECHAZO TOTAL DE LINEALES
# ============================================================================

def _forward_distance(a: int, b: int) -> int:
    """Distancia hacia delante módulo 2048."""
    return (b - a) % BLOCK


def _backward_distance(a: int, b: int) -> int:
    """Distancia hacia atrás módulo 2048."""
    return (a - b) % BLOCK


def is_fixed_step_progression(positions: list[int]) -> bool:
    """Detecta progresión de paso fijo módulo 2048."""
    if len(positions) != WORD_COUNT:
        return False
    step = (positions[1] - positions[0]) % BLOCK
    return all(
        (positions[i + 1] - positions[i]) % BLOCK == step
        for i in range(WORD_COUNT - 1)
    )


def is_ordered_with_arbitrary_gaps(positions: list[int]) -> bool:
    """
    Detecta recorrido lineal ASC o DESC con cualquier separación.
    Permite como máximo un cruce del borde.
    """
    if len(positions) != WORD_COUNT:
        return False
    if len(set(positions)) != WORD_COUNT:
        return False
    
    forward = [
        _forward_distance(positions[i], positions[i + 1])
        for i in range(WORD_COUNT - 1)
    ]
    backward = [
        _backward_distance(positions[i], positions[i + 1])
        for i in range(WORD_COUNT - 1)
    ]
    
    ascending = all(d > 0 for d in forward) and sum(forward) < BLOCK
    descending = all(d > 0 for d in backward) and sum(backward) < BLOCK
    return ascending or descending


def is_consecutive_local_range(positions: list[int]) -> bool:
    """
    Detecta si las 12 posiciones LOCALES forman un rango consecutivo
    en el ciclo 1..2048.
    
    Para serie INFINITA con coordenadas locales, esto significa:
    {5, 6, 7, ..., 16} o cualquier permutación de un rango de 12 consecutivos.
    """
    if len(positions) != WORD_COUNT:
        return False
    if len(set(positions)) != WORD_COUNT:
        return False
    
    # Verificar en orden directo (linear)
    sorted_pos = sorted(positions)
    is_linear = all(sorted_pos[i] == sorted_pos[i - 1] + 1 for i in range(1, WORD_COUNT))
    if is_linear:
        return True
    
    # Verificar con wrap-around (ej: 2045, 2046, 2047, 2048, 1, 2, ..., 10)
    # Buscar la posición mínima y verificar si es un rango consecutivo wrapping
    min_pos = min(positions)
    max_pos = max(positions)
    
    # Si max_pos - min_pos == 11, entonces es un rango lineal de 12
    if max_pos - min_pos == 11:
        return True
    
    # Caso wrap: mínimo valores pequeños y máximo valores grandes
    # Pero la diferencia max - min NO es 11 porque hay wrap
    # En este caso, el rango es: [max_pos, 2048] ∪ [1, min_pos]
    # Longitud total: (2048 - max_pos + 1) + min_pos = 2049 - max_pos + min_pos
    # Queremos que sea 12
    if 2049 - max_pos + min_pos == 12:
        # Verificar que todos los valores estén en ese rango
        expected_set = set(range(max_pos, BLOCK + 1)) | set(range(1, min_pos + 1))
        if len(expected_set) == WORD_COUNT and expected_set == set(positions):
            return True
    
    return False


def is_forbidden_linear_pattern(positions: list[int]) -> bool:
    """
    Maestro de filtro para serie INFINITA.
    
    RECHAZA:
    1. Progresión de paso fijo (módulo 2048)
    2. Orden estrictamente ASC o DESC (cualquier separación, máximo 1 cruce)
    3. Rango consecutivo de 12 posiciones (en cualquier orden)
    """
    if len(positions) != WORD_COUNT:
        return False
    
    # Progresión de paso fijo
    if is_fixed_step_progression(positions):
        return True
    
    # Orden ASC/DESC con separaciones arbitrarias
    if is_ordered_with_arbitrary_gaps(positions):
        return True
    
    # Rango consecutivo de 12 posiciones (incluyendo wrap-around)
    if is_consecutive_local_range(positions):
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
    """Carga los 2048 ítems base."""
    path = base_dir() / DATA_FILE
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra {DATA_FILE} junto a la aplicación.")
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = [Item(int(x["position"]), int(x["prime"]), str(x["word"])) for x in raw["items"]]
    validate_items(items)
    return items


def is_prime_small(n: int) -> bool:
    """Verificación simple de primalidad."""
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
    """Valida la estructura de los 2048 ítems."""
    if len(items) != BLOCK:
        raise ValueError(f"Se esperaban {BLOCK} registros.")
    if [x.position for x in items] != list(range(1, BLOCK + 1)):
        raise ValueError("Las posiciones deben ser 1..2048.")
    if len({x.word for x in items}) != BLOCK:
        raise ValueError("Las palabras deben ser únicas.")
    primes = [x.prime for x in items]
    if primes != sorted(primes) or len(set(primes)) != BLOCK:
        raise ValueError("Los primos no son estrictamente crecientes y únicos.")
    if any((p % 2 == 0 or not is_prime_small(p)) for p in primes):
        raise ValueError("Se detectó un primo no válido (debe ser impar).")


def local_position(absolute_pos: int) -> int:
    """Convierte posición absoluta a local (1..2048)."""
    if absolute_pos < 1:
        raise ValueError("La posición absoluta debe ser positiva.")
    return ((absolute_pos - 1) % BLOCK) + 1


def block_number(absolute_pos: int) -> int:
    """Número de bloque (0 para 1..2048, 1 para 2049..4096, etc.)."""
    if absolute_pos < 1:
        raise ValueError("La posición absoluta debe ser positiva.")
    return (absolute_pos - 1) // BLOCK


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


def lift_local_series(first_absolute: int, local_positions: list[int]) -> list[int]:
    """Eleva 12 posiciones locales a posiciones absolutas crecientes."""
    if len(local_positions) != 12:
        raise ValueError("Se esperaban 12 posiciones locales.")
    if local_positions[0] != local_position(first_absolute):
        raise ValueError("La primera posición local no corresponde.")
    absolute = [first_absolute]
    for p in local_positions[1:]:
        absolute.append(lift_after(absolute[-1], p))
    if any(b <= a for a, b in zip(absolute, absolute[1:])):
        raise RuntimeError("Error interno: serie no estrictamente creciente.")
    return absolute


def db_connect() -> sqlite3.Connection:
    """Conecta a BD de historial."""
    db_path = app_data_dir() / "historial_hashes_v3_infinita.db"
    con = sqlite3.connect(db_path)
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
    """Checksum de 4 bits."""
    return hashlib.sha256(entropy_bytes).digest()[0] >> 4


def indexes_from_entropy(entropy_int: int) -> tuple[list[int], int]:
    """Extrae 12 índices y checksum de entropía."""
    entropy_bytes = entropy_int.to_bytes(16, "big")
    cs = checksum4(entropy_bytes)
    combined = (entropy_int << 4) | cs
    indexes = [
        (combined >> (11 * (11 - i))) & 0x7FF
        for i in range(12)
    ]
    return indexes, cs


def phrase_is_valid(indexes: list[int]) -> bool:
    """Valida índices contra checksum."""
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
    """Criba de Eratóstenes hasta limit."""
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
    """Cota superior para el primo impar en posición n."""
    if n < 1:
        raise ValueError("La posición debe ser positiva.")
    m = n + 1
    small = [2, 3, 5, 7, 11, 13]
    if m < len(small):
        return small[m] + 10
    x = float(m)
    return int(math.ceil(x * (math.log(x) + math.log(math.log(x))))) + 32


def odd_primes_at_positions(target_positions: list[int], progress=None) -> dict[int, int]:
    """
    Devuelve {posición_absoluta: primo_impar} usando criba segmentada.
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


def build_candidate(first_absolute: int, items: list[Item]) -> dict:
    """Construye una frase válida con serie infinita."""
    if first_absolute < 1:
        raise ValueError("La posición absoluta inicial debe ser positiva.")
    
    first_local = local_position(first_absolute)
    first_index = first_local - 1
    
    con = db_connect()
    try:
        while True:
            random_tail = secrets.randbits(117)
            entropy_int = (first_index << 117) | random_tail
            indexes, cs = indexes_from_entropy(entropy_int)
            
            if indexes[0] != first_index:
                raise RuntimeError("Error interno: primer índice no coincide.")
            if not phrase_is_valid(indexes):
                raise RuntimeError("Error interno de checksum.")
            
            local_positions = [idx + 1 for idx in indexes]
            
            # FILTRO V3.0 REFORZADO
            if is_forbidden_linear_pattern(local_positions):
                continue
            
            selected = [items[idx] for idx in indexes]
            words = [x.word for x in selected]
            base_primes = [x.prime for x in selected]
            phrase = " ".join(words)
            phrase_hash = hashlib.sha256(phrase.encode("utf-8")).hexdigest()
            
            try:
                con.execute(
                    "INSERT INTO generated(phrase_hash, first_absolute_position, created_at) VALUES (?, ?, ?)",
                    (phrase_hash, str(first_absolute), datetime.now(timezone.utc).isoformat())
                )
                con.commit()
                break
            except sqlite3.IntegrityError:
                continue
        
        count = con.execute("SELECT COUNT(*) FROM generated").fetchone()[0]
    finally:
        con.close()
    
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
        "local_count": count,
    }


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador V3.0 — Serie Infinita · Filtro Lineal Total Reforzado")
        self.geometry("1150x800")
        self.minsize(1050, 700)
        
        try:
            self.items = load_items()
        except Exception as exc:
            messagebox.showerror("Error de datos", str(exc))
            self.destroy()
            return
        
        self.position_var = tk.StringVar(value="1")
        self.initial_info_var = tk.StringVar()
        self.entropy_var = tk.StringVar()
        self.checksum_var = tk.StringVar()
        self.count_var = tk.StringVar()
        self.phrase_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Listo")
        self.current_result = None
        self.generating = False
        
        self._build_ui()
        self._update_initial_info()
    
    def _build_ui(self):
        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)
        
        title = ttk.Label(
            main,
            text="Generador V3.0 — Serie Infinita · Filtro Lineal Total Reforzado",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        explanation = ttk.Label(
            main,
            text=(
                "Genera 12 palabras con serie INFINITA de números primos. "
                "Introduce una posición absoluta inicial (entero positivo). "
                "Las posiciones locales ciclan 1–2048, pero las posiciones absolutas siempre avanzan. "
                "Filtro lineal total reforzado: rechaza orden ASC/DESC, paso fijo, "
                "y secuencias de 12 posiciones consecutivas (con wrap-around)."
            ),
            wraplength=1100,
            justify="left"
        )
        explanation.pack(anchor="w", pady=(0, 8))
        
        input_frame = ttk.Frame(main)
        input_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(input_frame, text="Posición absoluta inicial:").pack(side="left")
        entry = ttk.Entry(input_frame, textvariable=self.position_var, width=18)
        entry.pack(side="left", padx=(8, 8))
        entry.bind("<KeyRelease>", lambda _: self._update_initial_info())
        entry.bind("<Return>", lambda _: self.on_generate())
        
        self.generate_btn = ttk.Button(input_frame, text="Generar 12 palabras", command=self.on_generate)
        self.generate_btn.pack(side="left", padx=(0, 12))
        ttk.Label(input_frame, textvariable=self.initial_info_var).pack(side="left")
        
        table_frame = ttk.Frame(main)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        columns = ("n", "local", "baseprime", "absolute", "block", "word")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {
            "n": "#",
            "local": "Posición local",
            "baseprime": "Primo base",
            "absolute": "Posición absoluta",
            "block": "Bloque",
            "word": "Palabra",
        }
        widths = {
            "n": 45,
            "local": 95,
            "baseprime": 105,
            "absolute": 140,
            "block": 75,
            "word": 190,
        }
        for c in columns:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="center" if c != "word" else "w")
        self.tree.pack(side="left", fill="both", expand=True)
        
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)
        
        phrase_frame = ttk.LabelFrame(main, text="Serie de 12 palabras", padding=10)
        phrase_frame.pack(fill="x", pady=(0, 8))
        phrase_entry = ttk.Entry(phrase_frame, textvariable=self.phrase_var, state="readonly")
        phrase_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(phrase_frame, text="Copiar", command=self.copy_phrase).pack(side="left", padx=(8, 0))
        
        meta = ttk.Frame(main)
        meta.pack(fill="x")
        ttk.Label(meta, text="Entropía (hex):").grid(row=0, column=0, sticky="w")
        ttk.Label(meta, textvariable=self.entropy_var).grid(row=0, column=1, sticky="w", padx=(8, 20))
        ttk.Label(meta, text="Checksum:").grid(row=0, column=2, sticky="w")
        ttk.Label(meta, textvariable=self.checksum_var).grid(row=0, column=3, sticky="w", padx=(8, 20))
        ttk.Label(meta, text="Frases únicas registradas:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        ttk.Label(meta, textvariable=self.count_var).grid(row=1, column=1, sticky="w", padx=(8, 20), pady=(5, 0))
        ttk.Label(meta, text="Estado:").grid(row=1, column=2, sticky="w", pady=(5, 0))
        ttk.Label(meta, textvariable=self.status_var).grid(row=1, column=3, sticky="w", padx=(8, 20), pady=(5, 0))
        
        note = ttk.Label(
            main,
            text=(
                "Regla infinita: gₙ₊₁ es la menor posición absoluta > gₙ con posición local "
                "generada por entropía. Las posiciones absolutas y primos siempre avanzan. "
                "Filtro lineal total reforzado activo."
            ),
            wraplength=1100,
            justify="left"
        )
        note.pack(anchor="w", pady=(8, 0))
    
    def _parse_absolute_position(self) -> int | None:
        try:
            p = int(self.position_var.get().strip())
            if p >= 1:
                return p
        except ValueError:
            pass
        return None
    
    def _update_initial_info(self):
        g = self._parse_absolute_position()
        if g is None:
            self.initial_info_var.set("Introduce un entero positivo")
            return
        lp = local_position(g)
        item = self.items[lp - 1]
        b = block_number(g)
        self.initial_info_var.set(
            f"local {lp} · bloque {b} · palabra «{item.word}» · primo base {item.prime}"
        )
    
    def on_generate(self):
        if self.generating:
            return
        first_absolute = self._parse_absolute_position()
        if first_absolute is None:
            messagebox.showwarning("Posición inválida", "Introduce una posición absoluta entera y positiva.")
            return
        
        try:
            candidate = build_candidate(first_absolute, self.items)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        
        self.generating = True
        self.generate_btn.configure(state="disabled")
        self.status_var.set("Calculando primos absolutos…")
        
        def progress(done, total):
            if total > 0:
                pct = min(100, int(done * 100 / total))
                self.after(0, lambda: self.status_var.set(f"Calculando primos… {pct}%"))
        
        def worker():
            try:
                primes_map = odd_primes_at_positions(candidate["absolute_positions"], progress=progress)
                absolute_primes = [primes_map[g] for g in candidate["absolute_positions"]]
                candidate["absolute_primes"] = absolute_primes
                self.after(0, lambda: self._display_result(candidate))
            except Exception as exc:
                self.after(0, lambda: self._generation_error(exc))
        
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
        
        for i in range(12):
            self.tree.insert(
                "", "end",
                values=(
                    i + 1,
                    result["local_positions"][i],
                    result["base_primes"][i],
                    result["absolute_positions"][i],
                    result["blocks"][i],
                    result["words"][i],
                )
            )
        
        self.phrase_var.set(result["phrase"])
        self.entropy_var.set(result["entropy_hex"])
        self.checksum_var.set(result["checksum_bits"])
        self.count_var.set(str(result["local_count"]))
        self.status_var.set("Listo — Serie infinita · Filtro total reforzado")
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
