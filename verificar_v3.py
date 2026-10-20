
#!/usr/bin/env python3

import subprocess
import re
import sys

# Requisitos de x86-64-v3 / AMD64-v3
requisitos = {
    "AVX":   {"avx"},
    "AVX2":  {"avx2"},
    "BMI1":  {"bmi1"},
    "BMI2":  {"bmi2"},
    "FMA":   {"fma"},
    "F16C":  {"f16c"},
    "LZCNT": {"lzcnt", "abm"},
    "MOVBE": {"movbe"},
    "XSAVE": {"xsave"},
}


def obtener_flags():
    try:
        resultado = subprocess.run(
            ["lscpu"],
            capture_output=True,
            text=True,
            check=True,
            errors="replace"
        )
    except FileNotFoundError:
        print("ERROR: no se encontró el comando lscpu.")
        sys.exit(1)
    except subprocess.CalledProcessError as error:
        print(f"ERROR al ejecutar lscpu: {error}")
        sys.exit(1)

    lineas = resultado.stdout.splitlines()
    flags = set()
    leyendo_flags = False

    for linea in lineas:
        # Detecta "Flags:", "Indicadores:", y variantes
        coincidencia = re.match(
            r"^\s*(?:Flags|Indicadores)\s*:\s*(.*)$",
            linea,
            re.IGNORECASE
        )

        if coincidencia:
            leyendo_flags = True
            flags.update(coincidencia.group(1).lower().split())
            continue

        if leyendo_flags:
            # Las líneas de continuación están indentadas.
            # Una nueva etiqueta de lscpu termina la lectura.
            if not linea.strip():
                break

            if re.match(r"^\s*[^:]+:\s*", linea):
                break

            flags.update(linea.lower().split())

    if not flags:
        print("ERROR: no se encontraron los indicadores de CPU.")
        print("Comprueba que lscpu esté instalado y disponible.")
        sys.exit(1)

    return flags


def main():
    flags = obtener_flags()
    faltantes = []

    print("=" * 46)
    print(" VERIFICACIÓN DE ARQUITECTURA X86-64-V3")
    print("=" * 46)

    for nombre, alternativas in requisitos.items():
        if flags.intersection(alternativas):
            print(f"{nombre:<8}: OK")
        else:
            print(f"{nombre:<8}: FALTANTE")
            faltantes.append(nombre)

    print("=" * 46)

    if faltantes:
        print("RESULTADO: NO CUMPLE todos los requisitos.")
        print("Indicadores faltantes:", ", ".join(faltantes))
    else:
        print("RESULTADO: CUMPLE los 9 indicadores.")
        print("Compatible con los requisitos de CPU verificados.")

    print("=" * 46)


if __name__ == "__main__":
    main()
