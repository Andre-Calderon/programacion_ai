# Guía de estudio · Unidad 3 (SQL y workflows)

Un snippet por cada uno de los 5 ejercicios obligatorios, con la idea que tienes que
poder explicar.

## Sesión 1 · SQLite y pandas

### Ej. 1 · Consulta parametrizada
```python
query = "SELECT title, pages FROM documents WHERE topic = ? AND pages >= ? ORDER BY pages ASC"
with closing(sqlite3.connect(DB_PATH, autocommit=False)) as connection:
    rows = connection.execute(query, ("data", 22)).fetchall()   # [("Pandas tables", 24)]
```
Los valores van en una tupla, en el orden de los `?`; nunca pegados con una f-string.

### Ej. 2 · Actualización confirmada
```python
with closing(sqlite3.connect(DB_PATH, autocommit=False)) as connection:
    with connection:                                   # commit / rollback
        connection.execute("UPDATE documents SET pages = ? WHERE id = ?", (14, 7))
```
`closing` **cierra** la conexión. `with connection` **confirma o revierte** la transacción.
Se verifica abriendo una conexión nueva.

### Ej. 3 · Resumen con pandas
```python
df = pd.read_sql_query("SELECT title, topic, pages FROM documents", connection)
df.groupby("topic", as_index=False).agg(documents=("title", "size"), average_pages=("pages", "mean"))
```

## Sesión 2 · LangGraph

### Ej. 1 · Filtrar por páginas
```python
minimum = state.get("min_pages", 0)          # compatible con llamadas sin min_pages
if document["topic"] == state["topic"] and document["pages"] >= minimum: ...
```
`retrieval` con mínimo 14 → 1 documento; con 20 → ninguno (ruta `empty`).

### Ej. 2 · Nodo `calculate_average`
```python
builder.add_edge("summarize", "calculate_average")
builder.add_edge("calculate_average", END)      # antes: summarize -> END
builder.add_edge("empty", END)                   # la ruta vacía no cambia
```
`data` con `min_pages=0` → media 22.0. La ruta vacía evita dividir entre cero.

## Opcionales (sin entrega)
Neo4j (`u3_n2`) y LangChain (sesión 3) no tienen ejercicios entregables; LangChain
necesita una API key propia.
