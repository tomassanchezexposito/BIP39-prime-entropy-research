# Generador V2.3-A24 — Ancla posicional bidireccional

## Objetivo

Esta versión lleva el desarrollo V2.3-A de 12 palabras a grupos BIP-39 de **24 palabras**.

El usuario indica:

- una **posición absoluta ancla**;
- la **posición del grupo 1..24** en la que debe aparecer la palabra asociada a esa coordenada.

La aplicación genera una frase BIP-39 válida y levanta las coordenadas absolutas:

- hacia atrás antes del ancla;
- hacia delante después del ancla;

manteniendo siempre una serie absoluta estrictamente creciente.

## BIP-39 de 24 palabras

Para 24 palabras:

- entropía: **256 bits**;
- checksum SHA-256: **8 bits**;
- total codificado: **264 bits**;
- 24 índices de 11 bits.

### Ancla en slots 1..23

Cada índice ocupa 11 bits completos del campo de entropía:

- 11 bits fijados por la palabra ancla;
- 245 bits generados mediante `secrets.randbits(245)`;
- checksum de 8 bits calculado después.

### Ancla en slot 24

La última palabra contiene:

- 3 bits finales de entropía;
- 8 bits de checksum.

Por ello la aplicación:

1. fija los 3 bits de entropía correspondientes al índice solicitado;
2. genera los otros 253 bits mediante CSPRNG;
3. calcula SHA-256;
4. repite hasta que el byte de checksum coincida con los 8 bits requeridos.

La aceptación esperada es aproximadamente **1 de cada 256 candidatos**.

## Coordenadas absolutas

La regla se mantiene:

```text
posición_local(g) = ((g - 1) mod 2048) + 1
```

Si el ancla ocupa el slot `k`:

```text
g1 < g2 < ... < gk = ANCLA < ... < g24
```

Cada `gi` conserva exactamente la posición local/índice BIP-39 correspondiente.

## Filtro V2.3 generalizado

Se aplica sobre las 24 posiciones locales:

- progresión modular de paso fijo;
- 24 posiciones iguales;
- recorrido local estrictamente ascendente o descendente con separación arbitraria y como máximo un cruce del borde 2048↔1.

Es un filtro determinista y **no añade entropía**.

## SQLite

La aplicación usa una base separada de la versión de 12 palabras:

```text
GeneradorPrimosPalabrasV23A24AnclaPosicional
```

Así no se mezclan historiales ni contadores de espacios de frase diferentes.

Se guardan:

- hash SHA-256 de la frase;
- primera posición absoluta real;
- fecha UTC;
- posición absoluta ancla;
- slot del ancla.

## Archivos

- `Generador_V2_3A24_Ancla_Posicional_Bidireccional.py`
- `datos_2048.json`
- `EJECUTAR_V2_3A24_ANCLA_POSICIONAL.bat`
- `test_V2_3A24_ancla_posicional.py`
- `RESULTADO_PRUEBAS.txt`

## Ejecución

En Windows:

```text
EJECUTAR_V2_3A24_ANCLA_POSICIONAL.bat
```

o:

```bash
python Generador_V2_3A24_Ancla_Posicional_Bidireccional.py
```

## Pruebas

```bash
python test_V2_3A24_ancla_posicional.py
```

La batería incluida verifica:

- vector BIP-39 de 24 palabras con entropía cero;
- 2.048 índices × 24 slots = **49.152 restricciones exhaustivas**;
- **2.400** levantamientos bidireccionales;
- posiciones ordinales de primos de referencia;
- integración real en slots 1, 12, 23 y 24;
- SQLite temporal;
- casos imposibles de borde.

## Seguridad

Software experimental. Las frases publicadas o generadas para investigación no deben utilizarse para custodiar activos reales.

El mapeo a primos, las coordenadas absolutas, los filtros y la base de datos no incrementan la entropía criptográfica de BIP-39.
