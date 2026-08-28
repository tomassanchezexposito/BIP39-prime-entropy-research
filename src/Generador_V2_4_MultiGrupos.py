#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador V2.4: serie infinita creciente + multi-grupos de 12 palabras.

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
almacenándolas en un archivo de texto secuencialmente. El motor matemático agrupa
los cálculos de la criba de primos en un solo barrido para máxima eficiencia.
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
from tkinter import ttk, messagebox, filedialog


APP_NAME = "GeneradorPrimosPalabrasV24FiltroLinealTotal"
DATA_FILE = "datos_2048.json"
BLOCK = 2048

WORD_COUNT = 12

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
    db_path = app_data_dir() / "historial_hashes.db"
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
    m = n + 1
    small = [2, 3, 5, 7, 11, 13]
    if m < len(small):
        return small[m] + 10
    x = float(m)
    return int(math.ceil(x * (math.log(x) + math.log(math.log(x))))) + 32


def odd_primes_at_positions(target_positions: list[int], progress=None) -> dict[int, int]:
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
    if first_absolute < 1:
        raise ValueError("La posición absoluta inicial debe ser un entero positivo.")

    first_local = local_position(first_absolute)
    first_index = first_local - 1

    con = db_connect()
    try:
        while True:
            random_tail = secrets.randbits(117)
            entropy_int = (first_index << 117) | random_tail
            indexes, cs = indexes_from_entropy(entropy_int)
            if indexes[0] != first_index:
                raise RuntimeError("Error interno: el primer índice no coincide.")
            if not phrase_is_valid(indexes):
                raise RuntimeError("Error interno de checksum.")

            local_positions = [idx + 1 for idx in indexes]

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
        self.title("Generador V2.4 — Infinita creciente · Multi-Grupos")
        self.geometry("1180x820")
        self.minsize(1050, 750)

        try:
            self.items = load_items()
        except Exception as exc:
            messagebox.showerror("Error de datos", str(exc))
            self.destroy()
            return

        self.position_var = tk.StringVar(value="1")
        self.num_groups_var = tk.StringVar(value="1")
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

        ttk.Label(
            main,
            text="Generador V2.4 — Serie infinita creciente · Multi-Grupos",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        explanation = ttk.Label(
            main,
            text=(
                "Introduce una posición ABSOLUTA y la CANTIDAD de grupos de 12 palabras que deseas generar. "
                "Cada grupo sucesivo tomará como inicio la posición absoluta siguiente al final del grupo anterior, "
                "garantizando un avance estricto e infinito sin romper el flujo entrópico. Se volcarán todas las frases, "
                "línea por línea, en un archivo de texto de tu elección, asegurando un proceso de alta eficiencia "
                "mediante la agrupación del cómputo de criba de primos segmentada."
            ),
            wraplength=1135,
            justify="left"
        )
        explanation.pack(anchor="w", pady=(4, 10))

        input_frame = ttk.Frame(main)
        input_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(input_frame, text="Posición absoluta inicial:").pack(side="left")
        entry = ttk.Entry(input_frame, textvariable=self.position_var, width=15)
        entry.pack(side="left", padx=(8, 8))
        entry.bind("<KeyRelease>", lambda _e: self._update_initial_info())
        entry.bind("<Return>", lambda _e: self.on_generate())

        ttk.Label(input_frame, text="Grupos a generar:").pack(side="left", padx=(15, 5))
        spin_groups = ttk.Spinbox(input_frame, from_=1, to=1000000, textvariable=self.num_groups_var, width=8)
        spin_groups.pack(side="left", padx=(0, 12))

        self.generate_btn = ttk.Button(input_frame, text="Generar y Guardar", command=self.on_generate)
        self.generate_btn.pack(side="left", padx=(0, 12))
        ttk.Label(input_frame, textvariable=self.initial_info_var).pack(side="left")

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
            "n": 45, "local": 100, "baseprime": 105, "absolute": 145,
            "block": 80, "absprime": 145, "word": 190,
        }
        for c in columns:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="center" if c != "word" else "w")
        self.tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

        phrase_box = ttk.LabelFrame(main, text="Última serie de 12 palabras generada", padding=10)
        phrase_box.pack(fill="x", pady=(12, 8))
        phrase_entry = ttk.Entry(phrase_box, textvariable=self.phrase_var, state="readonly")
        phrase_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(phrase_box, text="Copiar", command=self.copy_phrase).pack(side="left", padx=(8, 0))

        meta = ttk.Frame(main)
        meta.pack(fill="x", pady=(2, 0))
        ttk.Label(meta, text="Entropía (hex):").grid(row=0, column=0, sticky="w")
        ttk.Label(meta, textvariable=self.entropy_var).grid(row=0, column=1, sticky="w", padx=(8, 20))
        ttk.Label(meta, text="Checksum:").grid(row=0, column=2, sticky="w")
        ttk.Label(meta, textvariable=self.checksum_var).grid(row=0, column=3, sticky="w", padx=(8, 20))
        ttk.Label(meta, text="Frases únicas registradas localmente:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        ttk.Label(meta, textvariable=self.count_var).grid(row=1, column=1, sticky="w", padx=(8, 20), pady=(5, 0))
        ttk.Label(meta, text="Estado:").grid(row=1, column=2, sticky="w", pady=(5, 0))
        ttk.Label(meta, textvariable=self.status_var).grid(row=1, column=3, sticky="w", padx=(8, 20), pady=(5, 0))

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
            n_groups = int(self.num_groups_var.get())
            if n_groups < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Cantidad inválida", "Introduce un número válido de grupos a generar.")
            return

        out_filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar archivo de secuencias"
        )
        if not out_filepath:
            return

        self.generating = True
        self.generate_btn.configure(state="disabled")
        self.status_var.set("Iniciando generación...")

        def progress(done, total):
            if total > 0:
                pct = min(100, int(done * 100 / total))
                self.after(0, lambda: self.status_var.set(f"Calculando primos en lote… {pct}%"))

        def worker():
            try:
                candidates = []
                current_abs = first_absolute
                
                self.after(0, lambda: self.status_var.set("Generando candidatos criptográficos..."))
                
                for i in range(n_groups):
                    cand = build_candidate(current_abs, self.items)
                    candidates.append(cand)
                    # El siguiente grupo tomará la posición absoluta inmediatamente posterior 
                    # a la que finalizó el grupo anterior, perpetuando la expansión.
                    current_abs = cand["absolute_positions"][-1] + 1
                    
                    if i % max(1, n_groups // 20) == 0:
                        pct = int((i / n_groups) * 100)
                        self.after(0, lambda p=pct: self.status_var.set(f"Generando secuencias… {p}%"))

                all_absolute_positions = []
                for c in candidates:
                    all_absolute_positions.extend(c["absolute_positions"])

                self.after(0, lambda: self.status_var.set("Calculando matriz de primos (esto puede llevar su tiempo)..."))
                primes_map = odd_primes_at_positions(all_absolute_positions, progress=progress)

                for c in candidates:
                    c["absolute_primes"] = [primes_map[g] for g in c["absolute_positions"]]

                self.after(0, lambda: self.status_var.set("Volcando poder al archivo..."))
                with open(out_filepath, "w", encoding="utf-8") as f:
                    for i, c in enumerate(candidates):
                        f.write(c["phrase"])
                        if i < len(candidates) - 1:
                            f.write("\n")
                
                self.after(0, lambda: self._display_result(candidates[-1], out_filepath, n_groups))
            except Exception as exc:
                self.after(0, lambda e=exc: self._generation_error(e))

        threading.Thread(target=worker, daemon=True).start()

    def _generation_error(self, exc: Exception):
        self.generating = False
        self.generate_btn.configure(state="normal")
        self.status_var.set("Error crítico")
        messagebox.showerror("Error", str(exc))

    def _display_result(self, result: dict, filepath: str, count: int):
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
                    result["absolute_primes"][i],
                    result["words"][i],
                )
            )

        self.phrase_var.set(result["phrase"])
        self.entropy_var.set(result["entropy_hex"])
        self.checksum_var.set(result["checksum_bits"])
        self.count_var.set(str(result["local_count"]))
        self.status_var.set(f"Operación finalizada — {count} grupo(s) exportado(s)")
        self.generating = False
        self.generate_btn.configure(state="normal")
        
        messagebox.showinfo("Proceso Dominado", f"Se han forjado y volcado {count} grupos de 12 palabras en:\n\n{filepath}")

    def copy_phrase(self):
        phrase = self.phrase_var.get().strip()
        if not phrase:
            return
        self.clipboard_clear()
        self.clipboard_append(phrase)
        self.update()
        messagebox.showinfo("Copiado", "La última serie de 12 palabras está bajo tu control.")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
