# Catálogo de cursos con MCP — Práctica de la sesión 4

Una función consulta `data/courses.json`. `main.py` la usa desde la terminal y
`server.py` la expone como herramienta MCP mediante stdio.

Los resultados de abajo salen de ejecutar los comandos desde una **copia limpia**
(sin `.venv`, cachés ni logs) con `uv 0.13.0`, que descargó Python 3.13.16
según `.python-version`.

## Comandos principales

```bash
uv sync --locked
uv run --locked python main.py python
uv run --locked python main.py python --catalog data/extra_courses.json
uv run --locked python main.py python --log-level DEBUG --log-file logs/app.log
uv run --locked python client.py python
```

`make` no está instalado en mi equipo con Windows, así que usé directamente los
comandos de cada receta del `Makefile` (`make check` = ruff check + ruff format
--check + mypy + pytest).

---

## Ejercicio 1 · Punto de entrada

```bash
uv run python -c "import main"
```

**Resultado:** no imprime nada y termina con código 0.

**Por qué no consulta el catálogo:** al importar `main.py` Python ejecuta el código
del archivo, pero ahí solo se *definen* funciones e imports. La consulta vive dentro
de `main()`, y `main()` solo se llama bajo la condición
`if __name__ == "__main__":`. Cuando el archivo se importa, `__name__` vale `"main"`
y no `"__main__"`, por eso no se llama.

**Qué impide iniciar el transporte al importar `server.py`:** la condición final

```python
if __name__ == "__main__":
    configure_logging()
    mcp.run(transport="stdio")
```

Al importar `server`, `__name__` es `"server"` y `mcp.run(...)` no se ejecuta.
Comprobación:

```bash
uv run python -c "import server; print('server importado; herramientas registradas, transporte NO iniciado')"
# server importado; herramientas registradas, transporte NO iniciado   (código 0)
```

**Registrar una herramienta vs. iniciar el servidor:** `@mcp.tool()` solo *registra*
la función `find_courses` en el objeto `mcp` (la deja anotada en el servidor y
describe su entrada y salida). Eso ocurre al importar el módulo. Iniciar el servidor
es `mcp.run(transport="stdio")`: abre el transporte, se pone a leer stdin y atiende
peticiones. Registrar es declarar qué se ofrece; iniciar es empezar a atender.

---

## Ejercicio 2 · Datos y argumentos

Copié `data/courses.json` a `data/extra_courses.json` y le agregué:

```json
{"code": "PY03", "title": "Python for automation", "hours": 10}
```

```bash
uv run --locked python main.py python --catalog data/extra_courses.json
```

```text
INFO | catalog.search | Search completed: 3 matches out of 4 courses read
[ {"code": "PY01", ...}, {"code": "PY02", ...}, {"code": "PY03", "title": "Python for automation", "hours": 10} ]
```

Aparecen **tres resultados** (PY01, PY02 y PY03).

Ruta inexistente:

```bash
uv run --locked python main.py python --catalog data/missing.json
```

```text
ERROR | __main__ | Catalog search failed
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'data\\missing.json'
```

**Código de salida: 1.** (`main()` atrapa `OSError`/`ValueError`, registra el
traceback con `logger.exception` y devuelve 1.)

**La herramienta MCP sigue usando el catálogo predeterminado:** `client.py python`
devuelve solo PY01 y PY02, porque `server.py` llama a `search_courses(query)` sin
pasar ruta y usa `DEFAULT_CATALOG`. La opción `--catalog` existe solo en
`main.py`.

---

## Ejercicio 3 · Niveles y destinos

Misma consulta (`python`) con distintos niveles:

| Nivel de consola | Mensajes que aparecen en consola (stderr) |
|---|---|
| `DEBUG` | `DEBUG ... Reading catalog: .../data/courses.json` y `INFO ... Search completed` |
| `INFO` | solo `INFO ... Search completed` |
| `ERROR` | ninguno (la búsqueda no falló) |

El JSON con los cursos sale siempre igual por stdout.

```bash
uv run --locked python main.py python --log-level ERROR --log-file logs/app.log
```

La consola no muestra logs, pero `logs/app.log` contiene:

```text
DEBUG | catalog.search | Reading catalog: .../data/courses.json
INFO | catalog.search | Search completed: 2 matches
```

**Por qué el archivo conserva mensajes que no aparecen en consola:** el logger raíz
acepta desde DEBUG; cada *handler* decide qué deja pasar. El handler de consola usa
el nivel pedido (`ERROR`), mientras que el handler del archivo siempre usa `DEBUG`.
Un mismo mensaje pasa por los dos handlers y cada uno lo filtra distinto.

**Por qué stdout debe reservarse al protocolo en `server.py`:** con transporte stdio
el cliente y el servidor se comunican con mensajes MCP por stdin/stdout del proceso.
Si el servidor escribiera un `print` o un log en stdout, ese texto se mezclaría con
los mensajes del protocolo y el cliente no podría interpretarlos. Por eso los logs
van a stderr (`StreamHandler`) y se puede comprobar que `python main.py python > result.json`
guarda solo el JSON, sin logs.

---

## Ejercicio 4 · Mejorar el diagnóstico

Cambio en `catalog/search.py` (con argumentos de logging, no con f-string):

```python
logger.info(
    "Search completed: %d matches out of %d courses read",
    len(matches),
    len(courses),
)
```

Con `data/courses.json` ahora se ve:

```text
INFO | catalog.search | Search completed: 2 matches out of 3 courses read
```

Se usan argumentos (`%d` + valores) en lugar de una f-string para que logging solo
construya el texto si el mensaje realmente se va a emitir.

**Los resultados no cambiaron:** comparé la salida de `main.py python` y de
`client.py python` antes y después del cambio (solo la stderr cambia) y ambas
siguen devolviendo exactamente los cursos PY01 y PY02, tanto en la consulta directa
como en la llamada MCP.

---

## Ejercicio 5 · Reproducción y llamada MCP

Desde una copia limpia (solo código, datos, `pyproject.toml`, `uv.lock`,
`.python-version`, `Makefile` y README):

```bash
uv sync --locked
# Using CPython 3.13.16 / Creating virtual environment at: .venv / Installed 41 packages
uv run --locked python client.py python
uv run --locked python client.py astronomy
uv run --locked python client.py " "
```

| Consulta | Resultado | Código |
|---|---|---|
| `python` | `is_error: false`, 2 cursos: PY01 y PY02 | 0 |
| `astronomy` | `is_error: false`, lista vacía (`"result": []`) | 0 |
| `" "` | `is_error: true`, mensaje "Cannot search the catalog. Check the query and server logs." | 1 |

**Herramienta disponible:** `Tools: ['find_courses']`. El cliente inicia
`server.py`, lista las herramientas y llama a `find_courses`.

**Respuesta vacía vs. error:** `astronomy` es una consulta válida que simplemente no
coincide con ningún título; el resultado es una lista vacía con `is_error: false` y
el cliente termina con 0. En cambio la cadena de espacios es una consulta inválida
(`ValueError: Query must not be blank`), el servidor responde con `ToolError`,
`is_error: true` y el cliente termina con 1. Una lista vacía significa "no hay
resultados"; un error significa "no se pudo hacer la búsqueda".

**Qué aporta cada archivo:**

- `pyproject.toml`: nombre del proyecto, `requires-python >= 3.12` y las
  dependencias *directas* declaradas con rangos (`mcp>=2,<3`, `pydantic>=2,<3`) y
  las herramientas de desarrollo.
- `uv.lock`: las versiones *exactas* ya resueltas de todas las dependencias, directas
  y transitivas (por eso `--locked` reproduce las mismas versiones: pydantic 2.13.5,
  mcp 2.2.0, etc.).
- `.python-version`: el intérprete elegido (3.13), para que uv use la misma versión.

**Por qué no se entrega `.venv`:** es un entorno local, grande y específico de cada
sistema operativo y de cada ruta; se puede reconstruir en segundos con
`uv sync --locked` a partir de los tres archivos anteriores. Por eso está en
`.gitignore`, igual que las cachés y los logs.

---

## Ejercicios de calidad

### Calidad 1 · Import sin usar

Agregué `import os` a `main.py` sin usarlo y ejecuté:

```bash
uv run --locked ruff check .
```

```text
F401 [*] `os` imported but unused
 --> main.py:6:8
  |
6 | import os
  |        ^^
help: Remove unused import: `os`

Found 1 error.
```

(código de salida 1). Lo corregí quitando la línea y `ruff check .` volvió a dar
`All checks passed!` (código 0).

### Calidad 2 · Comprobaciones desde una copia limpia

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy --strict main.py server.py client.py catalog
uv run --locked python -m pytest
```

```text
All checks passed!
9 files already formatted
Success: no issues found in 6 source files
6 passed
```

Los cuatro comandos terminan con código 0. En la primera ejecución `ruff format --check`
había fallado porque mi cambio del ejercicio 4 estaba en dos líneas y Ruff lo
quiere con un argumento por línea; lo formateé con `ruff format` y quedó limpio.

- **Ruff** revisa estilo y errores frecuentes (aquí, el import sin usar).
- **mypy `--strict`** revisa los tipos sin ejecutar las consultas.
- **pytest** ejecuta las 6 pruebas existentes de búsqueda y de comunicación MCP
  real por stdio (no creé pruebas nuevas).
