# Guía de estudio · Unidad 2 (Procesamiento de datos)

Un snippet con lo esencial de cada uno de los 23 ejercicios y, debajo, **la idea
que tienes que poder explicar**.

Índice: [Sesión 1 · NumPy](#sesión-1--numpy) · [Sesión 2 · pandas](#sesión-2--pandas) ·
[Sesión 3 · PyTorch](#sesión-3--pytorch) · [Sesión 4 · Visualización](#sesión-4--visualización)

---

## Sesión 1 · NumPy

Datos: matriz `readings` de forma `(8, 3)`: 8 rondas (filas, eje 0) y 3 salas
(columnas, eje 1: norte, sur, almacén).

### Ej. 1 · Vector vs. matriz de una fila
```python
one_round = np.array([22.0, 24.0, 20.0])        # shape (3,)  ndim 1
one_round_table = np.array([[22.0, 24.0, 20.0]]) # shape (1, 3) ndim 2
```
Mismo `size` (3), distinto número de ejes.

### Ej. 2 · Tipo numérico
```python
values = np.array([22, 24, 20], dtype=np.float64)
values[0] = 22.75        # con dtype entero se truncaría a 22
```
Asignar a un arreglo entero **no** lo convierte a float: hay que crearlo float desde el inicio.

### Ej. 3 · Filas y columnas en un orden
```python
readings[-3:, [0, 2]]    # últimas 3 rondas; norte y almacén -> shape (3, 2)
```
Una lista de índices en una columna define su orden.

### Ej. 4 · Conservar el eje
```python
readings[:, 1:2].shape   # (8, 1)  el corte conserva el eje
readings[:, 1].shape     # (8,)    el índice entero lo elimina
```

### Ej. 5 · Máscara con intervalo
```python
south = readings[:, 1]
mask = (south >= 26) & (south < 29)   # & y paréntesis; NO usar "and"
readings[mask]                        # 3 filas completas
```
La máscara debe tener una posición por fila (`shape (8,)`).

### Ej. 6 · Copia independiente
```python
last_rounds = readings[-2:].copy()    # sin copy() sería una vista
last_rounds[0, 0] = 100               # readings no cambia
```
Un corte básico es **vista** (comparte memoria); máscara o lista de índices da **copia**.

### Ej. 7 · Vectorizar
```python
converted = readings * 9 / 5 + 32     # forma (8, 3) conservada, sin ciclo
```

### Ej. 8 · Filas completas
```python
complete = np.isfinite(q).all(axis=1)   # una posición por fila
q[complete]                             # aceptadas; (~complete).sum() = rechazadas
```
Sin filas completas la selección es `(0, 3)` y su media sería `nan`: se detecta antes.

### Ej. 9 · Broadcasting
```python
room_means = readings.mean(axis=0)        # (3,) una media por sala
differences = readings - room_means       # (8, 3) - (3,) -> (8, 3)
differences.mean(axis=0)                  # ~ [0, 0, 0]
```
Las formas se alinean **por la derecha**: el `(3,)` se empareja con las 3 columnas y se
repite en las 8 filas. No se resta la media general porque cada sala tiene su escala.

### Ej. 10 · Comparar reportes
```python
summarize(load_readings("readings.csv"))      # 8 rondas -> medias 25.5, 27.5, 23.5
summarize(complete)                           # 2 rondas -> medias 23, 25, 21
```
Cambian porque entran **otras filas** de **otro archivo**, no porque algo cambiara en el tiempo.

### Ej. 11 · `select_warm_rounds`
```python
def select_warm_rounds(readings, threshold):
    validate_shape(readings)
    if not np.isfinite(readings).all(): raise ValueError("Readings must be finite")
    if not np.isfinite(threshold):      raise ValueError("Threshold must be finite")
    return readings[readings[:, 0] >= threshold]     # máscara -> copia
```
Umbral 27 → 3 filas; umbral 100 → forma `(0, 3)` (no se calcula la media).
Media de la selección `[28, 30, 26]` vs. completa `[25.5, 27.5, 23.5]`.

---

## Sesión 2 · pandas

### Ej. 1 · Ausentes
```python
passengers["Age"].isna().sum()        # 177
passengers["Embarked"].isna().sum()   # 2
passengers.loc[passengers["Embarked"].isna(), ["PassengerId", "Pclass", "Embarked"]]
```
`Cabin` falta en 687 de 891 y es texto: no hay un valor simple que imputar.

### Ej. 2 · `groupby` + `agg`
```python
prepared.groupby("Pclass", as_index=False, dropna=False).agg(
    passengers=("Survived", "size"), survival_rate=("Survived", "mean"))
```
Conteos suman 891; clase 1 tiene la proporción más alta (~0.63). **Describe, no atribuyas causa.**

### Ej. 3 · Columna nueva en una copia
```python
with_alone = prepared.copy()
with_alone["travel_alone"] = with_alone["family_size"] == 1   # 537 pasajeros
```
`prepared` no recibe la columna porque trabajaste en la copia.

### Ej. 4 · Tabla → matriz
```python
idx = FEATURE_COLUMNS.index("age_filled")
np.testing.assert_allclose(features[:, idx].mean(), prepared["age_filled"].mean(),
                           atol=1e-4, rtol=0)
```
Difieren poquísimo porque la matriz es `float32` y la tabla `float64`.

### Ej. 5 · `missing_age_by_class`
```python
def missing_age_by_class(prepared):
    return prepared.groupby("Pclass", as_index=False, dropna=False).agg(
        passengers=("age_missing", "size"),
        missing_age_rate=("age_missing", "mean"))     # media de booleanos = proporción
```
Clase 1: 13.9 %, clase 2: 6.0 %, clase 3: 27.7 %. El total (177) no dice **dónde** faltan;
la proporción compara clases de distinto tamaño. Es asociación, no causa.

---

## Sesión 3 · PyTorch

### Ej. 1 · `clone()`
```python
first_three = features[:3].clone()   # copia independiente
first_three[0, 0] = 999.0            # features y features_np no cambian
```
`torch.from_numpy` **comparte** memoria; sin `clone()` el 999 aparecería en NumPy.

### Ej. 2 · Último lote
```python
[len(y) for _, y in DataLoader(ds, batch_size=3, shuffle=False)]                  # [3,3,3,1]
[len(y) for _, y in DataLoader(ds, batch_size=3, shuffle=False, drop_last=True)]  # [3,3,3]
```
`drop_last=True` descarta el lote incompleto: la muestra 9 (la última) no entra.

### Ej. 3 · Media por canal
```python
images.shape                              # (16, 3, 32, 32) = N, C, H, W
image_channel_means.mean(dim=0)           # (3,)
images.mean(dim=(0, 2, 3))                # (3,)  mismo resultado
torch.testing.assert_close(a, b)
```
Desaparecen los ejes 0, 2 y 3; queda el eje 1 (canal).

### Ej. 4 · Invertir `Normalize`
```python
restored_images = normalized_images * 0.5 + 0.5     # inversa de (x - 0.5) / 0.5
torch.testing.assert_close(restored_images, images)
```
Misma forma ≠ mismos valores: `[-1, 1]` frente a `[0, 1]`.

### Ej. 5 · `label_summary` con proporciones
```python
counts = torch.bincount(labels, minlength=len(class_names))
total = labels.numel()
{"class_id": i, "class_name": n, "count": int(counts[i]), "proportion": int(counts[i]) / total}
# retorno: list[dict[str, int | float | str]]
```
Etiquetas `[0,0,2,2,2]` → conteos `[2,0,3]`, proporciones `[0.4,0.0,0.6]` (suman 1); la clase vacía se conserva.

---

## Sesión 4 · Visualización

### Ej. 1 · Intervalos
```python
fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
ax.hist(ages, bins=20, color="#245E87", edgecolor="white")
```
Más `bins` muestran más detalle; la cantidad de edades (714) no cambia: solo cómo se agrupan.

### Ej. 2 · Barras de porcentajes
```python
pct = passengers.groupby("Pclass")["age_missing"].mean() * 100
ax.bar(names, pct); ax.set_ylim(0, 100); ax.set_ylabel("Missing ages (%)")
```
Clase 3 tiene el mayor porcentaje. El porcentaje divide entre el tamaño del grupo; contar solo
ausentes dependería de cuántos pasajeros tiene cada clase.
