# Pruebas Unitarias de Regresión (`tests/`)

Esta carpeta está dedicada a la verificación de la integridad, robustez y corrección lógica de todas las funciones del backend.

## 📌 Propósito

El módulo de pruebas asegura que cualquier cambio introducido en la base de datos o en los métodos de negocio (como el cálculo de proyecciones o boletines oficiales) no altere el funcionamiento general de la plataforma ni rompa relaciones relacionales preexistentes.

## 📂 Contenido del Directorio

- **`test_sistema.py`**: Suite de pruebas basada en el framework `unittest` de Python. Comprueba la validez de las tablas relacionales creadas, las restricciones únicas (`UNIQUE`), la inserción exitosa de datos y la correcta recuperación de registros académicos.

## ⚙️ Cómo Ejecutar las Pruebas

Para ejecutar las pruebas del sistema desde la carpeta principal `Proyecto`, abre la consola de comandos de Windows (PowerShell o CMD) y escribe:

```bash
py -m unittest tests/test_sistema.py
```

Deberás observar una salida exitosa confirmando que todas las aserciones han sido superadas (`OK`).

## ⚠️ Reglas y Restricciones de `tests/`

1. **Aislamiento de la Base de Datos**: Las pruebas deben diseñarse de forma que no contaminen la información productiva. Toda prueba que realice inserciones o modificaciones de datos temporales debe asegurar su limpieza o ejecutarse en una base de datos temporal si es necesario.
2. **Prohibido el Uso de Datos Estáticos Desconocidos**: Todos los IDs, correos o nombres utilizados en las pruebas deben coincidir estrictamente con los esquemas de datos semilla inicializados en el sistema para evitar falsos negativos.
3. **Nomenclatura Clara**: Los métodos de prueba deben comenzar obligatoriamente con el prefijo `test_` para que el recolector de `unittest` pueda localizarlos y ejecutarlos automáticamente.

---

*Garantizando la estabilidad y consistencia de la plataforma con cada modificación.*
