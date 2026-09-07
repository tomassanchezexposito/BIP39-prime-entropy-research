# Generador V2.3-A — Ancla posicional bidireccional

## Objetivo

Esta variante parte de la V2.3 del 24 de agosto de 2026 y cambia la restricción principal:

- antes, la **posición absoluta introducida** determinaba obligatoriamente la **palabra 1**;
- ahora, la misma posición absoluta determina la **palabra ancla**, pero el usuario puede decidir en qué posición del grupo de 12 debe aparecer: **1..12**.

Ejemplo:

- posición absoluta ancla: `49238`
- local: `86`
- palabra: `apple`
- posición dentro del grupo: `6`

El resultado contiene `apple` exactamente como palabra #6 y la posición absoluta #6 es exactamente `49238`.

## Qué significa “hacia atrás y hacia delante”

La entropía BIP-39 no se calcula temporalmente hacia atrás.

El proceso correcto es:

1. La posición absoluta ancla se proyecta a local 1..2048.
2. Esa posición local identifica el índice BIP-39/palabra.
3. Se genera un campo de entropía de 128 bits condicionado a que ese índice aparezca en el slot elegido.
4. Se calcula el checksum BIP-39.
5. Se obtienen las 12 posiciones locales.
6. Desde el ancla:
   - las palabras anteriores se levantan a las mayores coordenadas absolutas positivas compatibles **anteriores**;
   - las posteriores se levantan a las menores coordenadas compatibles **posteriores**.
7. El resultado absoluto completo queda estrictamente creciente.

## Entropía

### Palabra ancla en slots 1..11

Cada uno de esos índices ocupa 11 bits completos del campo de entropía.

- 11 bits quedan fijados por la palabra ancla.
- 117 bits se generan mediante `secrets.randbits(117)`.
- checksum: 4 bits SHA-256, deterministas.

### Palabra ancla en slot 12

La palabra 12 contiene:

- 7 bits finales del campo de entropía;
- 4 bits de checksum.

Por ello no es correcto “fijar 11 bits de entropía” en este slot.

La aplicación:

- fija los 7 bits de entropía asociados a la palabra;
- genera los otros 121 bits con CSPRNG;
- recalcula SHA-256;
- repite hasta que los 4 bits de checksum coinciden con el índice solicitado.

La aceptación esperada es aproximadamente 1 de cada 16 candidatos de checksum.

## Coordenada absoluta y borde inferior

Las posiciones absolutas de primos siguen siendo positivas: 1 -> 3, 2 -> 5, etc.

Por tanto, una palabra ancla situada en un slot >1 necesita posiciones positivas anteriores.

Ejemplo imposible:

- ancla absoluta = 1
- slot = 2

No existe una posición absoluta positiva anterior a 1.

La aplicación detecta estos casos y no inventa coordenadas negativas.

Además, con el filtro lineal V2.3 activo, `slot 12` con un ancla todavía dentro del primer bloque `1..2048` es incompatible con el filtro: las 12 coordenadas positivas anteriores formarían un orden local estricto que V2.3 rechaza por diseño.

## Filtro V2.3

Se conserva:

- progresión modular de paso fijo;
- 12 posiciones iguales;
- recorrido local estrictamente ascendente o descendente con separación arbitraria y como máximo un cruce del borde.

El filtro es determinista y **no añade entropía**.

## SQLite

Se conserva el mismo `APP_NAME` de V2.3 para reutilizar el historial local.

El esquema se amplía de forma compatible con dos columnas opcionales:

- `anchor_absolute_position`
- `anchor_word_slot`

Las versiones antiguas pueden seguir insertando filas porque las nuevas columnas permiten `NULL`.

`first_absolute_position` conserva su significado literal: guarda la primera posición absoluta real del grupo, que puede ser anterior al ancla.

## Archivos

- `Generador_V2_3A_Ancla_Posicional_Bidireccional.py`
- `datos_2048.json`
- `EJECUTAR_V2_3A_ANCLA_POSICIONAL.bat`
- `test_V2_3A_ancla_posicional.py`

## Ejecución

Windows:

```text
EJECUTAR_V2_3A_ANCLA_POSICIONAL.bat
```

o:

```bash
python Generador_V2_3A_Ancla_Posicional_Bidireccional.py
```

## Pruebas

```bash
python test_V2_3A_ancla_posicional.py
```

La prueba incluye:

- vector BIP-39 de entropía cero;
- todos los 2.048 índices en cada uno de los 12 slots: 24.576 verificaciones;
- 2.400 levantamientos bidireccionales;
- verificación de posiciones/primos básicos;
- integración de candidatos en slots 6 y 12;
- SQLite temporal;
- casos imposibles de borde.

## Seguridad

Aplicación experimental. Las frases generadas o publicadas no deben usarse para custodiar activos reales. El mapeo a primos y la coordenada absoluta son representaciones deterministas y no incrementan la entropía BIP-39.
