# Guía de estudio · Unidad 1 (Python moderno)

Un snippet con lo esencial de cada ejercicio (31 en total). Cada bloque trae el
código mínimo y, debajo, **la idea que tienes que poder explicar**.

Índice: [Sesión 1](#sesión-1--curso-acelerado-y-zen) ·
[Sesión 2](#sesión-2--tipado-y-pydantic) ·
[Sesión 3](#sesión-3--iteración-recursos-y-concurrencia) ·
[Sesión 4](#sesión-4--uv-logging-y-mcp)

---

## Sesión 1 · Curso acelerado y Zen

### N1-1 · f-string con formato
```python
print(f"{nombre_modelo} obtuvo {exactitud:.1%} en {cantidad_pruebas} pruebas")
```
`:.1%` multiplica por 100 y deja 1 decimal. **Exactitud 0.0 no es dato ausente**:
es una medición real; la ausencia es `None`.

### N1-2 · `append` vs `extend`
```python
a = ["hola"]; a.append(["x", "y"])   # ['hola', ['x', 'y']]  (lista dentro de lista)
b = ["hola"]; b.extend(["x", "y"])   # ['hola', 'x', 'y']    (lista plana)
b[-2:]                               # los dos últimos
```
`append` agrega **un** elemento; `extend` agrega **los elementos** de otra colección.

### N1-3 · Copia superficial vs. independiente
```python
copia = fuente.copy()
copia["etiquetas"] = copia["etiquetas"].copy()   # copiar también la lista interna
copia["etiquetas"].append("corto")               # el original no cambia
```
`.copy()` es superficial: la lista interna sigue compartida. Más niveles → `copy.deepcopy()`.

### N1-4 · Elegir estructura
```python
predicciones = [{"texto": "Python", "etiqueta": "lenguaje", "score": 0.99}, ...]
etiquetas = {p["etiqueta"] for p in predicciones}
```
Lista de dicts = registros **en orden de llegada** con campos con nombre.
Set = valores **únicos** y pertenencia rápida.

### N1-5 · Cero no es ausencia
```python
for score in [None, 0.0, 0.4, 0.95, 0.99]:
    if score is None:
        continue          # salta al siguiente
    print(score)
    if score >= 0.9:
        break             # termina el ciclo
```
`if not score` descartaría el `0.0` (es falso). Para ausencia usa `is None`.

### N1-6 · Ciclo vs. comprehension
```python
fahrenheit = [c * 9 / 5 + 32 for c in temperaturas if c >= 25]   # [77.0, 84.2, 87.8]
```
Misma lógica que el `for` + `if` + `append`, en una sola expresión legible.

### N1-7 · Promedio sin inventar datos
```python
def promedio_o_none(valores):
    if not valores:
        return None
    return sum(valores) / len(valores)
```
`0.0` = medición real. `None` = no hay datos (y evita dividir entre cero).

### N1-8 · Resumir grupos
```python
promedios = {etiqueta: sum(s) / len(s) for etiqueta, s in por_etiqueta.items()}
sorted(promedios.items(), key=lambda par: par[1], reverse=True)   # ranking
```
`defaultdict(list)` agrupa; después se promedia cada lista. `key=` recibe la función sin llamarla.

### N1-9 · Alias vs. instancia nueva
```python
otro_nombre = contador_a        # NO crea objeto: es el mismo (otro_nombre is contador_a)
otro_nombre.reiniciar()         # reinicia también a contador_a
contador_c = Contador("lote C") # esto sí es una instancia nueva e independiente
```

### N1-10 · Estado por instancia
```python
class RegistroIndependiente:
    def __init__(self):
        self.registros = []      # una lista por instancia, creada en __init__
```
Una lista definida en el cuerpo de la clase se **comparte** entre todas las instancias.

### N1-11 · Comprobar el contrato con `assert`
```python
assert resumen["cantidad"] == 4
assert math.isclose(resumen["promedio"], 0.6425)   # floats: isclose, no ==
assert lote_vacio.resumen()["promedio"] is None
assert lote._registros[3]["score"] == 0.0          # el cero se conserva
```

### Zen · Refactorizar con las reglas
```python
def parse_score(record):
    if not record or "score" not in record:   # guard clause (regla 5)
        return None
    try:
        score = float(record["score"])
    except (ValueError, TypeError):           # solo lo esperado (regla 10)
        return None
    return score if score >= 0 else None
```
Nombres descriptivos (7), nada de `except Exception: pass` (10/11), menos anidación (5).

### Laboratorio de errores (sección 7)
| Código | Excepción | Causa |
|---|---|---|
| `int("tres")` | `ValueError` | el texto no tiene forma de número |
| `["a","b"][5]` | `IndexError` | posición que no existe |
| `{"modelo":"demo"}["score"]` | `KeyError` | clave que no existe (`.get` evita el error) |
| `"score=" + 0.91` | `TypeError` | no se puede sumar `str` con `float` (usa f-string) |

---

## Sesión 2 · Tipado y Pydantic

### N3-1 · Anotar sin cambiar el comportamiento
```python
def select_scores(values: list[float], threshold: float) -> list[float]:
    return [v for v in values if v >= threshold]    # >= conserva el igual al umbral
```

### N3-2 · Corregir el contrato (mypy)
```python
result = apply_threshold(float("0.9"), 0.8)      # convertir explícitamente
def display_score(score: float | None) -> str:
    if score is None:                            # atender None antes de multiplicar
        return "No score"
    return f"{score * 100:.1f}%"
```
`float("abc")` pasa mypy (es un `str`) pero falla en ejecución con `ValueError`:
mypy revisa **tipos**, no el **contenido** de los valores.

### N3-3 · Ausente, nulo e inválido
```python
class RequiredNullable(BaseModel):
    source: str | None          # acepta None pero es OBLIGATORIO
class Optional(BaseModel):
    source: str | None = None   # acepta None y se puede omitir
```
Sin `source` ✔ · `source=None` ✔ · sin `score` ✘ (`missing`) · `score=None` ✘ (`float_type`) · 0 y 1 ✔.

### N3-4 · Casos que faltaban
```python
@field_validator("text", "label", "source", mode="before")
@classmethod
def normalize_strings(cls, value):
    return value.strip().lower() if isinstance(value, str) else value
```
`min_length=1` solo acepta `"   "` (longitud 3). El validador `before` quita espacios
primero; entonces `""` sí falla. Rechazados: `"   "`, `None`, `True`, `"nan"`, `-0.1`, `1.1`. `0.0` es válido.

### N3-5 · Configuración antes de procesar
```python
BatchConfig.model_validate({"batch_name": "Practice", "threshold": 0, "max_records": 3})
# max_records="3" ✘ (strict)   max_records=0 ✘ (ge=1)   batch_name="   " ✘
```
Config inválida → se detiene **todo** el lote (no hay regla confiable). Registro inválido →
solo ese registro se guarda como rechazo.

### N3-6 · Ida y vuelta (JSON) y errores anidados
```python
restored = BatchReport.model_validate_json(report.model_dump_json())
assert restored == report
payload = example_report.model_dump()
payload["accepted"][0]["score"] = 5
# ValidationError -> loc == ("accepted", 0, "score")
```
`loc` es la ruta completa al campo. `model_dump()` crea dicts nuevos: el original no cambia.

### N3-7 · Comprobar antes de ampliar
```python
assert average_score(process_records([], cfg).accepted) is None
assert average_score(process_records([None], cfg).accepted) is None
with pytest.raises(ValueError): ...   # aquí: try/except ValueError con raise AssertionError en else
process_records([registro] * 11, cfg) # > max_records -> ValueError, no se trunca
```

### N3-8 · `count_labels` y registro con dos errores
```python
def count_labels(predictions: list[Prediction]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for p in predictions:
        counts[p.label] = counts.get(p.label, 0) + 1
    return counts
```
Registro `{"text": "Bad", "label": "other", "score": 2}` → **2 issues, 1 registro rechazado**:
el rechazo se cuenta por posición del registro, no por error. `mypy --strict` sin errores.

---

## Sesión 3 · Iteración, recursos y concurrencia

### N4-1 · Generador
```python
def even_numbers(stop: int) -> Iterator[int]:
    for number in range(0, stop, 2):
        yield number
list(even_numbers(7))   # [0, 2, 4, 6]
```
`yield` pausa la función y entrega un valor a la vez; no se construye la lista completa.

### N4-2 · Cierre de archivos con `with`
```python
with path.open(encoding="utf-8") as file:
    first_line = next(file).strip()
assert file.closed                      # cerrado al salir del bloque

try:
    with path.open(encoding="utf-8") as f:
        raise ValueError("Invalid reading")
except ValueError:
    pass
assert f.closed                         # cerrado aunque haya excepción
```

### N4-3 · Tareas concurrentes con `TaskGroup`
```python
async with asyncio.TaskGroup() as group:
    north = group.create_task(fetch_reading("north", 3))
    west = group.create_task(fetch_reading("west", 1))
assert north.result() == ("north", 18.0)
assert west.result() == ("west", 32.0)
```
Total ≈ 3 s (no 4). `west` se anuncia primero porque crear la tarea solo decide
cuándo **empieza**; termina primero la que espera menos (1 s < 3 s).

### N4-4 · Limpieza con timeout
```python
async def slow_update(delay):
    events.append("started")
    try:
        await asyncio.sleep(delay)
    finally:
        events.append("cleaned up")      # corre aunque se cancele

try:
    async with asyncio.timeout(1):
        await slow_update(3)             # TimeoutError
except TimeoutError: ...
async with asyncio.timeout(3):
    await slow_update(1)                 # termina a tiempo, también limpia
```
Al vencer el tiempo se cancela la corrutina, corre `finally` y después sale `TimeoutError`.

---

## Sesión 4 · uv, logging y MCP

### S4-1 · Punto de entrada
```python
if __name__ == "__main__":
    raise SystemExit(main())     # importar el módulo NO ejecuta main()
```
Registrar herramienta (`@mcp.tool()`) ≠ iniciar servidor (`mcp.run(transport="stdio")`).

### S4-2 · Datos y argumentos
```bash
uv run --locked python main.py python --catalog data/extra_courses.json   # 3 resultados
uv run --locked python main.py python --catalog data/missing.json          # código 1
```
La herramienta MCP usa siempre `DEFAULT_CATALOG`.

### S4-3 · Niveles y destinos de logging
```bash
uv run --locked python main.py python --log-level ERROR --log-file logs/app.log
```
Handler de consola = nivel pedido; handler de archivo = siempre `DEBUG`.
stdout se reserva al protocolo MCP; los logs van a **stderr**.

### S4-4 · Mejorar el diagnóstico
```python
logger.info(
    "Search completed: %d matches out of %d courses read",
    len(matches),
    len(courses),
)
```
Argumentos (`%d`) y no f-string: logging formatea solo si se emite.

### S4-5 · Reproducción y llamada MCP
```bash
uv sync --locked
uv run --locked python client.py python      # 2 cursos, is_error: false
uv run --locked python client.py astronomy   # lista vacía, is_error: false
uv run --locked python client.py " "         # is_error: true, código 1
```
Vacío = "no hay resultados"; error = "no se pudo buscar". `pyproject.toml` = dependencias
declaradas · `uv.lock` = versiones exactas · `.python-version` = intérprete.
`.venv` no se entrega: se reconstruye.

### S4-6 · Calidad 1 (Ruff)
```bash
uv run --locked ruff check .     # F401 `os` imported but unused  -> quitar el import
```

### S4-7 · Calidad 2 (las cuatro comprobaciones)
```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy --strict main.py server.py client.py catalog
uv run --locked python -m pytest
```
Ruff = estilo y errores comunes · mypy = tipos sin ejecutar · pytest = pruebas existentes.
