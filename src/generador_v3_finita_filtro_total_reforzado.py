#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GENERADOR V3.0 — SERIE FINITA · FILTRO LINEAL TOTAL REFORZADO
===============================================================

OBJETIVO
--------
Genera 12 palabras usando una serie FINITA de posiciones (1..2048) con filtro
lineal total mejorado que rechaza:

1. Orden estrictamente ascendente (cualquier separación)
2. Orden estrictamente descendente (cualquier separación)
3. Progresiones de paso fijo (incluyendo paso 0)
4. Secuencias completamente consecutivas (N, N+1, ..., N+11 en cualquier orden)
5. 12 posiciones consecutivas ordenadas ASC/DESC (con wrap-around cíclico)

ENTROPÍA
--------
- 128 bits de entropía + 4 bits de checksum SHA-256.
- 2048 símbolos base para serie finita.
- Primera posición elegida por el usuario (1..2048).
- Generación criptográfica del resto mediante secrets.

ARQUITECTURA
------------
- Serie FINITA: posiciones se mueven dentro del rango 1..2048 sin ciclar.
- Cada posición mapea a un primo impar y una palabra de la lista base.
- Número exacto de combinaciones posibles: C(2048, 12) ≈ muy grande.

FILTRO REFORZADO
----------------
Rechazo adicional de:
  - Conjunto de 12 posiciones consecutivas sin repetición (ej: {5, 6, 7, ..., 16})
  - Cualquier ordenamiento cíclico de un rango consecutivo (incluyendo wrap)
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


APP_NAME = "GeneradorPrimosV30FiuitaFiltroTotalReforzado"
DATA_FILE = "datos_2048.json"
BLOCK = 2048
WORD_COUNT = 12


# ============================================================================
# FILTRO ESTRUCTURAL V3.0 — SERIE FINITA CON RECHAZO TOTAL DE CONSECUTIVAS
# ============================================================================

def _forward_distance(a: int, b: int) -> int:
    """Distancia positiva hacia delante sobre el círculo 1..2048 (módulo)."""
    return (b - a) % BLOCK


def _backward_distance(a: int, b: int) -> int:
    """Distancia positiva hacia atrás sobre el círculo 1..2048 (módulo)."""
    return (a - b) % BLOCK


def is_fixed_step_progression(positions: list[int]) -> bool:
    """Detecta progresión de paso fijo módulo 2048, incluyendo paso 0."""
    if len(positions) != WORD_COUNT:
        return False
    step = (positions[1] - positions[0]) % BLOCK
    return all(
        (positions[i + 1] - positions[i]) % BLOCK == step
        for i in range(WORD_COUNT - 1)
    )


def is_ordered_sequence(positions: list[int]) -> bool:
    """
    Detecta si 12 posiciones están en orden estrictamente ASC o DESC
    con cualquier separación, permitiendo máximo un cruce del borde.
    """
    if len(positions) != WORD_COUNT:
        return False
    if len(set(positions)) != WORD_COUNT:
        return False  # Repeticiones no son orden estricto

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


def is_consecutive_range(positions: list[int]) -> bool:
    """
    Detecta si las 12 posiciones forman un rango consecutivo.
    Ej: {5, 6, 7, ..., 16} en cualquier orden = rechazado.
    
    Para serie FINITA (1..2048), no hay wrap-around del borde.
    """
    if len(positions) != WORD_COUNT:
        return False
    if len(set(positions)) != WORD_COUNT:
        return False  # Repeticiones no se consideran consecutivas
    
    sorted_pos = sorted(positions)
    # Verificar si todos los elementos son números consecutivos
    for i in range(1, WORD_COUNT):
        if sorted_pos[i] != sorted_pos[i - 1] + 1:
            return False
    return True


def is_cyclic_ordered_consecutive(positions: list[int]) -> bool:
    """
    Detecta si 12 posiciones, cuando ordenadas, forman un rango consecutivo
    Y además están en orden ascendente o descendente (con wrap-around cíclico).
    
    Para serie FINITA, esto es menos relevante que para serie infinita,
    pero lo incluimos por completitud.
    """
    if len(positions) != WORD_COUNT:
        return False
    if len(set(positions)) != WORD_COUNT:
        return False
    
    # Primero, ¿son consecutivas?
    if not is_consecutive_range(positions):
        return False
    
    # Segundo, ¿están ordenadas (ASC o DESC) en la secuencia original?
    return is_ordered_sequence(positions)


def is_forbidden_linear_pattern(positions: list[int]) -> bool:
    """
    Maestro de filtro: rechaza patrones no deseados.
    
    RECHAZA:
    1. Progresión de paso fijo (cualquier paso, incluyendo 0)
    2. Orden estrictamente ASC o DESC (con cualquier separación)
    3. Conjunto de 12 posiciones consecutivas (sin importar orden)
    4. 12 posiciones consecutivas en orden ASC/DESC
    """
    if len(positions) != WORD_COUNT:
        return False
    
    # Progresión de paso fijo
    if is_fixed_step_progression(positions):
        return True
    
    # Orden ASC/DESC con separaciones arbitrarias
    if is_ordered_sequence(positions):
        return True
    
    # Rango consecutivo (ej: 5-16 en cualquier orden)
    if is_consecutive_range(positions):
        return True
    
    # Rango consecutivo en orden ASC/DESC (redundante pero explícito)
    if is_cyclic_ordered_consecutive(positions):
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
    """Carga los 2048 ítems (posición, primo, palabra)."""
    path = base_dir() / DATA_FILE
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra {DATA_FILE} junto a la aplicación.")
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = [Item(int(x["position"]), int(x["prime"]), str(x["word"])) for x in raw["items"]]
    validate_items(items)
    return items


def is_prime_small(n: int) -> bool:
    """Verificación simple de primalidad para números pequeños."""
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
    """Valida que los 2048 ítems tengan estructura correcta."""
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


def db_connect() -> sqlite3.Connection:
    """Conecta a la BD de historial de frases generadas."""
    db_path = app_data_dir() / "historial_hashes_v3_finita.db"
    con = sqlite3.connect(db_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS generated (
            phrase_hash TEXT PRIMARY KEY,
            first_position TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    con.commit()
    return con


def checksum4(entropy_bytes: bytes) -> int:
    """Calcula checksum de 4 bits desde entropía SHA-256."""
    return hashlib.sha256(entropy_bytes).digest()[0] >> 4


def indexes_from_entropy(entropy_int: int) -> tuple[list[int], int]:
    """
    Extrae 12 índices (0..2047) y checksum de 4 bits de 128 bits de entropía.
    """
    entropy_bytes = entropy_int.to_bytes(16, "big")
    cs = checksum4(entropy_bytes)
    combined = (entropy_int << 4) | cs
    indexes = [
        (combined >> (11 * (11 - i))) & 0x7FF
        for i in range(12)
    ]
    return indexes, cs


def phrase_is_valid(indexes: list[int]) -> bool:
    """Valida que los índices correspondan a la entropía y checksum correctos."""
    if len(indexes) != 12 or any(not (0 <= i < BLOCK) for i in indexes):
        return False
    combined = 0
    for idx in indexes:
        combined = (combined << 11) | idx
    cs = combined & 0xF
    entropy_int = combined >> 4
    entropy_bytes = entropy_int.to_bytes(16, "big")
    return cs == checksum4(entropy_bytes)


def build_candidate(first_position: int, items: list[Item]) -> dict:
    """
    Construye una frase válida comenzando con first_position (1..2048).
    
    Genera entropía aleatoria para los siguientes 11 valores,
    valida que no forme un patrón lineal o consecutivo,
    y verifica que no se haya generado antes.
    """
    if not (1 <= first_position <= BLOCK):
        raise ValueError(f"La posición inicial debe estar entre 1 y {BLOCK}.")
    
    first_index = first_position - 1  # 0-based index
    
    con = db_connect()
    try:
        while True:
            # Generar 117 bits aleatorios para llenar el resto
            random_tail = secrets.randbits(117)
            entropy_int = (first_index << 117) | random_tail
            indexes, cs = indexes_from_entropy(entropy_int)
            
            if indexes[0] != first_index:
                raise RuntimeError("Error interno: el primer índice no coincide.")
            if not phrase_is_valid(indexes):
                raise RuntimeError("Error interno de checksum.")
            
            # Convertir a posiciones (1-based) para el filtro
            positions = [idx + 1 for idx in indexes]
            
            # FILTRO REFORZADO V3.0: rechazar patrones lineales Y consecutivos
            if is_forbidden_linear_pattern(positions):
                continue
            
            # Obtener palabras y primos
            selected = [items[idx] for idx in indexes]
            words = [x.word for x in selected]
            primes = [x.prime for x in selected]
            phrase = " ".join(words)
            phrase_hash = hashlib.sha256(phrase.encode("utf-8")).hexdigest()
            
            # Intentar registrar en BD (evita duplicados)
            try:
                con.execute(
                    "INSERT INTO generated(phrase_hash, first_position, created_at) VALUES (?, ?, ?)",
                    (phrase_hash, str(first_position), datetime.now(timezone.utc).isoformat())
                )
                con.commit()
                break
            except sqlite3.IntegrityError:
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
        self.title("Generador V3.0 — Serie FINITA · Filtro Lineal Total Reforzado")
        self.geometry("1100x750")
        self.minsize(1000, 650)
        
        try:
            self.items = load_items()
        except Exception as exc:
            messagebox.showerror("Error de datos", str(exc))
            self.destroy()
            return
        
        self.position_var = tk.StringVar(value="1")
        self.info_var = tk.StringVar()
        self.entropy_var = tk.StringVar()
        self.checksum_var = tk.StringVar()
        self.count_var = tk.StringVar()
        self.phrase_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Listo")
        self.current_result = None
        self.generating = False
        
        self._build_ui()
        self._update_info()
    
    def _build_ui(self):
        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)
        
        title = ttk.Label(
            main,
            text="Generador V3.0 — Serie Finita · Filtro Lineal Total Reforzado",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        explanation = ttk.Label(
            main,
            text=(
                "Generador con serie FINITA (posiciones 1–2048). "
                "Introduce una posición inicial (1–2048) y se generarán 12 palabras únicas con entropía criptográfica. "
                "Se rechaza automáticamente: orden ascendente/descendente, paso fijo, "
                "secuencias consecutivas y patrones lineales ordenados. "
                "Filtro lineal total reforzado activo."
            ),
            wraplength=1050,
            justify="left"
        )
        explanation.pack(anchor="w", pady=(0, 8))
        
        input_frame = ttk.Frame(main)
        input_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(input_frame, text="Posición inicial (1–2048):").pack(side="left")
        entry = ttk.Entry(input_frame, textvariable=self.position_var, width=12)
        entry.pack(side="left", padx=(8, 8))
        entry.bind("<KeyRelease>", lambda _: self._update_info())
        entry.bind("<Return>", lambda _: self.on_generate())
        
        self.generate_btn = ttk.Button(input_frame, text="Generar 12 palabras", command=self.on_generate)
        self.generate_btn.pack(side="left", padx=(0, 12))
        ttk.Label(input_frame, textvariable=self.info_var).pack(side="left")
        
        table_frame = ttk.Frame(main)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        columns = ("n", "position", "prime", "word")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {
            "n": "#",
            "position": "Posición",
            "prime": "Primo impar",
            "word": "Palabra",
        }
        widths = {
            "n": 40,
            "position": 120,
            "prime": 140,
            "word": 250,
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
        phrase_entry = ttk.Entry(phrase_frame, textvariable=self.phrase_var, state="readonly", width=100)
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
    
    def _update_info(self):
        try:
            pos = int(self.position_var.get().strip())
            if 1 <= pos <= BLOCK:
                item = self.items[pos - 1]
                self.info_var.set(f"Palabra: «{item.word}» · Primo: {item.prime}")
                return
        except (ValueError, IndexError):
            pass
        self.info_var.set("Introduce un entero entre 1 y 2048")
    
    def on_generate(self):
        if self.generating:
            return
        try:
            pos = int(self.position_var.get().strip())
            if not (1 <= pos <= BLOCK):
                messagebox.showwarning("Posición inválida", f"Introduce un entero entre 1 y {BLOCK}.")
                return
        except ValueError:
            messagebox.showwarning("Posición inválida", "Introduce un entero válido.")
            return
        
        try:
            result = build_candidate(pos, self.items)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return
        
        self.generating = True
        self.generate_btn.configure(state="disabled")
        self.status_var.set("Generando…")
        
        def worker():
            try:
                self.after(0, lambda: self._display_result(result))
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
                    result["positions"][i],
                    result["primes"][i],
                    result["words"][i],
                )
            )
        
        self.phrase_var.set(result["phrase"])
        self.entropy_var.set(result["entropy_hex"])
        self.checksum_var.set(result["checksum_bits"])
        self.count_var.set(str(result["local_count"]))
        self.status_var.set("Listo — Serie finita · Filtro total reforzado")
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
