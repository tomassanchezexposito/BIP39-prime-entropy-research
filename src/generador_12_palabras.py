#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de series de 12 palabras a partir de una posición inicial 1..2048.

Diseño:
- Cada posición 1..2048 se asocia de forma biyectiva a:
    posición -> primo impar -> palabra
- 2048 = 2^11, por lo que cada palabra representa 11 bits.
- Una serie de 12 palabras contiene 132 bits de codificación:
    128 bits de entropía + 4 bits de checksum SHA-256.
- La posición inicial introducida fija los primeros 11 bits.
- Los 117 bits restantes se generan con secrets (CSPRNG del sistema operativo).
- Para una posición inicial fija existen exactamente 2^117 series válidas.
- Sumando las 2048 posiciones iniciales: 2048 * 2^117 = 2^128 series válidas.
- Se guarda únicamente el SHA-256 de cada serie en SQLite para no repetir
  localmente una serie ya emitida por esta instalación. No se guarda la frase.

IMPORTANTE:
Este programa es una implementación experimental basada en los datos del usuario.
No debe considerarse software de custodia ni un generador de cartera auditado.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
import tkinter as tk
from tkinter import ttk, messagebox


APP_NAME = "GeneradorPrimosPalabrasV1"
DATA_FILE = "datos_2048.json"


@dataclass(frozen=True)
class Item:
    position: int
    prime: int
    word: str


def base_dir() -> Path:
    # Compatible con script normal y con empaquetados.
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


def is_prime(n: int) -> bool:
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
    if len(items) != 2048:
        raise ValueError(f"Se esperaban 2048 registros y hay {len(items)}.")
    if [x.position for x in items] != list(range(1, 2049)):
        raise ValueError("Las posiciones deben ser exactamente 1..2048.")
    if len({x.word for x in items}) != 2048:
        raise ValueError("Las 2048 palabras deben ser únicas.")
    primes = [x.prime for x in items]
    if primes != sorted(primes) or len(set(primes)) != 2048:
        raise ValueError("La lista de primos no es estrictamente creciente y única.")
    if any((p % 2 == 0 or not is_prime(p)) for p in primes):
        raise ValueError("Se ha detectado un valor que no es primo impar.")


def db_connect() -> sqlite3.Connection:
    db_path = app_data_dir() / "historial_hashes.db"
    con = sqlite3.connect(db_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS generated (
            phrase_hash TEXT PRIMARY KEY,
            first_position INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    con.commit()
    return con


def checksum4(entropy_bytes: bytes) -> int:
    return hashlib.sha256(entropy_bytes).digest()[0] >> 4


def indexes_from_entropy(entropy_int: int) -> tuple[list[int], int]:
    # ENT=128 bits, CS=4 bits -> 132 bits -> 12 índices de 11 bits.
    entropy_bytes = entropy_int.to_bytes(16, "big")
    cs = checksum4(entropy_bytes)
    combined = (entropy_int << 4) | cs
    indexes = [
        (combined >> (11 * (11 - i))) & 0x7FF
        for i in range(12)
    ]
    return indexes, cs


def phrase_is_valid(indexes: list[int]) -> bool:
    if len(indexes) != 12 or any(not (0 <= i < 2048) for i in indexes):
        return False
    combined = 0
    for idx in indexes:
        combined = (combined << 11) | idx
    cs = combined & 0xF
    entropy_int = combined >> 4
    entropy_bytes = entropy_int.to_bytes(16, "big")
    return cs == checksum4(entropy_bytes)


def generate_series(first_position: int, items: list[Item]) -> dict:
    if not 1 <= first_position <= 2048:
        raise ValueError("La posición inicial debe estar entre 1 y 2048.")

    first_index = first_position - 1  # 11 bits fijados por el usuario

    con = db_connect()
    try:
        while True:
            # Uniforme sobre las 2^117 continuaciones posibles para ese primer índice.
            random_tail = secrets.randbits(117)
            entropy_int = (first_index << 117) | random_tail
            indexes, cs = indexes_from_entropy(entropy_int)

            if indexes[0] != first_index:
                raise RuntimeError("Error interno: el primer índice no coincide.")

            positions = [idx + 1 for idx in indexes]
            selected = [items[idx] for idx in indexes]
            words = [x.word for x in selected]
            primes = [x.prime for x in selected]

            if not phrase_is_valid(indexes):
                raise RuntimeError("Error interno de checksum.")

            phrase = " ".join(words)
            phrase_hash = hashlib.sha256(phrase.encode("utf-8")).hexdigest()

            try:
                con.execute(
                    "INSERT INTO generated(phrase_hash, first_position, created_at) VALUES (?, ?, ?)",
                    (phrase_hash, first_position, datetime.now(timezone.utc).isoformat())
                )
                con.commit()
                break
            except sqlite3.IntegrityError:
                # Duplicado local: se descarta y se genera otro.
                continue

        count = con.execute("SELECT COUNT(*) FROM generated").fetchone()[0]
    finally:
        con.close()

    return {
        "first_position": first_position,
        "entropy_hex": entropy_int.to_bytes(16, "big").hex(),
        "checksum_bits": f"{cs:04b}",
        "positions": positions,
        "primes": primes,
        "words": words,
        "phrase": phrase,
        "local_count": count,
    }


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de 12 palabras — primos / posiciones")
        self.geometry("980x720")
        self.minsize(900, 650)

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

        self._build_ui()
        self._update_initial_info()

    def _build_ui(self):
        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="Generador de serie de 12 palabras", font=("Segoe UI", 18, "bold"))
        title.pack(anchor="w")

        explanation = ttk.Label(
            main,
            text=(
                "Introduce la posición del primer primo (1–2048). "
                "Ese valor fija el primer símbolo de 11 bits; los 117 bits restantes "
                "se generan con entropía criptográfica del sistema. La serie resultante "
                "usa 128 bits de entropía y 4 bits de checksum en su codificación de 12 palabras."
            ),
            wraplength=930,
            justify="left"
        )
        explanation.pack(anchor="w", pady=(4, 12))

        input_frame = ttk.Frame(main)
        input_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(input_frame, text="Posición inicial:").pack(side="left")
        entry = ttk.Entry(input_frame, textvariable=self.position_var, width=10)
        entry.pack(side="left", padx=(8, 8))
        entry.bind("<KeyRelease>", lambda _e: self._update_initial_info())
        entry.bind("<Return>", lambda _e: self.on_generate())

        ttk.Button(input_frame, text="Generar serie", command=self.on_generate).pack(side="left", padx=(0, 12))
        ttk.Label(input_frame, textvariable=self.initial_info_var).pack(side="left")

        table_frame = ttk.Frame(main)
        table_frame.pack(fill="both", expand=True)

        columns = ("n", "position", "prime", "word")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("n", text="#")
        self.tree.heading("position", text="Posición")
        self.tree.heading("prime", text="Número primo")
        self.tree.heading("word", text="Palabra")
        self.tree.column("n", width=55, anchor="center")
        self.tree.column("position", width=100, anchor="center")
        self.tree.column("prime", width=140, anchor="center")
        self.tree.column("word", width=260, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

        phrase_box = ttk.LabelFrame(main, text="Serie de 12 palabras", padding=10)
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
        ttk.Label(meta, text="Series únicas registradas localmente:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        ttk.Label(meta, textvariable=self.count_var).grid(row=1, column=1, sticky="w", padx=(8, 20), pady=(5, 0))

        warning = ttk.Label(
            main,
            text=(
                "Nota: con una posición inicial fija hay 2^117 continuaciones válidas. "
                "El universo total de las 2048 posiciones iniciales es 2^128. "
                "La aplicación evita repeticiones respecto de su historial local; "
                "no puede garantizar unicidad global entre equipos desconectados."
            ),
            wraplength=930,
            justify="left"
        )
        warning.pack(anchor="w", pady=(10, 0))

    def _parse_position(self) -> int | None:
        try:
            p = int(self.position_var.get().strip())
            if 1 <= p <= 2048:
                return p
        except ValueError:
            pass
        return None

    def _update_initial_info(self):
        p = self._parse_position()
        if p is None:
            self.initial_info_var.set("Introduce un entero entre 1 y 2048")
            return
        item = self.items[p - 1]
        self.initial_info_var.set(f"Primo {item.prime} · palabra «{item.word}»")

    def on_generate(self):
        p = self._parse_position()
        if p is None:
            messagebox.showwarning("Posición inválida", "Introduce una posición entre 1 y 2048.")
            return
        try:
            result = generate_series(p, self.items)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, (pos, prime, word) in enumerate(
            zip(result["positions"], result["primes"], result["words"]), start=1
        ):
            self.tree.insert("", "end", values=(i, pos, prime, word))

        self.phrase_var.set(result["phrase"])
        self.entropy_var.set(result["entropy_hex"])
        self.checksum_var.set(result["checksum_bits"])
        self.count_var.set(str(result["local_count"]))

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
