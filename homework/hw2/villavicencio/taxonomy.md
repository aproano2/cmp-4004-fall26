# Taxonomía de errores — brazo B (AUTO-GENERADO por `code/analyze.py`; no editar a mano)

Modelo: `qwen2.5:3b` · temperatura 0.7 · 3 corridas · 60 intentos de B · 60 fallos.

SAT no tiene cuantificadores; el análogo de los errores de *scope/aridad* de FOL son los errores de **índice/aridad** (literal fuera de rango, `num_vars` incorrecto, esquema inválido). El ground truth (CNF de referencia) se usa **solo aquí, en el análisis**; nunca se muestra al modelo ni al bucle de refinamiento.

## Conteo por categoría

| categoría | ¿detectable sin ground truth? | n |
|---|---|---|
| Arity / index error (invalid literal, var count or schema) | Yes | 30 |
| Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour) | Yes (decoder) | 18 |
| Malformed syntax (won't parse) | Yes | 7 |
| Valid syntax, under-constrained (wrong solution returned) — silent | No (needs a verifier / reference) | 4 |
| Valid syntax, over-constrained (UNSAT) | Yes | 1 |

**Fallos de B anunciados por el pipeline: 56 / 60** · silenciosos: 4 / 60.
Aciertos de B 'por las razones equivocadas' (respuesta válida con un CNF no equivalente al de referencia): 0 / 0.

## Todos los fallos de B (salida literal del modelo)

### 1. P01 · run 0 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 3 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D']; restricción de arista omitida por completo: ['A-B', 'A-D', 'B-C', 'C-D']; 15 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 12, "clauses": [[1, 2, 3, 4], [-5, -6, -7, -8], [9, 10, 11, 12], [-1, -7, -11, -12], [-2, -5, -9, -10], [-3, -6, -9, -11], [-4, -8, -10, -12], [1, 5, -7, -11], [-1, -5, 7, -11], [2, 6, -8, -12], [-2, -6, 8, -12], [3, 7, -9, -12], [-3, -7, 9, -12], [4, 8, -10, -11], [-4, -8, 10, -11]]}
````

### 2. P02 · run 0 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 0 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E']; restricción de arista omitida por completo: ['A-B', 'B-C', 'C-D', 'D-E']; 28 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 15, "clauses": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, -1], [1, 2, -5, -6], [1, 3, -5, -7], [1, 4, -5, -8], [2, 3, -6, -7], [2, 4, -6, -8], [3, 4, -7, -8], [5, 1, -13, -14], [5, 2, -13, -15], [6, 1, -14, -15], [7, 1, -13, -15], [7, 2, -13, -14], [8, 1, -13, -14], [8, 2, -13, -15], [9, 1, -12, -14], [9, 2, -12, -15], [10, 1, -11, -14], [10, 2, -11, -15], [11, 1, -10, -14], [11, 2, -10, -15], [12, 1, -9, -14], [12, 2, -9, -15], [13, 3, -15, -14], [14, 3, -15, -13], [15, 3, -14, -13]]}
````

### 3. P03 · run 0 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 2 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D']; restricción de arista omitida por completo: ['A-B', 'A-D', 'B-C']; 12 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 12, "clauses": [[1, 2, 3, 4], [-5, -6, -7, -8], [9, 10, 11, 12], [-1, -7, -11, -12], [-2, -5, -9, -11], [-3, -6, -9, -10], [4, 7, 11, 12], [-1, -4, -8, -12], [2, 5, 8, 10], [-3, -4, -6, -8], [1, 4, 7, 10], [-2, -3, -5, -7]]}
````

### 4. P04 · run 0 · easy

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 6: 16 (debe ser entero no nulo con |lit| <= 15)

````text
{"num_vars": 15, "clauses": [[1, 2, 3, 4], [-5, -6, -7], [8, 9, 10], [-8, -9, -10], [11, 12, 13], [-11, -12, -13], [14, 15, 16], [-14, -15, -16], [1, -2], [1, -2, 3], [1, -2, 4], [1, -2, 5], [1, -2, 6], [1, -2, 7], [1, -2, 8], [1, -2, 9], [1, -2, 10], [1, -2, 11], [1, -2, 12], [1, -2, 13], [1, -2, 14], [1, -2, 15]]}
````

### 5. P05 · run 0 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice E tiene 2 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E']; restricción de arista omitida por completo: ['A-B', 'A-E', 'B-C']; 65 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 15, "clauses": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, -1], [1, 2, -5, -6], [2, 3, -6, -7], [3, 4, -7, -8], [4, 5, -8, -9], [1, 4, -13, -14], [2, 5, -14, -15], [3, 6, -13, -15], [4, 7, -13, -14], [5, 8, -14, -15], [1, 6, -1, -2], [2, 7, -1, -3], [3, 8, -1, -4], [1, 7, -5, -6], [2, 8, -5, -7], [1, 9, -1, -2], [2, 10, -1, -3], [3, 11, -1, -4], [4, 12, -1, -5], [5, 13, -1, -6], [1, 10, -9, -10], [2, 11, -9, -11], [3, 12, -9, -12], [4, 13, -9, -10], [5, 14, -9, -11], [6, 15, -9, -12], [1, 11, -1, -2], [2, 12, -1, -3], [3, 13, -1, -4], [4, 14, -1, -5], [5, 15, -1, -6], [-1, -2, -3, -4], [-5, -6, -7, -8], [-9, -10, -11, -12], [-13, -14, -15, -1], [-13, -14, -15, -2], [-13, -14, -15, -3], [-13, -14, -15, -4], [-1, -2, -3, -4], [-1, -2, -5, -6], [-1, -2, -7, -8], [-1, -2, -9, -10], [-1, -3, -4, -5], [-1, -3, -6, -7], [-1, -3, -8, -9], [-1, -4, -5, -6], [-1, -4, -7, -8], [-1, -5, -6, -7], [-1, -5, -8, -9], [-2, -3, -4, -5], [-2, -3, -6, -7], [-2, -3, -8, -9], [-2, -4, -5, -6], [-2, -4, -7, -8], [-2, -5, -6, -7], [-2, -5, -8, -9], [-3, -4, -5, -6], [-3, -4, -7, -8], [-3, -5, -6, -7], [-3, -5, -8, -9], [-4, -5, -6, -7], [-4, -5, -7, -8], [-4, -6, -7, -8]]}
````

### 6. P06 · run 0 · easy

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 4: 19 (debe ser entero no nulo con |lit| <= 18)

````text
{"num_vars": 18, "clauses": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24], [25, 26, 27, 28], [29, 30, 31, 32], [-33, -34, -35, -36], [-37, -38, -39, -40], [-41, -42, -43, -44], [-45, -46, -47, -48], [-49, -50, -51, -52], [-53, -54, -55, -56], [-57, -58, -59, -60], [-61, -62, -63, -64], [-65, -66, -67, -68], [-69, -70, -71, -72]]}
````

### 7. P07 · run 0 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 4: 19 (debe ser entero no nulo con |lit| <= 18)

````text
{"num_vars": 18, "clauses": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24], [25, 26, 27, 28], [29, 30, 31, 32], [33, 34, 35, 36], [37, 38, 39, 40], [41, 42, 43, 44], [45, 46, 47, 48], [-49, -50, -51, -52], [-49, -52, -53, -54], [-49, -51, -54, -55], [-49, -50, -55, -56], [-57, -58, -59, -60], [-57, -59, -61, -62], [-57, -58, -62, -63], [-57, -59, -63, -64], [-57, -58, -64, -65], [-66, -67, -68, -69], [-66, -68, -70, -71], [-66, -67, -71, -72], [-66, -68, -72, -73], [-66, -67, -73, -74], [-75, -76, -77, -78], [-75, -77, -79, -80], [-75, -76, -80, -81], [-75, -77, -81, -82], [-75, -76, -82, -83], [-84, -85, -86, -87], [-84, -86, -88, -89], [-84, -85, -89, -90], [-84, -86, -90, -91], [-84, -85, -91, -92], [-93, -94, -95, -96], [-93, -95, -97, -98], [-93, -94, -98, -99], [-93, -95, -99, -100], [-93, -94, -100, -101], [-102, -103, -104, -105], [-102, -104, -106, -107], [-102, -103, -107, -108], [-102, -104, -108, -109], [-102, -103, -109, -110], [-111, -112, -113, -114], [-111, -113, -115, -116], [-111, -112, -116, -117], [-111, -113, -117, -118], [-111, -112, -118, -119], [-120, -121, -122, -123], [-120, -122, -124, -125], [-120, -121, -125, -126], [-120, -122, -126, -127], [-120, -121, -127, -128]]}
````

### 8. P08 · run 0 · medium

- **Categoría:** Malformed syntax (won't parse)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** PARSE_ERROR
- **Diagnóstico (usa el CNF de referencia):** JSON inválido: Expecting ',' delimiter (posición 4038) [salida truncada por num_predict]

````text
{"num_vars": 18, "clauses": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24], [25, 26, 27, 28], [29, 30, 31, 32], [33, 34, 35, 36], [37, 38, 39, 40], [41, 42, 43, 44], [45, 46, 47, 48], [-49, -50, -51, -52], [-49, -51, -53, -54], [-49, -52, -53, -55], [-49, -50, -54, -55], [-50, -51, -52, -56], [-51, -52, -53, -57], [-52, -53, -54, -58], [-53, -54, -55, -59], [-54, -55, -56, -60], [-55, -56, -57, -61], [-56, -57, -58, -62], [-57, -58, -59, -63], [-58, -59, -60, -64], [-59, -60, -61, -65], [-60, -61, -62, -66], [-61, -62, -63, -67], [-62, -63, -64, -68], [-63, -64, -65, -69], [-64, -65, -66, -70], [-65, -66, -67, -71], [-66, -67, -68, -72], [-67, -68, -69, -73], [-68, -69, -70, -74], [-69, -70, -71, -75], [-70, -71, -72, -76], [-71, -72, -73, -77], [-72, -73, -74, -78], [-73, -74, -75, -79], [-74, -75, -76, -80], [-75, -76, -77, -81], [-76, -77, -78, -82], [-77, -78, -79, -83], [-78, -79, -80, -84], [-79, -80, -81, -85], [-80, -81, -82, -86], [-81, -82, -83, -87], [-82, -83, -84, -88], [-83, -84, -85, -89], [-84, -85, -86, -90], [-85, -86, -87, -91], [-86, -87, -88, -92], [-87, -88, -89, -93], [-88, -89, -90, -94], [-89, -90, -91, -95], [-90, -91, -92, -96], [-91, -92, -93, -97], [-92, -93, -94, -98], [-93, -94, -95, -99], [-94, -95, -96, -100], [-95, -96, -97, -101], [-96, -97, -98, -102], [-97, -98, -99, -103], [-98, -99, -100, -104], [-99, -100, -101, -105], [-100, -101, -102, -106], [-101, -102, -103, -107], [-102, -103, -104, -108], [-103, -104, -105, -109], [-104, -105, -106, -110], [-105, -106, -107, -111], [-106, -107, -108, -112], [-107, -108, -109, -113], [-108, -109, -110, -114], [-109, -110, -111, -115], [-110, -111, -112, -116], [-111, -112, -113, -117], [-112, -113, -114, -118], [-113, -114, -115, -119], [-114, -115, -116, -120], [-115, -116, -117, -121], [-116, -117, -118, -122], [-117, -118, -119, -123], [-118, -119, -120, -124], [-119, -120, -121, -125], [-120, -121, -122, -126], [-121, -122, -123, -127], [-122, -123, -124, -128], [-123, -124, -125, -129], [-124, -125, -126, -130], [-125, -126, -127, -131], [-126, -127, -128, -132], [-127, -128, -129, -133], [-128, -129, -130, -134], [-129, -130, -131, -135], [-130, -131, -132, -136], [-131, -132, -133, -137], [-132, -133, -134, -138], [-133, -134, -135, -139], [-134, -135, -136, -140], [-135, -136, -137, -141], [-136, -137, -138, -142], [-137, -138, -139, -143], [-138, -139, -140, -144], [-139, -140, -141, -145], [-140, -141, -142, -146], [-141, -142, -143, -147], [-142, -143, -144, -148], [-143, -144, -145, -149], [-144, -145, -146, -150], [-145, -146, -147, -151], [-146, -147, -148, -152], [-147, -148, -149, -153], [-148, -149, -150, -154], [-149, -150, -151, -155], [-150, -151, -152, -156], [-151, -152, -153, -157], [-152, -153, -154, -158], [-153, -154, -155, -159], [-154, -155, -156, -160], [-155, -156, -157, -161], [-156, -157, -158, -162], [-157, -158, -159, -163], [-158, -159, -160, -164], [-159, -160, -161, -165], [-160, -161, -162, -166], [-161, -162, -163, -167], [-162, -163, -164, -168], [-163, -164, -165, -169], [-164, -165, -166, -170], [-165, -166, -167, -171], [-166, -167, -168, -172], [-167, -168, -169, -173], [-168, -169, -170, -174], [-169, -170, -171, -175], [-170, -171, -172, -176], [-171, -172, -173, -177], [-172, -173, -174, -178], [-173, -174, -175, -179], [-174, -175, -176, -180], [-175, -176, -177, -181], [-176, -177, -178, -182], [-177, -178, -179, -183], [-178, -179, -180, -184], [-179, -180, -181, -185], [-180, -181, -182, -186], [-181, -182, -183, -187], [-182, -183, -184, -188], [-183, -184, -185, -189], [-184, -185, -186, -190], [-185, -186, -187, -191], [-186, -187, -188, -192], [-187, -188, -189, -193], [-188, -189, -190, -194], [-189, -190, -191, -195], [-190, -191, -192, -196], [-191, -192, -193, -197], [-192, -193, -194, -198], [-193, -194, -195, -199], [-194, -195, -196, -200], [-195, -196, -197, -201], [-196, -197, -198, -202], [-197, -198, -199, -203], [-198, -199, -200, -204], [-199, -200, -201, -205], [-200
````

### 9. P09 · run 0 · medium

- **Categoría:** Malformed syntax (won't parse)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** PARSE_ERROR
- **Diagnóstico (usa el CNF de referencia):** JSON inválido: Expecting value (posición 4014) [salida truncada por num_predict]

````text
{"num_vars": 21, "clauses": [[1, 2, 3, 4, 5, 6], [-1, -2, -7, -8, -9, -10], [-3, -4, -7, -8, -11, -12], [-5, -6, -7, -8, -13, -14], [-9, -10, -11, -12, -15, -16], [-11, -12, -13, -14, -17, -18], [-13, -14, -15, -16, -19, -20], [-15, -16, -17, -18, -21, -22], [-17, -18, -19, -20, -23, -24], [-19, -20, -21, -22, -25, -26], [-21, -22, -23, -24, -27, -28], [-23, -24, -25, -26, -29, -30], [-25, -26, -27, -28, -31, -32], [-27, -28, -29, -30, -33, -34], [-29, -30, -31, -32, -35, -36], [-31, -32, -33, -34, -37, -38], [-33, -34, -35, -36, -39, -40], [-35, -36, -37, -38, -41, -42], [-37, -38, -39, -40, -43, -44], [-39, -40, -41, -42, -45, -46], [-41, -42, -43, -44, -47, -48], [-43, -44, -45, -46, -49, -50], [-45, -46, -47, -48, -51, -52], [-47, -48, -49, -50, -53, -54], [-49, -50, -51, -52, -55, -56], [-51, -52, -53, -54, -57, -58], [-53, -54, -55, -56, -59, -60], [-55, -56, -57, -58, -61, -62], [-57, -58, -59, -60, -63, -64], [-59, -60, -61, -62, -65, -66], [-61, -62, -63, -64, -67, -68], [-63, -64, -65, -66, -69, -70], [-65, -66, -67, -68, -71, -72], [-67, -68, -69, -70, -73, -74], [-69, -70, -71, -72, -75, -76], [-71, -72, -73, -74, -77, -78], [-73, -74, -75, -76, -79, -80], [-75, -76, -77, -78, -81, -82], [-77, -78, -79, -80, -83, -84], [-79, -80, -81, -82, -85, -86], [-81, -82, -83, -84, -87, -88], [-83, -84, -85, -86, -89, -90], [-85, -86, -87, -88, -91, -92], [-87, -88, -89, -90, -93, -94], [-89, -90, -91, -92, -95, -96], [-91, -92, -93, -94, -97, -98], [-93, -94, -95, -96, -99, -100], [-95, -96, -97, -98, -101, -102], [-97, -98, -99, -100, -103, -104], [-99, -100, -101, -102, -105, -106], [-101, -102, -103, -104, -107, -108], [-103, -104, -105, -106, -109, -110], [-105, -106, -107, -108, -111, -112], [-107, -108, -109, -10, -113, -114], [-109, -10, -110, -10, -115, -116], [-10, -110, -10, -116, -117, -118], [-110, -10, -110, -10, -119, -120], [-10, -110, -10, -119, -121, -122], [-10, -110, -10, -119, -123, -124], [-10, -110, -10, -119, -125, -126], [-10, -110, -10, -119, -127, -128], [-10, -110, -10, -119, -129, -130], [-10, -110, -10, -119, -131, -132], [-10, -110, -10, -119, -133, -134], [-10, -110, -10, -119, -135, -136], [-10, -110, -10, -119, -137, -138], [-10, -110, -10, -119, -139, -140], [-10, -110, -10, -119, -141, -142], [-10, -110, -10, -119, -143, -144], [-10, -110, -10, -119, -145, -146], [-10, -110, -10, -119, -147, -148], [-10, -110, -10, -119, -149, -150], [-10, -110, -10, -119, -151, -152], [-10, -110, -10, -119, -153, -154], [-10, -110, -10, -119, -155, -156], [-10, -110, -10, -119, -157, -158], [-10, -110, -10, -119, -159, -160], [-10, -110, -10, -119, -161, -162], [-10, -110, -10, -119, -163, -164], [-10, -110, -10, -119, -165, -166], [-10, -110, -10, -119, -167, -168], [-10, -110, -10, -119, -169, -170], [-10, -110, -10, -119, -171, -172], [-10, -110, -10, -119, -173, -174], [-10, -110, -10, -119, -175, -176], [-10, -110, -10, -119, -177, -178], [-10, -110, -10, -119, -179, -180], [-10, -110, -10, -119, -181, -182], [-10, -110, -10, -119, -183, -184], [-10, -110, -10, -119, -185, -186], [-10, -110, -10, -119, -187, -188], [-10, -110, -10, -119, -189, -190], [-10, -110, -10, -119, -191, -192], [-10, -110, -10, -119, -193, -194], [-10, -110, -10, -119, -195, -196], [-10, -110, -10, -119, -197, -198], [-10, -110, -10, -119, -199, -200], [-10, -110, -10, -119, -201, -202], [-10, -110, -10, -119, -203, -204], [-10, -110, -10, -119, -205, -206], [-10, -110, -10, -119, -207, -208], [-10, -110, -10, -119, -209, -210], [-10, -110, -10, -119, -211, -212], [-10, -110, -10, -119, -213, -214], [-10, -110, -10, -119, -215, -216], [-10, -110, -10, -119, -217, -218], [-10, -110, -10, -119, -219, -220], [-10, -110, -10, -119, -221, -222], [-10, -110, -10, -119, -223, -224], [-10, -110, -10, -119, -225, -226], [-10, -110, -10, -119, -227, -228], [-10, -110, -10, -119, -229, -230], [-10, -110, -10, -119, -231, -232], [-10, -110, -10, -119, -233, -234], [-10, -110, -10, -119, -235, -236], [-10, -110, -10, -119, -237, -238], [-10, -110, -10, -
````

### 10. P10 · run 0 · medium

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice E tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice F tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice G tiene 2 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E', 'F', 'G']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G']; restricción de arista omitida por completo: ['A-B', 'A-C', 'A-F', 'B-C', 'B-E', 'C-E', 'D-E', 'D-F', 'E-F', 'F-G']; 24 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 21, "clauses": [[1, 2, 3, 4, 5, 6], [-1, -2, -7, -8, -9, -10, -11], [-3, -4, -12, -13, -14, -15, -16], [-5, -6, -17, -18, -19, -20, -21], [1, -2, 7, -8, 13, -14, 19, -20, 21], [-1, 2, 8, -7, 14, -13, 20, -19, 21], [3, -4, 9, -10, 15, -16, 21], [-3, 4, -9, 10, -15, 16, 21], [5, -6, 11, -12, 17, -18, 21], [-5, 6, -11, 12, -17, 18, 21], [7, -8, 12, -9, 19, -10, 20, -11, 21], [-7, 8, -12, 9, -19, 10, -20, 11, 21], [9, -10, 13, -14, 20, -15, 21], [-9, 10, -13, 14, -20, 15, 21], [11, -12, 14, -15, 21], [-11, 12, -14, 15, 21], [15, -16, 21], [-15, 16, 21], [17, -18, 21], [-17, 18, 21], [19, -20, 21], [-19, 20, 21], [20, -21, 21], [-20, 21, 21]]}
````

### 11. P11 · run 0 · medium

- **Categoría:** Malformed syntax (won't parse)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** PARSE_ERROR
- **Diagnóstico (usa el CNF de referencia):** JSON inválido: Expecting value (posición 3641) [salida truncada por num_predict]

````text
{"num_vars": 21, "clauses": [[1, 2, 3, 4, 5, 6], [-1, -2, -7, -8, -9, -10], [-3, -4, -7, -8, -11, -12], [4, 5, 9, 10, 11, 12], [-6, -7, -13, -14, -15, -16], [7, 8, 13, 14, 15, 16], [-9, -10, -17, -18, -19, -20], [10, 11, 19, 20, 21, -21], [-11, -12, -17, -18, -21, 21], [12, 13, 18, 19, -22, 22], [-14, -15, -17, -18, 22, 23], [15, 16, 19, 20, -24, 24], [-16, -17, -19, -20, 24, 25], [17, 18, 21, 22, -26, 26], [-19, -20, -21, -22, 26, 27], [19, 20, 23, 24, -28, 28], [-21, -22, -23, -24, 28, 29], [21, 22, 25, 26, -30, 30], [-23, -24, -25, -26, 30, 31], [23, 24, 27, 28, -32, 32], [-25, -26, -27, -28, 32, 33], [25, 26, 29, 30, -34, 34], [-27, -28, -29, -30, 34, 35], [27, 28, 31, 32, -36, 36], [-29, -30, -31, -32, 36, 37], [29, 30, 33, 34, -38, 38], [-31, -32, -33, -34, 38, 39], [31, 32, 35, 36, -40, 40], [-33, -34, -35, -36, 40, 41], [33, 34, 37, 38, -42, 42], [-35, -36, -37, -38, 42, 43], [35, 36, 39, 40, -44, 44], [-37, -38, -39, -40, 44, 45], [37, 38, 41, 42, -46, 46], [-39, -40, -41, -42, 46, 47], [39, 40, 43, 44, -48, 48], [-41, -42, -43, -44, 48, 49], [41, 42, 45, 46, -50, 50], [-43, -44, -45, -46, 50, 51], [43, 44, 47, 48, -52, 52], [-45, -46, -47, -48, 52, 53], [45, 46, 49, 50, -54, 54], [-47, -48, -49, -50, 54, 55], [47, 48, 51, 52, -56, 56], [-49, -50, -51, -52, 56, 57], [49, 50, 53, 54, -58, 58], [-51, -52, -53, -54, 58, 59], [51, 52, 55, 56, -60, 60], [-53, -54, -55, -56, 60, 61], [53, 54, 57, 58, -62, 62], [-55, -56, -57, -58, 62, 63], [55, 56, 59, 60, -64, 64], [-57, -58, -59, -60, 64, 65], [57, 58, 61, 62, -66, 66], [-59, -60, -61, -62, 66, 67], [59, 60, 63, 64, -68, 68], [-61, -62, -63, -64, 68, 69], [61, 62, 65, 66, -70, 70], [-63, -64, -65, -66, 70, 71], [63, 64, 67, 68, -72, 72], [-65, -66, -67, -68, 72, 73], [65, 66, 69, 70, -74, 74], [-67, -68, -69, -70, 74, 75], [67, 68, 71, 72, -76, 76], [-69, -70, -71, -72, 76, 77], [69, 70, 73, 74, -78, 78], [-71, -72, -73, -74, 78, 79], [71, 72, 75, 76, -80, 80], [-73, -74, -75, -76, 80, 81], [73, 74, 77, 78, -82, 82], [-75, -76, -77, -78, 82, 83], [75, 76, 79, 80, -84, 84], [-77, -78, -79, -80, 84, 85], [77, 78, 81, 82, -86, 86], [-79, -80, -81, -82, 86, 87], [79, 80, 83, 84, -88, 88], [-81, -82, -83, -84, 88, 89], [81, 82, 85, 86, -90, 90], [-83, -84, -85, -86, 90, 91], [83, 84, 87, 88, -92, 92], [-85, -86, -87, -88, 92, 93], [85, 86, 89, 90, -94, 94], [-87, -88, -89, -90, 94, 95], [87, 88, 91, 92, -96, 96], [-89, -90, -91, -92, 96, 97], [89, 90, 93, 94, -98, 98], [-91, -92, -93, -94, 98, 99], [91, 92, 95, 96, -100, 100], [-93, -94, -95, -96, 100, 101], [93, 94, 97, 98, -102, 102], [-95, -96, -97, -98, 102, 103], [95, 96, 99, 100, -104, 104], [-97, -98, -99, -100, 104, 105], [97, 98, 101, 102, -106, 106], [-99, -100, -101, -102, 106, 107], [99, 100, 103, 104, -108, 108], [-101, -102, -103, -104, 108, 109], [101, 102, 105, 106, -110, 110], [-103, -104, -105, -106, 110, 111], [103, 104, 107, 108, -112, 112], [-105, -106, -107, -108, 112, 113], [105, 106, 109, 110, -114, 114], [-107, -108, -109, -110, 114, 115], [107, 108, 111, 112, -116, 116], [-109, -110, -111, -112, 116, 117], [109, 110, 113, 114, -118, 118], [-111, -112, -113, -114, 118, 119], [111, 112, 115, 116, -120, 120], [-113, -114, -115, -116, 120, 121], [113, 114, 117, 118, -122, 122], [-115, -116, -117, -118, 122, 123], [115, 116, 119, 120, -124, 124], [-117, -118, -119, -120, 124, 125], [117, 118, 121, 122, -126, 126], [-119, -120, -121, -122, 126, 127], [119, 120, 123, 124, -128, 128], [-121, -122, -123, -124, 128, 129], [121, 122, 125, 126, -130, 130], [-123, -124, -125, -126, 130, 131], [123, 124, 127, 128, -132, 132], [-125, -126, -127, -128, 132, 133], [
````

### 12. P12 · run 0 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 8: -25 (debe ser entero no nulo con |lit| <= 24)

````text
{"num_vars": 24, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24], [-25, -26, -27], [-28, -29, -30], [-31, -32, -33], [-34, -35, -36], [-37, -38, -39], [-40, -41, -42], [-43, -44, -45], [-46, -47, -48], [-49, -50, -51], [-52, -53, -54], [-55, -56, -57], [-58, -59, -60], [-61, -62, -63], [-64, -65, -66], [-67, -68, -69], [-70, -71, -72], [-73, -74, -75], [-76, -77, -78], [-79, -80, -81], [-82, -83, -84], [-85, -86, -87], [-88, -89, -90], [-91, -92, -93], [-94, -95, -96], [-97, -98, -99], [-100, -101, -102], [-103, -104, -105], [-106, -107, -108], [-109, -110, -111], [-112, -113, -114], [-115, -116, -117], [-118, -119, -120], [-121, -122, -123], [-124, -125, -126], [-127, -128, -129], [-130, -131, -132], [-133, -134, -135], [-136, -137, -138], [-139, -140, -141], [-142, -143, -144], [-145, -146, -147], [-148, -149, -150], [-151, -152, -153], [-154, -155, -156], [-157, -158, -159], [-160, -161, -162], [-163, -164, -165], [-166, -167, -168], [-169, -170, -171], [-172, -173, -174], [-175, -176, -177], [-178, -179, -180], [-181, -182, -183], [-184, -185, -186], [-187, -188, -189], [-190, -191, -192], [-193, -194, -195], [-196, -197, -198], [-199, -200, -201], [-202, -203, -204], [-205, -206, -207], [-208, -209, -210], [-211, -212, -213], [-214, -215, -216], [-217, -218, -219], [-220, -221, -222], [-223, -224, -225], [-226, -227, -228], [-229, -230, -231], [-232, -233, -234], [-235, -236, -237], [-238, -239, -240]]}
````

### 13. P13 · run 0 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 8: -25 (debe ser entero no nulo con |lit| <= 24)

````text
{"num_vars": 24, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24], [-25, -26, -27], [-28, -29, -30], [-31, -32, -33], [-34, -35, -36], [-37, -38, -39], [-40, -41, -42], [-43, -44, -45], [-46, -47, -48], [-49, -50, -51], [-52, -53, -54], [-55, -56, -57], [-58, -59, -60], [-61, -62, -63], [-64, -65, -66], [-67, -68, -69], [-70, -71, -72], [-73, -74, -75], [-76, -77, -78], [-79, -80, -81], [-82, -83, -84], [-85, -86, -87], [-88, -89, -90], [-91, -92, -93], [-94, -95, -96], [-97, -98, -99], [-100, -101, -102], [-103, -104, -105], [-106, -107, -108], [-109, -110, -111], [-112, -113, -114], [-115, -116, -117], [-118, -119, -120], [-121, -122, -123], [-124, -125, -126], [-127, -128, -129], [-130, -131, -132], [-133, -134, -135], [-136, -137, -138], [-139, -140, -141], [-142, -143, -144], [-145, -146, -147], [-148, -149, -150], [-151, -152, -153], [-154, -155, -156], [-157, -158, -159], [-160, -161, -162], [-163, -164, -165], [-166, -167, -168], [-169, -170, -171], [-172, -173, -174], [-175, -176, -177], [-178, -179, -180], [-181, -182, -183], [-184, -185, -186], [-187, -188, -189], [-190, -191, -192], [-193, -194, -195], [-196, -197, -198], [-199, -200, -201], [-202, -203, -204], [-205, -206, -207], [-208, -209, -210], [-211, -212, -213], [-214, -215, -216], [-217, -218, -219], [-220, -221, -222], [-223, -224, -225], [-226, -227, -228], [-229, -230, -231], [-232, -233, -234], [-235, -236, -237], [-238, -239, -240]]}
````

### 14. P14 · run 0 · hard

- **Categoría:** Valid syntax, under-constrained (wrong solution returned) — silent
- **¿Detectable sin ground truth?** No (needs a verifier / reference)
- **Estado del solver/validador:** SAT
- **Diagnóstico (usa el CNF de referencia):** falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']; restricción de arista omitida por completo: ['A-B', 'A-C', 'A-F', 'B-C', 'B-D', 'B-E', 'B-F', 'B-G', 'C-D', 'C-G', 'D-E', 'D-F', 'E-G', 'F-G']

````text
{"num_vars": 24, "clauses": [[1, 2, 3], [-1, -2], [4, 5, 6], [-4, -5], [7, 8, 9], [-7, -8], [10, 11, 12], [-10, -11], [13, 14, 15], [-13, -14], [16, 17, 18], [-16, -17], [19, 20, 21], [-19, -20], [22, 23, 24], [-22, -23]]}
````

### 15. P15 · run 0 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 8: -25 (debe ser entero no nulo con |lit| <= 24)

````text
{"num_vars": 24, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24], [-25, -26, -27], [-28, -29, -30], [-31, -32, -33], [-34, -35, -36], [-37, -38, -39], [-40, -41, -42], [-43, -44, -45], [-46, -47, -48], [-49, -50, -51], [-52, -53, -54], [-55, -56, -57], [-58, -59, -60], [-61, -62, -63], [-64, -65, -66], [-67, -68, -69], [-70, -71, -72], [-73, -74, -75], [-76, -77, -78], [-79, -80, -81], [-82, -83, -84], [-85, -86, -87], [-88, -89, -90], [-91, -92, -93], [-94, -95, -96], [-97, -98, -99], [-100, -101, -102], [-103, -104, -105], [-106, -107, -108], [-109, -110, -111], [-112, -113, -114], [-115, -116, -117], [-118, -119, -120], [-121, -122, -123], [-124, -125, -126], [-127, -128, -129], [-130, -131, -132], [-133, -134, -135], [-136, -137, -138], [-139, -140, -141], [-142, -143, -144], [-145, -146, -147], [-148, -149, -150], [-151, -152, -153], [-154, -155, -156], [-157, -158, -159], [-160, -161, -162], [-163, -164, -165], [-166, -167, -168], [-169, -170, -171], [-172, -173, -174], [-175, -176, -177], [-178, -179, -180], [-181, -182, -183], [-184, -185, -186], [-187, -188, -189], [-190, -191, -192], [-193, -194, -195], [-196, -197, -198], [-199, -200, -201], [-202, -203, -204], [-205, -206, -207], [-208, -209, -210], [-211, -212, -213], [-214, -215, -216], [-217, -218, -219], [-220, -221, -222], [-223, -224, -225], [-226, -227, -228], [-229, -230, -231], [-232, -233, -234], [-235, -236, -237], [-238, -239, -240]]}
````

### 16. P16 · run 0 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 12: 28 (debe ser entero no nulo con |lit| <= 27)

````text
{"num_vars": 27, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24], [25, 26, 27], [-19, -20, -21], [-22, -23, -24], [-25, -26, -27], [28, 29, 30], [31, 32, 33], [34, 35, 36], [37, 38, 39], [40, 41, 42], [43, 44, 45], [46, 47, 48], [49, 50, 51], [52, 53, 54], [55, 56, 57], [58, 59, 60], [61, 62, 63], [64, 65, 66], [67, 68, 69], [70, 71, 72], [73, 74, 75], [76, 77, 78], [79, 80, 81], [82, 83, 84], [85, 86, 87], [88, 89, 90], [-82, -83, -84], [-85, -86, -87], [-88, -89, -90]]}
````

### 17. P17 · run 0 · hard

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice G tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice I tiene 3 colores asignados en el modelo (debe tener exactamente 1) | falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']; restricción de arista omitida por completo: ['A-B', 'A-C', 'A-E', 'A-F', 'A-G', 'A-H', 'A-I', 'B-C', 'B-F', 'B-H', 'C-D', 'C-E', 'C-G', 'C-I', 'D-E', 'D-F', 'D-G', 'D-H', 'D-I', 'E-F', 'E-H', 'F-G', 'F-I', 'G-H', 'H-I']; 23 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 27, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24], [25, 26, 27], [-1, -4, -7], [-2, -5, -8], [-3, -6, -9], [-10, -13, -16], [-11, -14, -17], [-12, -15, -18], [-19, -22, -25], [-20, -23, -26], [-21, -24, -27], [4, -5, -6], [5, -6, -7], [6, -7, -8], [7, -8, -9], [16, -17, -18], [17, -18, -19], [18, -19, -20], [19, -20, -21], [26, -27, -2], [27, -2, -3], [2, -3, -4], [3, -4, -5], [4, -5, -6], [5, -6, -7], [6, -7, -8], [7, -8, -9], [25, -26, -2], [26, -2, -3], [2, -3, -4], [3, -4, -5], [4, -5, -6], [5, -6, -7], [6, -7, -8], [7, -8, -9]]}
````

### 18. P18 · run 0 · hard

- **Categoría:** Valid syntax, under-constrained (wrong solution returned) — silent
- **¿Detectable sin ground truth?** No (needs a verifier / reference)
- **Estado del solver/validador:** SAT
- **Diagnóstico (usa el CNF de referencia):** falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']; restricción de arista omitida por completo: ['A-B', 'A-F', 'A-H', 'B-C', 'B-D', 'B-F', 'B-G', 'B-J', 'C-D', 'C-H', 'C-J', 'D-F', 'D-H', 'D-I', 'E-F', 'E-H', 'F-G', 'F-H', 'F-I', 'F-J', 'G-H', 'H-J', 'I-J']

````text
{"num_vars": 30, "clauses": [[1, 2, 3], [-1, -2], [4, 5, 6], [-4, -5], [7, 8, 9], [-7, -8], [10, 11, 12], [-10, -11], [13, 14, 15], [-13, -14], [16, 17, 18], [-16, -17], [19, 20, 21], [-19, -20], [22, 23, 24], [-22, -23], [25, 26, 27], [-25, -26], [28, 29, 30], [-28, -29]]}
````

### 19. P19 · run 0 · hard

- **Categoría:** Valid syntax, under-constrained (wrong solution returned) — silent
- **¿Detectable sin ground truth?** No (needs a verifier / reference)
- **Estado del solver/validador:** SAT
- **Diagnóstico (usa el CNF de referencia):** falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']; restricción de arista omitida por completo: ['A-B', 'A-C', 'A-D', 'A-F', 'A-G', 'A-H', 'A-I', 'B-C', 'B-E', 'B-J', 'C-E', 'C-G', 'C-I', 'D-E', 'D-F', 'D-G', 'D-I', 'E-F', 'E-I', 'E-J', 'F-H', 'F-J', 'G-H', 'H-I', 'I-J']

````text
{"num_vars": 30, "clauses": [[1, 2, 3], [-1, -2], [4, 5, 6], [-4, -5], [7, 8, 9], [-7, -8], [10, 11, 12], [-10, -11], [13, 14, 15], [-13, -14], [16, 17, 18], [-16, -17], [19, 20, 21], [-19, -20], [22, 23, 24], [-22, -23], [25, 26, 27], [-25, -26], [28, 29, 30], [-28, -29]]}
````

### 20. P20 · run 0 · hard

- **Categoría:** Valid syntax, under-constrained (wrong solution returned) — silent
- **¿Detectable sin ground truth?** No (needs a verifier / reference)
- **Estado del solver/validador:** SAT
- **Diagnóstico (usa el CNF de referencia):** falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']; restricción de arista omitida por completo: ['A-B', 'A-C', 'A-F', 'A-H', 'B-C', 'B-D', 'B-E', 'B-G', 'C-D', 'C-H', 'C-J', 'D-E', 'D-H', 'E-H', 'E-J', 'F-G', 'F-H', 'F-J', 'G-H', 'G-I', 'H-I', 'I-J']

````text
{"num_vars": 30, "clauses": [[1, 2, 3], [-1, -2], [4, 5, 6], [-4, -5], [7, 8, 9], [-7, -8], [10, 11, 12], [-10, -11], [13, 14, 15], [-13, -14], [16, 17, 18], [-16, -17], [19, 20, 21], [-19, -20], [22, 23, 24], [-22, -23], [25, 26, 27], [-25, -26], [28, 29, 30], [-28, -29]]}
````

### 21. P01 · run 1 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 2 colores asignados en el modelo (debe tener exactamente 1) | falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D']; restricción de arista omitida por completo: ['A-B', 'A-D', 'B-C', 'C-D']; 12 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 12, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [1, -2, -4], [2, -1, -5], [3, -1, -6], [4, -2, -7], [5, -3, -8], [6, -3, -9], [7, -4, -10], [8, -4, -11], [9, -5, -12], [10, -6, -12], [11, -6, -11], [12, -5, -10]]}
````

### 22. P02 · run 1 · easy

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 5: -17 (debe ser entero no nulo con |lit| <= 15)

````text
{"num_vars": 15, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [-17, -18, -19], [-20, -21, -22], [-23, -24, -25], [-26, -27, -28], [-29, -30, -31], [-32, -33, -34], [-35, -36, -37], [-38, -39, -40], [-41, -42, -43], [-44, -45, -46]]}
````

### 23. P03 · run 1 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 2 colores asignados en el modelo (debe tener exactamente 1) | falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D']; restricción de arista omitida por completo: ['A-B', 'A-D', 'B-C']; 8 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 12, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [1, -2], [2, -1], [4, -5], [5, -4], [7, -8], [8, -7], [10, -11], [11, -10]]}
````

### 24. P04 · run 1 · easy

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 5: -17 (debe ser entero no nulo con |lit| <= 15)

````text
{"num_vars": 15, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [-17, -18, -19], [-20, -21, -22], [-23, -24, -25], [-26, -27, -28], [-29, -30, -31], [-32, -33, -34], [-35, -36, -37], [-38, -39, -40], [-41, -42, -43], [-44, -45, -46]]}
````

### 25. P05 · run 1 · easy

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 5: -17 (debe ser entero no nulo con |lit| <= 15)

````text
{"num_vars": 15, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [-17, -18, -19], [-20, -21, -22], [-23, -24, -25], [-26, -27, -28], [-29, -30, -31], [-32, -33, -34], [-35, -36, -37], [-38, -39, -40], [-41, -42, -43], [-44, -45, -46]]}
````

### 26. P06 · run 1 · easy

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 6: -19 (debe ser entero no nulo con |lit| <= 18)

````text
{"num_vars": 18, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [-19, -20, -21], [-22, -23, -24], [-25, -26, -27], [-28, -29, -30], [-31, -32, -33], [-34, -35, -36], [-37, -38, -39], [-40, -41, -42], [-43, -44, -45], [-46, -47, -48], [-49, -50, -51]]}
````

### 27. P07 · run 1 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 6: -19 (debe ser entero no nulo con |lit| <= 18)

````text
{"num_vars": 18, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [-19, -20, -21], [-22, -23, -24], [-25, -26, -27], [-28, -29, -30], [-31, -32, -33], [-34, -35, -36], [-37, -38, -39], [-40, -41, -42], [-43, -44, -45], [-46, -47, -48], [-49, -50, -51]]}
````

### 28. P08 · run 1 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 6: -19 (debe ser entero no nulo con |lit| <= 18)

````text
{"num_vars": 18, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [-19, -20, -21], [-22, -23, -24], [-25, -26, -27], [-28, -29, -30], [-31, -32, -33], [-34, -35, -36], [-37, -38, -39], [-40, -41, -42], [-43, -44, -45], [-46, -47, -48], [-49, -50, -51]]}
````

### 29. P09 · run 1 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 14: 22 (debe ser entero no nulo con |lit| <= 21)

````text
{"num_vars": 21, "clauses": [[1, 2, 3], [-1, -2], [4, 5, 6], [-4, -5], [7, 8, 9], [-7, -8], [10, 11, 12], [-10, -11], [13, 14, 15], [-13, -14], [16, 17, 18], [-16, -17], [19, 20, 21], [-19, -20], [22, 23, 24], [-22, -23], [25, 26, 27], [-25, -26], [28, 29, 30], [-28, -29], [31, 32, 33], [-31, -32], [34, 35, 36], [-34, -35], [37, 38, 39], [-37, -38], [40, 41, 42], [-40, -41], [43, 44, 45], [-43, -44], [46, 47, 48], [-46, -47], [49, 50, 51], [-49, -50], [52, 53, 54], [-52, -53], [55, 56, 57], [-55, -56], [58, 59, 60], [-58, -59], [61, 62, 63], [-61, -62], [64, 65, 66], [-64, -65], [67, 68, 69], [-67, -68], [70, 71, 72], [-70, -71], [73, 74, 75], [-73, -74], [76, 77, 78], [-76, -77], [79, 80, 81], [-79, -80], [82, 83, 84], [-82, -83], [85, 86, 87], [-85, -86], [88, 89, 90], [-88, -89], [91, 92, 93], [-91, -92], [94, 95, 96], [-94, -95], [97, 98, 99], [-97, -98], [100, 101, 102], [-100, -101], [103, 104, 105], [-103, -104], [106, 107, 108], [-106, -107], [109, 110, 111], [-109, -110], [112, 113, 114], [-112, -113], [115, 116, 117], [-115, -116], [118, 119, 120], [-118, -119], [121, 122, 123], [-121, -122], [124, 125, 126], [-124, -125], [127, 128, 129], [-127, -128], [130, 131, 132], [-130, -131], [133, 134, 135], [-133, -134], [136, 137, 138], [-136, -137], [139, 140, 141], [-139, -140], [142, 143, 144], [-142, -143], [145, 146, 147], [-145, -146], [148, 149, 150], [-148, -149], [151, 152, 153], [-151, -152], [154, 155, 156], [-154, -155], [157, 158, 159], [-157, -158], [160, 161, 162], [-160, -161], [163, 164, 165], [-163, -164], [166, 167, 168], [-166, -167], [169, 170, 171], [-169, -170], [172, 173, 174], [-172, -173], [175, 176, 177], [-175, -176], [178, 179, 180], [-178, -179], [181, 182, 183], [-181, -182], [184, 185, 186], [-184, -185], [187, 188, 189], [-187, -188], [190, 191, 192], [-190, -191], [193, 194, 195], [-193, -194], [196, 197, 198], [-196, -197], [199, 200, 201], [-199, -200], [202, 203, 204], [-202, -203], [205, 206, 207], [-205, -206], [208, 209, 210], [-208, -209]]}
````

### 30. P10 · run 1 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 1: 22 (debe ser entero no nulo con |lit| <= 21)

````text
{"num_vars": 21, "clauses": [[1, 2, 3], [-1, -2, 22, 23], [2, 22, 24], [-2, -22], [3, 23, 25], [-3, -23], [4, 26, 27], [-4, -26], [5, 28, 29], [-5, -28], [6, 30, 31], [-6, -30], [7, 32, 33], [-7, -32], [8, 34, 35], [-8, -34], [9, 36, 37], [-9, -36], [10, 38, 39], [-10, -38], [11, 40, 41], [-11, -40], [12, 42, 43], [-12, -42], [13, 44, 45], [-13, -44], [14, 46, 47], [-14, -46], [15, 48, 49], [-15, -48], [16, 50, 51], [-16, -50], [17, 52, 53], [-17, -52], [18, 54, 55], [-18, -54], [19, 56, 57], [-19, -56], [20, 58, 59], [-20, -58], [21, 60, 61], [-21, -60]]}
````

### 31. P11 · run 1 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 14: 22 (debe ser entero no nulo con |lit| <= 21)

````text
{"num_vars": 21, "clauses": [[1, 2, 3], [-1, -2], [4, 5, 6], [-4, -5], [7, 8, 9], [-7, -8], [10, 11, 12], [-10, -11], [13, 14, 15], [-13, -14], [16, 17, 18], [-16, -17], [19, 20, 21], [-19, -20], [22, 23, 24], [-22, -23], [25, 26, 27], [-25, -26], [28, 29, 30], [-28, -29], [31, 32, 33], [-31, -32], [34, 35, 36], [-34, -35], [37, 38, 39], [-37, -38], [40, 41, 42], [-40, -41], [43, 44, 45], [-43, -44], [46, 47, 48], [-46, -47], [49, 50, 51], [-49, -50], [52, 53, 54], [-52, -53], [55, 56, 57], [-55, -56], [58, 59, 60], [-58, -59], [61, 62, 63], [-61, -62], [64, 65, 66], [-64, -65], [67, 68, 69], [-67, -68], [70, 71, 72], [-70, -71], [73, 74, 75], [-73, -74], [76, 77, 78], [-76, -77], [79, 80, 81], [-79, -80], [82, 83, 84], [-82, -83], [85, 86, 87], [-85, -86], [88, 89, 90], [-88, -89], [91, 92, 93], [-91, -92], [94, 95, 96], [-94, -95], [97, 98, 99], [-97, -98], [100, 101, 102], [-100, -101], [103, 104, 105], [-103, -104], [106, 107, 108], [-106, -107], [109, 110, 111], [-109, -110], [112, 113, 114], [-112, -113], [115, 116, 117], [-115, -116], [118, 119, 120], [-118, -119], [121, 122, 123], [-121, -122], [124, 125, 126], [-124, -125], [127, 128, 129], [-127, -128], [130, 131, 132], [-130, -131], [133, 134, 135], [-133, -134], [136, 137, 138], [-136, -137], [139, 140, 141], [-139, -140], [142, 143, 144], [-142, -143], [145, 146, 147], [-145, -146], [148, 149, 150], [-148, -149], [151, 152, 153], [-151, -152], [154, 155, 156], [-154, -155], [157, 158, 159], [-157, -158], [160, 161, 162], [-160, -161], [163, 164, 165], [-163, -164], [166, 167, 168], [-166, -167], [169, 170, 171], [-169, -170], [172, 173, 174], [-172, -173], [175, 176, 177], [-175, -176], [178, 179, 180], [-178, -179], [181, 182, 183], [-181, -182], [184, 185, 186], [-184, -185], [187, 188, 189], [-187, -188], [190, 191, 192], [-190, -191], [193, 194, 195], [-193, -194], [196, 197, 198], [-196, -197], [199, 200, 201], [-199, -200], [202, 203, 204], [-202, -203], [205, 206, 207], [-205, -206], [208, 209, 210], [-208, -209]]}
````

### 32. P12 · run 1 · medium

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice B tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice H tiene 0 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']; restricción de arista omitida por completo: ['A-B', 'B-C', 'C-D', 'C-F', 'D-E', 'D-F', 'E-G', 'F-G', 'G-H']; 9 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 24, "clauses": [[1, 2, 3, -4, -5], [4, 5, -6, -7], [6, 7, -8, -9], [9, 10, -11, -12], [12, 13, -14, -15], [15, 16, -17, -18], [18, 19, -20, -21], [21, 22, -23, -24], [1, 2, -3, -4], [4, 5, -6, -7], [6, 7, -8, -9], [9, 10, -11, -12], [12, 13, -14, -15], [15, 16, -17, -18], [18, 19, -20, -21], [21, 22, -23, -24]]}
````

### 33. P13 · run 1 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 7: -25 (debe ser entero no nulo con |lit| <= 24)

````text
{"num_vars": 24, "clauses": [[1, 2, 3, -4, -5], [4, 5, -6, -7], [7, 8, -9, -10], [10, 11, -12, -13], [13, 14, -15, -16], [16, 17, -18, -19], [19, 20, -21, -22], [22, 23, -24, -25], [25, 26, -27, -28], [28, 29, -30, -31], [31, 32, -33, -34], [34, 35, -36, -37], [37, 38, -39, -40], [40, 41, -42, -43], [43, 44, -45, -46], [46, 47, -48, -49], [49, 50, -51, -52], [52, 53, -54, -55], [55, 56, -57, -58], [58, 59, -60, -61], [61, 62, -63, -64], [64, 65, -66, -67], [67, 68, -69, -70], [69, 70, -71, -72], [72, 73, -74, -75], [75, 76, -77, -78], [78, 79, -80, -81], [81, 82, -83, -84], [84, 85, -86, -87], [87, 88, -89, -90], [89, 90, -91, -92], [92, 93, -94, -95], [95, 96, -97, -98], [98, 99, -100, -101], [101, 102, -103, -104], [104, 105, -106, -107], [107, 108, -109, -110], [110, 111, -112, -113], [113, 114, -115, -116], [116, 117, -118, -119], [119, 120, -121, -122], [122, 123, -124, -125], [125, 126, -127, -128], [128, 129, -130, -131], [131, 132, -133, -134], [134, 135, -136, -137], [137, 138, -139, -140], [140, 141, -142, -143], [143, 144, -145, -146], [146, 147, -148, -149], [149, 150, -151, -152], [152, 153, -154, -155], [155, 156, -157, -158], [158, 159, -160, -161], [161, 162, -163, -164], [164, 165, -166, -167], [167, 168, -169, -170], [169, 170, -171, -172], [172, 173, -174, -175], [175, 176, -177, -178], [178, 179, -180, -181], [181, 182, -183, -184], [184, 185, -186, -187], [187, 188, -189, -190], [189, 190, -191, -192], [192, 193, -194, -195], [195, 196, -197, -198], [198, 199, -200, -201], [201, 202, -203, -204], [204, 205, -206, -207], [207, 208, -209, -210], [210, 211, -212, -213], [213, 214, -215, -216], [216, 217, -218, -219], [219, 220, -221, -222], [222, 223, -224, -225], [225, 226, -227, -228], [228, 229, -230, -231], [231, 232, -233, -234], [234, 235, -236, -237], [237, 238, -239, -240], [240, 241, -242, -243]]}
````

### 34. P14 · run 1 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 1: 25 (debe ser entero no nulo con |lit| <= 24)

````text
{"num_vars": 24, "clauses": [[1, 2, 3], [-1, -2, 25], [2, 25, 26], [-2, -25], [3, 27, 28], [-3, -27], [4, 29, 30], [-4, -29], [5, 31, 32], [-5, -31], [6, 33, 34], [-6, -33], [7, 35, 36], [-7, -35], [8, 37, 38], [-8, -37], [9, 39, 40], [-9, -39], [10, 41, 42], [-10, -41], [11, 43, 44], [-11, -43], [12, 45, 46], [-12, -45], [13, 47, 48], [-13, -47], [14, 49, 50], [-14, -49], [15, 51, 52], [-15, -51], [16, 53, 54], [-16, -53], [17, 55, 56], [-17, -55], [18, 57, 58], [-18, -57], [19, 59, 60], [-19, -59], [20, 61, 62], [-20, -61], [21, 63, 64], [-21, -63], [22, 65, 66], [-22, -65], [23, 67, 68], [-23, -67], [24, 69, 70], [-24, -69]]}
````

### 35. P15 · run 1 · hard

- **Categoría:** Malformed syntax (won't parse)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** PARSE_ERROR
- **Diagnóstico (usa el CNF de referencia):** JSON inválido: Expecting ',' delimiter (posición 4121) [salida truncada por num_predict]

````text
{"num_vars": 24, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24], [-25, -26, -27], [-28, -29, -30], [-31, -32, -33], [-34, -35, -36], [-37, -38, -39], [-40, -41, -42], [-43, -44, -45], [-46, -47, -48], [-49, -50, -51], [-52, -53, -54], [-55, -56, -57], [-58, -59, -60], [-61, -62, -63], [-64, -65, -66], [-67, -68, -69], [-70, -71, -72], [-73, -74, -75], [-76, -77, -78], [-79, -80, -81], [-82, -83, -84], [-85, -86, -87], [-88, -89, -90], [-91, -92, -93], [-94, -95, -96], [-97, -98, -99], [-100, -101, -102], [-103, -104, -105], [-106, -107, -108], [-109, -110, -111], [-112, -113, -114], [-115, -116, -117], [-118, -119, -120], [-121, -122, -123], [-124, -125, -126], [-127, -128, -129], [-130, -131, -132], [-133, -134, -135], [-136, -137, -138], [-139, -140, -141], [-142, -143, -144], [-145, -146, -147], [-148, -149, -150], [-151, -152, -153], [-154, -155, -156], [-157, -158, -159], [-160, -161, -162], [-163, -164, -165], [-166, -167, -168], [-169, -170, -171], [-172, -173, -174], [-175, -176, -177], [-178, -179, -180], [-181, -182, -183], [-184, -185, -186], [-187, -188, -189], [-190, -191, -192], [-193, -194, -195], [-196, -197, -198], [-199, -200, -201], [-202, -203, -204], [-205, -206, -207], [-208, -209, -210], [-211, -212, -213], [-214, -215, -216], [-217, -218, -219], [-220, -221, -222], [-223, -224, -225], [-226, -227, -228], [-229, -230, -231], [-232, -233, -234], [-235, -236, -237], [-238, -239, -240], [-241, -242, -243], [-244, -245, -246], [-247, -248, -249], [-250, -251, -252], [-253, -254, -255], [-256, -257, -258], [-259, -260, -261], [-262, -263, -264], [-265, -266, -267], [-268, -269, -270], [-271, -272, -273], [-274, -275, -276], [-277, -278, -279], [-280, -281, -282], [-283, -284, -285], [-286, -287, -288], [-289, -290, -291], [-292, -293, -294], [-295, -296, -297], [-298, -299, -300], [-301, -302, -303], [-304, -305, -306], [-307, -308, -309], [-310, -311, -312], [-313, -314, -315], [-316, -317, -318], [-319, -320, -321], [-322, -323, -324], [-325, -326, -327], [-328, -329, -330], [-331, -332, -333], [-334, -335, -336], [-337, -338, -339], [-340, -341, -342], [-343, -344, -345], [-346, -347, -348], [-349, -350, -351], [-352, -353, -354], [-355, -356, -357], [-358, -359, -360], [-361, -362, -363], [-364, -365, -366], [-367, -368, -369], [-370, -371, -372], [-373, -374, -375], [-376, -377, -378], [-379, -380, -381], [-382, -383, -384], [-385, -386, -387], [-388, -389, -390], [-391, -392, -393], [-394, -395, -396], [-397, -398, -399], [-400, -401, -402], [-403, -404, -405], [-406, -407, -408], [-409, -410, -411], [-412, -413, -414], [-415, -416, -417], [-418, -419, -420], [-421, -422, -423], [-424, -425, -426], [-427, -428, -429], [-430, -431, -432], [-433, -434, -435], [-436, -437, -438], [-439, -440, -441], [-442, -443, -444], [-445, -446, -447], [-448, -449, -450], [-451, -452, -453], [-454, -455, -456], [-457, -458, -459], [-460, -461, -462], [-463, -464, -465], [-466, -467, -468], [-469, -470, -471], [-472, -473, -474], [-475, -476, -477], [-478, -479, -480], [-481, -482, -483], [-484, -485, -486], [-487, -488, -489], [-490, -491, -492], [-493, -494, -495], [-496, -497, -498], [-499, -500, -501], [-502, -503, -504], [-505, -506, -507], [-508, -509, -510], [-511, -512, -513], [-514, -515, -516], [-517, -518, -519], [-520, -521, -522], [-523, -524, -525], [-526, -527, -528], [-529, -530, -531], [-532, -533, -534], [-535, -536, -537], [-538, -539, -540], [-541, -542, -543], [-544, -545, -546], [-547, -548, -549], [-550, -551, -552], [-553, -554, -555], [-556, -557, -558], [-559, -560, -561], [-562, -563, -564], [-565, -566, -567], [-568, -569, -570], [-571, -572, -573], [-574, -575, -576], [-577, -578, -579], [-580, -581, -582], [-583, -584, -585], [-586, -587, -588], [-589, -590, -591], [-592, -593, -594], [-595, -596, -597], [-598, -599, -600], [-601, -602, -603], [-604, -605, -606], [-607, -608, -609], [-610, -611, -612], [-613, -614, -615], [-616, -617, -618], [-619, -620, -621], [-622, -623, -624], [-625, -626, -627], [-628, -629, -630], [-631, -632, -633], [-63
````

### 36. P16 · run 1 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 5: 28 (debe ser entero no nulo con |lit| <= 27)

````text
{"num_vars": 27, "clauses": [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20], [21, 22, 23, 24, 25], [26, 27, 28, 29, 30], [31, 32, 33, 34, 35], [36, 37, 38, 39, 40], [41, 42, 43, 44, 45], [46, 47, 48, 49, 50], [51, 52, 53, 54, 55], [56, 57, 58, 59, 60], [61, 62, 63, 64, 65], [66, 67, 68, 69, 70], [71, 72, 73, 74, 75], [76, 77, 78, 79, 80], [81, 82, 83, 84, 85], [86, 87, 88, 89, 90], [91, 92, 93, 94, 95], [96, 97, 98, 99, 100], [101, 102, 103, 104, 105], [106, 107, 108, 109, 110], [111, 112, 113, 114, 115], [116, 117, 118, 119, 120], [121, 122, 123, 124, 125], [126, 127, 128, 129, 130], [131, 132, 133, 134, 135], [136, 137, 138, 139, 140], [141, 142, 143, 144, 145], [146, 147, 148, 149, 150], [151, 152, 153, 154, 155], [156, 157, 158, 159, 160], [161, 162, 163, 164, 165], [166, 167, 168, 169, 170], [171, 172, 173, 174, 175], [176, 177, 178, 179, 180], [181, 182, 183, 184, 185], [186, 187, 188, 189, 190], [191, 192, 193, 194, 195], [196, 197, 198, 199, 200], [201, 202, 203, 204, 205], [206, 207, 208, 209, 210], [211, 212, 213, 214, 215], [216, 217, 218, 219, 220], [221, 222, 223, 224, 225], [226, 227, 228, 229, 230], [231, 232, 233, 234, 235], [236, 237, 238, 239, 240], [241, 242, 243, 244, 245], [246, 247, 248, 249, 250], [251, 252, 253, 254, 255], [256, 257, 258, 259, 260], [261, 262, 263, 264, 265], [266, 267, 268, 269, 270], [271, 272, 273, 274, 275], [276, 277, 278, 279, 280], [281, 282, 283, 284, 285], [286, 287, 288, 289, 290], [291, 292, 293, 294, 295], [296, 297, 298, 299, 300], [301, 302, 303, 304, 305], [306, 307, 308, 309, 310], [311, 312, 313, 314, 315], [316, 317, 318, 319, 320], [321, 322, 323, 324, 325], [326, 327, 328, 329, 330], [331, 332, 333, 334, 335], [336, 337, 338, 339, 340], [341, 342, 343, 344, 345], [346, 347, 348, 349, 350], [351, 352, 353, 354, 355], [356, 357, 358, 359, 360], [361, 362, 363, 364, 365], [366, 367, 368, 369, 370], [371, 372, 373, 374, 375], [376, 377, 378, 379, 380], [381, 382, 383, 384, 385], [386, 387, 388, 389, 390], [391, 392, 393, 394, 395], [396, 397, 398, 399, 400], [401, 402, 403, 404, 405], [406, 407, 408, 409, 410], [401, 402, 403, 404, 405], [416, 417, 418, 419, 420], [421, 422, 423, 424, 425], [426, 427, 428, 429, 430], [431, 432, 433, 434, 435], [436, 437, 438, 439, 440], [441, 442, 443, 444, 445], [446, 447, 448, 449, 450], [446, 447, 448, 449, 450]]}
````

### 37. P17 · run 1 · hard

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 0 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 0 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 0 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 0 colores asignados en el modelo (debe tener exactamente 1); el vértice E tiene 0 colores asignados en el modelo (debe tener exactamente 1); el vértice F tiene 0 colores asignados en el modelo (debe tener exactamente 1); el vértice G tiene 0 colores asignados en el modelo (debe tener exactamente 1); el vértice H tiene 0 colores asignados en el modelo (debe tener exactamente 1); el vértice I tiene 0 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']; restricción de arista omitida por completo: ['A-B', 'A-C', 'A-E', 'A-F', 'A-G', 'A-H', 'A-I', 'B-C', 'B-F', 'B-H', 'C-D', 'C-E', 'C-G', 'C-I', 'D-E', 'D-F', 'D-G', 'D-H', 'D-I', 'E-F', 'E-H', 'F-G', 'F-I', 'G-H', 'H-I']; 10 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 27, "clauses": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, -1, -2], [-1, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, 2, 4], [-1, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, 2, 5], [-1, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, 2, 6], [-1, -2, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, 3, 4], [-1, -2, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, 3, 5], [-1, -2, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, 3, 6], [-1, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, 4, 5], [-1, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, 4, 6], [-1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, 5, 6]]}
````

### 38. P18 · run 1 · hard

- **Categoría:** Malformed syntax (won't parse)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** PARSE_ERROR
- **Diagnóstico (usa el CNF de referencia):** JSON inválido: Expecting ',' delimiter (posición 3619) [salida truncada por num_predict]

````text
{"num_vars": 30, "clauses": [[1, 2, 3, -4, -5, -6], [4, 5, -7, -8, -9, -10], [11, 12, 13, -14, -15, -16], [17, 18, 19, -20, -21, -22], [23, 24, 25, -26, -27, -28], [29, 30, -31, -32, -33, -34], [-35, -36, -37, 38, 39, 40], [-41, -42, -43, 44, 45, 46], [-47, -48, -49, 50, 51, 52], [-53, -54, -55, 56, 57, 58], [-59, -60, -61, 62, 63, 64], [-65, -66, -67, 68, 69, 70], [-71, -72, -73, 74, 75, 76], [-77, -78, -79, 80, 81, 82], [-83, -84, -85, 86, 87, 88], [-89, -90, -91, 92, 93, 94], [-95, -96, -97, 98, 99, 100], [-101, -102, -103, 104, 105, 106], [-107, -108, -109, 110, 111, 112], [-113, -114, -115, 116, 117, 118], [-119, -120, -121, 122, 123, 124], [-125, -126, -127, 128, 129, 130], [-131, -132, -133, 134, 135, 136], [-137, -138, -139, 140, 141, 142], [-143, -144, -145, 146, 147, 148], [-149, -150, -151, 152, 153, 154], [-155, -156, -157, 158, 159, 160], [-161, -162, -163, 164, 165, 166], [-167, -168, -169, 170, 171, 172], [-173, -174, -175, 176, 177, 178], [-179, -180, -181, 182, 183, 184], [-185, -186, -187, 188, 189, 190], [-189, -190, -191, 192, 193, 194], [-195, -196, -197, 198, 199, 200], [-201, -202, -203, 204, 205, 206], [-207, -208, -209, 210, 211, 212], [-213, -214, -215, 216, 217, 218], [-219, -220, -221, 222, 223, 224], [-225, -226, -227, 228, 229, 230], [-229, -230, -231, 232, 233, 234], [-235, -236, -237, 238, 239, 240], [-239, -240, -241, 242, 243, 244], [-245, -246, -247, 248, 249, 250], [-249, -250, -251, 252, 253, 254], [-251, -252, -253, 254, 255, 256], [-255, -256, -257, 258, 259, 260], [-259, -260, -261, 262, 263, 264], [-261, -262, -263, 264, 265, 266], [-265, -266, -267, 268, 269, 270], [-269, -270, -271, 272, 273, 274], [-271, -272, -273, 274, 275, 276], [-275, -276, -277, 278, 279, 280], [-277, -278, -279, 280, 281, 282], [-281, -282, -283, 284, 285, 286], [-283, -284, -285, 286, 287, 288], [-287, -288, -289, 290, 291, 292], [-289, -290, -291, 292, 293, 294], [-293, -294, -295, 296, 297, 298], [-295, -296, -297, 298, 299, 300], [-299, -300, -301, 302, 303, 304], [-301, -302, -303, 304, 305, 306], [-303, -304, -305, 306, 307, 308], [-305, -306, -307, 308, 309, 310], [-307, -308, -309, 309, 310, 311], [-309, -310, -311, 311, 312, 313], [-311, -312, -313, 313, 314, 315], [-313, -314, -315, 314, 315, 316], [-315, -316, -317, 317, 318, 319], [-317, -318, -319, 319, 320, 321], [-319, -320, -321, 321, 322, 323], [-321, -322, -323, 323, 324, 325], [-323, -324, -325, 325, 326, 327], [-325, -326, -327, 327, 328, 329], [-327, -328, -329, 328, 329, 330], [-329, -330, -331, 331, 332, 333], [-331, -332, -333, 333, 334, 335], [-333, -334, -335, 335, 336, 337], [-335, -336, -337, 337, 338, 339], [-337, -338, -339, 339, 340, 341], [-339, -340, -341, 341, 342, 343], [-341, -342, -343, 343, 344, 345], [-343, -344, -345, 345, 346, 347], [-345, -346, -347, 347, 348, 349], [-347, -348, -349, 348, 349, 350], [-349, -350, -351, 350, 351, 352], [-351, -352, -353, 352, 353, 354], [-353, -354, -355, 354, 355, 356], [-355, -356, -357, 356, 357, 358], [-357, -358, -359, 358, 359, 360], [-359, -360, -361, 360, 361, 362], [-361, -362, -363, 362, 363, 364], [-363, -364, -365, 364, 365, 366], [-365, -366, -367, 366, 367, 368], [-367, -368, -369, 368, 369, 370], [-369, -370, -371, 370, 371, 372], [-371, -372, -373, 372, 373, 374], [-373, -374, -375, 374, 375, 376], [-375, -376, -377, 376, 377, 378], [-377, -378, -379, 378, 379, 380], [-379, -380, -381, 380, 381, 382], [-381, -382, -383, 382, 383, 384], [-383, -384, -385, 384, 385, 386], [-385, -386, -387, 386, 387, 388], [-387, -388, -389, 388, 389, 390], [-389, -390, -391, 390, 391, 392], [-391, -392, -393, 392, 3
````

### 39. P19 · run 1 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 5: -31 (debe ser entero no nulo con |lit| <= 30)

````text
{"num_vars": 30, "clauses": [[1, 2, 3, -4, -5, -6], [4, 5, -7, -8, -9, -10], [11, 12, 13, -14, -15, -16], [17, 18, -19, -20, -21, -22], [23, 24, 25, -26, -27, -28], [29, 30, -31, -32, -33, -34], [-35, -36, -37, 38, 39, 40], [-41, -42, -43, 44, 45, 46], [-47, -48, -49, 50, 51, 52], [53, 54, -55, -56, -57, -58], [59, 60, -61, -62, -63, -64], [65, 66, 67, -68, -69, -70], [71, 72, -73, -74, -75, -76], [77, 78, 79, -80, -81, -82], [83, 84, -85, -86, -87, -88], [89, 90, -91, -92, -93, -94], [95, 96, 97, -98, -99, -100], [101, 102, -103, -104, -105, -106], [-107, -108, -109, 110, 111, 112], [-113, -114, -115, 116, 117, 118], [-119, -120, -121, 122, 123, 124], [125, 126, -127, -128, -129, -130]]}
````

### 40. P20 · run 1 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 5: -31 (debe ser entero no nulo con |lit| <= 30)

````text
{"num_vars": 30, "clauses": [[1, 2, 3, -4, -5, -6], [4, 5, 6, -7, -8, -9], [10, 11, 12, -13, -14, -15], [16, 17, 18, -19, -20, -21], [22, 23, 24, -25, -26, -27], [28, 29, 30, -31, -32, -33]]}
````

### 41. P01 · run 2 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 3 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D']; restricción de arista omitida por completo: ['A-B', 'A-D', 'B-C', 'C-D']; 21 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 12, "clauses": [[1, 2, 5, 6], [3, 4, 7, 8], [9, 10, 11, 12], [1, -2, -5, -6], [2, -1, -5, -6], [3, -4, -7, -8], [4, -3, -7, -8], [9, -10, -11, -12], [10, -9, -11, -12], [11, -9, -10, -12], [12, -9, -10, -11], [1, 2, -5, -6], [1, 3, -7, -8], [2, 3, -5, -6], [4, 5, -11, -12], [5, 6, -10, -12], [6, 4, -10, -12], [7, 8, -9, -12], [8, 7, -9, -12], [9, 10, -7, -8], [10, 9, -7, -8], [11, 12, -5, -6], [12, 11, -5, -6], [1, 2, 3, -5, -6, -7, -8]]}
````

### 42. P02 · run 2 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 2 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E']; restricción de arista omitida por completo: ['A-B', 'B-C', 'C-D', 'D-E']; 9 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 15, "clauses": [[1, 2, 3, 4, 5], [-1, -2, -6, -7, -8], [-3, -4, -9, -10, -11], [-5, -6, -12, -13, -14], [-7, -8, -15], [9, 10, 11, 12, 13], [-9, -10, -14], [-11, -12, -15], [14, 15], [-14, -15]]}
````

### 43. P03 · run 2 · easy

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 2: 13 (debe ser entero no nulo con |lit| <= 12)

````text
{"num_vars": 12, "clauses": [[1, 2, 5, 6], [-3, -4, -7, -8], [9, 10, 13, 14], [-9, -10, -11, -12], [-1, -5, -9, -13], [2, -6, -10, -14], [5, -1, -9, -11], [-2, -6, -10, -12], [-1, -4, -8, -11], [2, -5, -8, -12], [3, -7, -13, -14], [-3, -7, -13, -11], [-3, -7, -13, -12]]}
````

### 44. P04 · run 2 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice E tiene 0 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E']; restricción de arista omitida por completo: ['A-B', 'B-C']; 24 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 15, "clauses": [[1, 2, 5], [3, 6, 9], [4, 7, 10], [8, 11, 14], [-15, -12, -13], [-1, -2, -15], [-3, -6, -12], [-4, -7, -11], [-8, -11, -14], [-9, -12, -13], [10, 13, 15], [11, 14, 15], [12, 13, 14], [-1, -15, -14], [-2, -12, -14], [-3, -12, -15], [-4, -11, -15], [-5, -9, -15], [-5, -8, -14], [-6, -9, -13], [-6, -8, -12], [-7, -10, -13], [-7, -9, -12], [-8, -10, -11]]}
````

### 45. P05 · run 2 · easy

- **Categoría:** Valid syntax, over-constrained (UNSAT)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** UNSAT
- **Diagnóstico (usa el CNF de referencia):** falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E']; restricción de arista omitida por completo: ['A-B', 'A-E', 'B-C']; 18 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 15, "clauses": [[1, 2, 5], [3, 6, 9], [4, 7, 10], [8, 11, 14], [12, 15, -1], [1, -2], [2, -1], [-1, -3], [3, -4], [4, -1], [-5, -6], [5, -7], [6, -5], [7, -6], [-8, -9], [8, -10], [9, -8], [10, -9], [-11, -12], [11, -13], [12, -11], [-14, -15], [14, -15]]}
````

### 46. P06 · run 2 · easy

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 2 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E', 'F']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F']; restricción de arista omitida por completo: ['A-B', 'B-C', 'D-E', 'E-F']; 15 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 18, "clauses": [[1, 2, 5], [3, 6, 9], [10, 13, 16], [-17, -18], [4, 7, 11], [8, 12, 15], [17, -18], [1, 2, 5, -10, -13, -16], [3, 6, 9, -11, -14, -17], [4, 7, 11, -12, -15, -18], [10, 13, 16, -1, -2, -5], [17, -18, -1, -2, -5], [8, 12, 15, -3, -6, -9], [11, -14, -17, -4, -7, -10], [14, -17, -4, -7, -10], [12, -15, -18, -4, -7, -10], [17, -18, -1, -2, -5]]}
````

### 47. P07 · run 2 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 3: -19 (debe ser entero no nulo con |lit| <= 18)

````text
{"num_vars": 18, "clauses": [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12], [13, 14, 15, 16, 17, 18], [-19, -20, -21, -22, -23, -24], [-25, -26, -27, -28, -29, -30], [-31, -32, -33, -34, -35, -36], [-37, -38, -39, -40, -41, -42], [-43, -44, -45, -46, -47, -48], [-49, -50, -51, -52, -53, -54], [-55, -56, -57, -58, -59, -60], [-61, -62, -63, -64, -65, -66], [-67, -68, -69, -70, -71, -72], [-73, -74, -75, -76, -77, -78], [-79, -80, -81, -82, -83, -84], [-85, -86, -87, -88, -89, -90], [-91, -92, -93, -94, -95, -96], [-97, -98, -99, -100, -101, -102], [-103, -104, -105, -106, -107, -108]]}
````

### 48. P08 · run 2 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 3: -19 (debe ser entero no nulo con |lit| <= 18)

````text
{"num_vars": 18, "clauses": [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12], [13, 14, 15, 16, 17, 18], [-19, -20, -21, -22, -23, -24], [-25, -26, -27, -28, -29, -30], [-31, -32, -33, -34, -35, -36], [-37, -38, -39, -40, -41, -42], [-43, -44, -45, -46, -47, -48], [-49, -50, -51, -52, -53, -54], [-55, -56, -57, -58, -59, -60], [-61, -62, -63, -64, -65, -66], [-67, -68, -69, -70, -71, -72], [-73, -74, -75, -76, -77, -78], [-79, -80, -81, -82, -83, -84], [-85, -86, -87, -88, -89, -90], [-91, -92, -93, -94, -95, -96], [-97, -98, -99, -100, -101, -102], [-103, -104, -105, -106, -107, -108]]}
````

### 49. P09 · run 2 · medium

- **Categoría:** Malformed syntax (won't parse)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** PARSE_ERROR
- **Diagnóstico (usa el CNF de referencia):** JSON inválido: Expecting ',' delimiter (posición 3921) [salida truncada por num_predict]

````text
{"num_vars": 21, "clauses": [[1, 2, 3, 4], [5, 6, 7, 8], [-1, -2, -5, -6], [-3, -4, -7, -8], [9, 10, 11], [-9, -10, -11, -12], [-13, -14, -15], [16, 17, 18], [-16, -17, -18, -19], [-20, -21, -22], [23, 24, 25], [-23, -24, -25, -26], [-27, -28, -29], [30, 31, 32], [-30, -31, -32, -33], [-34, -35, -36], [37, 38, 39], [-37, -38, -39, -40], [-41, -42, -43], [44, 45, 46], [-44, -45, -46, -47], [-48, -49, -50], [51, 52, 53], [-51, -52, -53, -54], [-55, -56, -57], [58, 59, 60], [-58, -59, -60, -61], [-62, -63, -64], [65, 66, 67], [-65, -66, -67, -68], [-69, -70, -71], [72, 73, 74], [-72, -73, -74, -75], [-76, -77, -78], [79, 80, 81], [-79, -80, -81, -82], [-83, -84, -85], [86, 87, 88], [-86, -87, -88, -89], [-90, -91, -92], [93, 94, 95], [-93, -94, -95, -96], [-97, -98, -99], [100, 101, 102], [-100, -101, -102, -103], [-104, -105, -106], [107, 108, 109], [-107, -108, -109, -110], [-111, -112, -113], [114, 115, 116], [-114, -115, -116, -117], [-118, -119, -120], [121, 122, 123], [-121, -122, -123, -124], [-125, -126, -127], [128, 129, 130], [-128, -129, -130, -131], [-132, -133, -134], [135, 136, 137], [-135, -136, -137, -138], [-139, -140, -141], [142, 143, 144], [-142, -143, -144, -145], [-146, -147, -148], [149, 150, 151], [-149, -150, -151, -152], [-153, -154, -155], [156, 157, 158], [-156, -157, -158, -159], [-160, -161, -162], [163, 164, 165], [-163, -164, -165, -166], [-167, -168, -169], [170, 171, 172], [-170, -171, -172, -173], [-174, -175, -176], [177, 178, 179], [-177, -178, -179, -180], [-181, -182, -183], [184, 185, 186], [-184, -185, -186, -187], [-188, -189, -190], [191, 192, 193], [-191, -192, -193, -194], [-195, -196, -197], [198, 199, 200], [-198, -199, -200, -201], [-202, -203, -204], [205, 206, 207], [-205, -206, -207, -208], [-209, -210, -211], [212, 213, 214], [-212, -213, -214, -215], [-216, -217, -218], [219, 220, 221], [-219, -220, -221, -222], [-223, -224, -225], [226, 227, 228], [-226, -227, -228, -229], [-230, -231, -232], [233, 234, 235], [-233, -234, -235, -236], [-237, -238, -239], [240, 241, 242], [-240, -241, -242, -243], [-244, -245, -246], [247, 248, 249], [-247, -248, -249, -250], [-251, -252, -253], [254, 255, 256], [-254, -255, -256, -257], [-258, -259, -260], [261, 262, 263], [-261, -262, -263, -264], [-265, -266, -267], [268, 269, 270], [-268, -269, -270, -271], [-272, -273, -274], [275, 276, 277], [-275, -276, -277, -278], [-279, -280, -281], [282, 283, 284], [-282, -283, -284, -285], [-286, -287, -288], [289, 290, 291], [-289, -290, -291, -292], [-293, -294, -295], [296, 297, 298], [-296, -297, -298, -299], [-300, -301, -302], [303, 304, 305], [-303, -304, -305, -306], [-307, -308, -309], [310, 311, 312], [-310, -311, -312, -313], [-314, -315, -316], [317, 318, 319], [-317, -318, -319, -320], [-321, -322, -323], [324, 325, 326], [-324, -325, -326, -327], [-328, -329, -330], [331, 332, 333], [-331, -332, -333, -334], [-335, -336, -337], [338, 339, 340], [-338, -339, -340, -341], [-342, -343, -344], [345, 346, 347], [-345, -346, -347, -348], [-349, -350, -351], [352, 353, 354], [-352, -353, -354, -355], [-356, -357, -358], [359, 360, 361], [-359, -360, -361, -362], [-363, -364, -365], [366, 367, 368], [-366, -367, -368, -369], [-370, -371, -372], [373, 374, 375], [-373, -374, -375, -376], [-377, -378, -379], [380, 381, 382], [-380, -381, -382, -383], [-384, -385, -386], [387, 388, 389], [-387, -388, -389, -390], [-391, -392, -393], [394, 395, 396], [-394, -395, -396, -397], [-398, -399, -400], [401, 402, 403], [-401, -402, -403, -404], [-405, -406, -407], [408, 409, 410], [-408, -409, -410, -411], [-412, -413, -414], [415, 416, 417], [-415, -416, -417, -418], [-419, -420, -421], [422, 423, 424], [-422, -423, -424, -425], [-426, -427, -428], [429, 430, 431], [-429, -430, -431, -432], [-433, -434, -435], [436, 437, 438], [-436, -437, -438, -439], [-440, -441, -442], [443, 444, 445], [-443, -444, -445, -446], [-447, -448
````

### 50. P10 · run 2 · medium

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 0 colores asignados en el modelo (debe tener exactamente 1); el vértice F tiene 0 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E', 'F', 'G']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G']; restricción de arista omitida por completo: ['A-B', 'A-C', 'A-F', 'B-C', 'B-E', 'C-E', 'D-E', 'D-F', 'E-F', 'F-G']; 12 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 21, "clauses": [[1, 2, 3, 4], [5, 6, 7, 8], [-1, -2, -5, -6], [-1, -5, -2, -6], [-2, -3, -4, -7], [-2, -3, -4, -8], [9, 10, 11, 12], [13, 14, 15, 16], [-5, -10, -13, -18], [-5, -13, -10, -18], [-6, -11, -14, -19], [-6, -14, -11, -19], [-7, -12, -15, -20], [-7, -15, -12, -20], [-8, -16, -17, -21], [-8, -17, -16, -21], [18, 19, 20, 21], [18, 20, 19, 21], [19, 20, 18, 21], [18, 19, 20, 21]]}
````

### 51. P11 · run 2 · medium

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice E tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice F tiene 3 colores asignados en el modelo (debe tener exactamente 1) | falta 'al menos un color' en ['A', 'B', 'C', 'D', 'E', 'F', 'G']; falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G']; restricción de arista omitida por completo: ['A-B', 'B-C', 'B-G', 'C-D', 'D-E', 'D-G', 'E-F', 'E-G']; 11 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 21, "clauses": [[1, 2, 3, 4], [5, 6, 7, 8], [-1, -2, -5, -6], [-3, -4, -7, -8], [9, 10, 11], [-9, -10, -11], [-12, -13, -14, -15], [12, 13, 14, 15], [-16, -17, -18, -19], [16, 17, 18, 19], [-20, -21], [20, 21]]}
````

### 52. P12 · run 2 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 8: 25 (debe ser entero no nulo con |lit| <= 24)

````text
{"num_vars": 24, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [-10, -11, -12], [-13, -14, -15], [16, 17, 18], [-19, -20, -21], [-22, -23, -24], [25, 26, 27], [28, 29, 30], [-31, -32, -33], [-34, -35, -36], [37, 38, 39], [-40, -41, -42], [-43, -44, -45], [46, 47, 48], [49, 50, 51], [-52, -53, -54], [-55, -56, -57], [58, 59, 60], [61, 62, 63], [-64, -65, -66], [-67, -68, -69]]}
````

### 53. P13 · run 2 · medium

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 8: 25 (debe ser entero no nulo con |lit| <= 24)

````text
{"num_vars": 24, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [-10, -11, -12], [-13, -14, -15], [16, 17, 18], [-19, -20, -21], [-22, -23, -24], [25, 26, 27], [28, 29, 30], [-31, -32, -33], [-34, -35, -36], [37, 38, 39], [-40, -41, -42], [-43, -44, -45], [46, 47, 48], [49, 50, 51], [-52, -53, -54], [-55, -56, -57], [58, 59, 60], [61, 62, 63], [-64, -65, -66], [-67, -68, -69]]}
````

### 54. P14 · run 2 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 24: 25 (debe ser entero no nulo con |lit| <= 24)

````text
{"num_vars": 24, "clauses": [[1, 2, 3, 4], [5, 6, 7, 8], [-1, -2, -5, -6], [-1, -5, -2, -7], [-2, -4, -5, -6], [-2, -4, -7, -8], [-3, -4, -5, -6], [-3, -4, -7, -8], [9, 10, 11, 12], [-9, -10, -13, -14], [-9, -13, -10, -15], [-9, -13, -15, -16], [-10, -12, -13, -14], [-10, -12, -15, -16], [-11, -12, -13, -14], [-11, -12, -15, -16], [17, 18, 19, 20], [-17, -18, -21, -22], [-17, -21, -18, -23], [-17, -21, -23, -24], [-18, -16, -21, -22], [-18, -16, -23, -24], [-19, -16, -21, -22], [-19, -16, -23, -24], [25, 26, 27, 28], [-25, -26, -29, -30], [-25, -29, -26, -31], [-25, -29, -31, -32], [-26, -30, -29, -31], [-26, -30, -31, -32], [-27, -30, -29, -31], [-27, -30, -31, -32], [33, 34, 35, 36], [-33, -34, -37, -38], [-33, -37, -34, -39], [-33, -37, -39, -40], [-34, -36, -37, -38], [-34, -36, -39, -40], [-35, -36, -37, -38], [-35, -36, -39, -40], [41, 42, 43, 44], [-41, -42, -45, -46], [-41, -45, -42, -47], [-41, -45, -47, -48], [-42, -44, -45, -46], [-42, -44, -47, -48], [-43, -44, -45, -46], [-43, -44, -47, -48]]}
````

### 55. P15 · run 2 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 8: 25 (debe ser entero no nulo con |lit| <= 24)

````text
{"num_vars": 24, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [-10, -11, -12], [-13, -14, -15], [16, 17, 18], [-19, -20, -21], [-22, -23, -24], [25, 26, 27], [28, 29, 30], [-31, -32, -33], [-34, -35, -36], [37, 38, 39], [-40, -41, -42], [-43, -44, -45], [46, 47, 48], [49, 50, 51], [-52, -53, -54], [-55, -56, -57], [58, 59, 60], [61, 62, 63], [-64, -65, -66], [-67, -68, -69]]}
````

### 56. P16 · run 2 · hard

- **Categoría:** Malformed syntax (won't parse)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** PARSE_ERROR
- **Diagnóstico (usa el CNF de referencia):** JSON inválido: Expecting ',' delimiter (posición 3562) [salida truncada por num_predict]

````text
{"num_vars": 27, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [-1, -2, -3], [-4, -5, -6], [-7, -8, -9], [10, 11, 12], [-10, -11, -12], [13, 14, 15], [-13, -14, -15], [16, 17, 18], [-16, -17, -18], [19, 20, 21], [-19, -20, -21], [22, 23, 24], [-22, -23, -24], [25, 26, 27], [-25, -26, -27], [3, 6, 9], [3, 12, 15], [3, 18, 21], [3, 24, 27], [6, 9, 12], [6, 15, 18], [6, 21, 24], [6, 27, 30], [9, 12, 15], [9, 18, 21], [9, 24, 27], [12, 15, 18], [12, 21, 24], [12, 27, 30], [15, 18, 21], [15, 24, 27], [18, 21, 24], [18, 27, 30], [21, 24, 27], [21, 30, 33], [24, 27, 30], [24, 33, 36], [27, 30, 33], [27, 36, 39], [30, 33, 36], [30, 39, 42], [33, 36, 39], [33, 42, 45], [36, 39, 42], [36, 45, 48], [39, 42, 45], [39, 48, 51], [42, 45, 48], [42, 51, 54], [45, 48, 51], [45, 54, 57], [48, 51, 54], [48, 57, 60], [51, 54, 57], [51, 60, 63], [54, 57, 60], [54, 63, 66], [57, 60, 63], [57, 66, 69], [60, 63, 66], [60, 69, 72], [63, 66, 69], [63, 72, 75], [66, 69, 72], [66, 75, 78], [69, 72, 75], [69, 78, 81], [72, 75, 78], [72, 81, 84], [75, 78, 81], [75, 84, 87], [78, 81, 84], [78, 87, 90], [81, 84, 87], [81, 90, 93], [84, 87, 90], [84, 93, 96], [87, 90, 93], [87, 96, 99], [90, 93, 96], [90, 99, 102], [93, 96, 99], [93, 102, 105], [96, 99, 102], [96, 105, 108], [99, 102, 105], [99, 108, 111], [102, 105, 108], [102, 111, 114], [105, 108, 111], [105, 114, 117], [108, 111, 114], [108, 117, 120], [111, 114, 117], [111, 120, 123], [114, 117, 120], [114, 123, 126], [117, 120, 123], [117, 126, 129], [120, 123, 126], [120, 129, 132], [123, 126, 129], [123, 132, 135], [126, 129, 132], [126, 135, 138], [129, 132, 135], [129, 138, 141], [132, 135, 138], [132, 141, 144], [135, 138, 141], [135, 144, 147], [138, 141, 144], [138, 147, 150], [141, 144, 147], [141, 150, 153], [144, 147, 150], [144, 153, 156], [147, 150, 153], [147, 156, 159], [150, 153, 156], [150, 159, 162], [153, 156, 159], [153, 162, 165], [156, 159, 162], [156, 165, 168], [159, 162, 165], [159, 168, 171], [162, 165, 168], [162, 171, 174], [165, 168, 171], [165, 174, 177], [168, 171, 174], [168, 177, 180], [171, 174, 177], [171, 180, 183], [174, 177, 180], [174, 183, 186], [177, 180, 183], [177, 186, 189], [180, 183, 186], [180, 189, 192], [183, 186, 189], [183, 192, 195], [186, 189, 192], [186, 195, 198], [189, 192, 195], [189, 198, 201], [192, 195, 198], [192, 201, 204], [195, 198, 201], [195, 204, 207], [198, 201, 204], [198, 207, 210], [201, 204, 207], [201, 210, 213], [204, 207, 210], [204, 213, 216], [207, 210, 213], [207, 216, 219], [210, 213, 216], [210, 219, 222], [213, 216, 219], [213, 222, 225], [216, 219, 222], [216, 225, 228], [219, 222, 225], [219, 228, 231], [222, 225, 228], [222, 231, 234], [225, 228, 231], [225, 234, 237], [228, 231, 234], [228, 237, 240], [231, 234, 237], [231, 240, 243], [234, 237, 240], [234, 243, 246], [237, 240, 243], [237, 246, 249], [240, 243, 246], [240, 249, 252], [243, 246, 249], [243, 252, 255], [246, 249, 252], [246, 255, 258], [249, 252, 255], [249, 258, 261], [252, 255, 258], [252, 261, 264], [255, 258, 261], [255, 264, 267], [258, 261, 264], [258, 267, 270], [261, 264, 267], [261, 270, 273], [264, 267, 270], [264, 273, 276], [267, 270, 273], [267, 276, 279], [270, 273, 276], [270, 279, 282], [273, 276, 279], [273, 282, 285], [276, 279, 282], [276, 285, 288], [279, 282, 285], [279, 288, 291], [282, 285, 288], [282, 291, 294], [285, 288, 291], [285, 294, 297], [288, 291, 294], [288, 297, 300], [291, 294, 297], [291, 300, 303], [294, 297, 300], [294, 303, 306], [297, 300, 303], [297, 306, 309], [300, 303, 306], [300, 3
````

### 57. P17 · run 2 · hard

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice B tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice E tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice F tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice G tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice H tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice I tiene 2 colores asignados en el modelo (debe tener exactamente 1) | falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']; restricción de arista omitida por completo: ['A-B', 'A-C', 'A-E', 'A-F', 'A-G', 'A-H', 'A-I', 'B-C', 'B-F', 'B-H', 'C-D', 'C-E', 'C-G', 'C-I', 'D-E', 'D-F', 'D-G', 'D-H', 'D-I', 'E-F', 'E-H', 'F-G', 'F-I', 'G-H', 'H-I']; 36 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 27, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [-1, -2, -3], [-4, -5, -6], [-7, -8, -9], [10, 11, 12], [-10, -11, -12], [13, 14, 15], [-13, -14, -15], [16, 17, 18], [-16, -17, -18], [19, 20, 21], [-19, -20, -21], [22, 23, 24], [-22, -23, -24], [25, 26, 27], [-25, -26, -27], [3, 6, 9], [3, 10, 12], [3, 13, 15], [3, 16, 18], [3, 19, 21], [3, 22, 24], [3, 25, 27], [6, 10, 14], [6, 13, 17], [6, 16, 20], [6, 19, 24], [6, 22, 26], [9, 12, 15], [9, 14, 18], [9, 16, 21], [9, 19, 24], [9, 22, 27], [12, 15, 18], [12, 17, 20], [12, 19, 24], [12, 22, 26], [15, 18, 21], [15, 20, 24], [15, 22, 27], [18, 21, 24], [18, 24, 27], [21, 24, 27]]}
````

### 58. P18 · run 2 · hard

- **Categoría:** Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)
- **¿Detectable sin ground truth?** Yes (decoder)
- **Estado del solver/validador:** DECODE_ERROR
- **Diagnóstico (usa el CNF de referencia):** el vértice A tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice C tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice D tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice E tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice G tiene 3 colores asignados en el modelo (debe tener exactamente 1); el vértice H tiene 2 colores asignados en el modelo (debe tener exactamente 1); el vértice J tiene 2 colores asignados en el modelo (debe tener exactamente 1) | falta 'a lo sumo un color' (parcial o total) en ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']; restricción de arista omitida por completo: ['A-B', 'A-F', 'A-H', 'B-C', 'B-D', 'B-F', 'B-G', 'B-J', 'C-D', 'C-H', 'C-J', 'D-F', 'D-H', 'D-I', 'E-F', 'E-H', 'F-G', 'F-H', 'F-I', 'F-J', 'G-H', 'H-J', 'I-J']; 39 cláusulas extra de otro tipo (variables/índices incorrectos u otras)

````text
{"num_vars": 30, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24], [25, 26, 27], [28, 29, 30], [-1, -4, -7], [-2, -5, -8], [-3, -6, -9], [-10, -13, -16], [-11, -14, -17], [-12, -15, -18], [-19, -22, -25], [-20, -23, -26], [-21, -24, -27], [-28, -30, -29], [3, 6, 9], [3, 7, 10], [3, 8, 11], [3, 9, 12], [4, 7, 10], [4, 8, 11], [4, 9, 12], [5, 7, 10], [5, 8, 11], [5, 9, 12], [6, 8, 11], [6, 9, 12], [7, 9, 12], [15, 18, 21], [15, 19, 22], [15, 20, 23], [15, 21, 24], [16, 19, 22], [16, 20, 23], [16, 21, 24], [17, 20, 23], [17, 21, 24], [18, 20, 23], [18, 21, 24], [19, 21, 24], [23, 26, 29], [23, 27, 30], [24, 27, 30], [25, 28, 30]]}
````

### 59. P19 · run 2 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 10: -31 (debe ser entero no nulo con |lit| <= 30)

````text
{"num_vars": 30, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24], [25, 26, 27], [28, 29, 30], [-31, -32, -33], [-34, -35, -36], [-37, -38, -39], [-40, -41, -42], [-43, -44, -45], [-46, -47, -48], [-49, -50, -51], [-52, -53, -54], [-55, -56, -57], [-58, -59, -60], [-61, -62, -63], [-64, -65, -66], [-67, -68, -69], [-70, -71, -72], [-73, -74, -75], [-76, -77, -78], [-79, -80, -81], [-82, -83, -84], [-85, -86, -87], [-88, -89, -90], [-91, -92, -93], [-94, -95, -96], [-97, -98, -99], [-100, -101, -102], [-103, -104, -105], [-106, -107, -108], [-109, -110, -111], [-112, -113, -114], [-115, -116, -117], [-118, -119, -120], [-121, -122, -123], [-124, -125, -126], [-127, -128, -129], [-130, -131, -132], [-133, -134, -135], [-136, -137, -138], [-139, -140, -141], [-142, -143, -144], [-145, -146, -147], [-148, -149, -150], [-151, -152, -153], [-154, -155, -156], [-157, -158, -159], [-160, -161, -162], [-163, -164, -165], [-166, -167, -168], [-169, -170, -171], [-172, -173, -174], [-175, -176, -177], [-178, -179, -180], [-181, -182, -183], [-184, -185, -186], [-187, -188, -189], [-190, -191, -192], [-193, -194, -195], [-196, -197, -198], [-199, -200, -201], [-202, -203, -204], [-205, -206, -207], [-208, -209, -210], [-211, -212, -213], [-214, -215, -216], [-217, -218, -219], [-220, -221, -222], [-223, -224, -225], [-226, -227, -228], [-229, -230, -231], [-232, -233, -234], [-235, -236, -237], [-238, -239, -240], [-241, -242, -243], [-244, -245, -246], [-247, -248, -249], [-250, -251, -252], [-253, -254, -255], [-256, -257, -258], [-259, -260, -261], [-262, -263, -264], [-265, -266, -267], [-268, -269, -270], [-271, -272, -273], [-274, -275, -276], [-277, -278, -279], [-280, -281, -282], [-283, -284, -285], [-286, -287, -288], [-289, -290, -291], [-292, -293, -294], [-295, -296, -297], [-298, -299, -300]]}]
````

### 60. P20 · run 2 · hard

- **Categoría:** Arity / index error (invalid literal, var count or schema)
- **¿Detectable sin ground truth?** Yes
- **Estado del solver/validador:** SCHEMA_ERROR
- **Diagnóstico (usa el CNF de referencia):** literal inválido en la cláusula 10: -31 (debe ser entero no nulo con |lit| <= 30)

````text
{"num_vars": 30, "clauses": [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24], [25, 26, 27], [28, 29, 30], [-31, -32, -33], [-34, -35, -36], [-37, -38, -39], [-40, -41, -42], [-43, -44, -45], [-46, -47, -48], [-49, -50, -51], [-52, -53, -54], [-55, -56, -57], [-58, -59, -60], [-61, -62, -63], [-64, -65, -66], [-67, -68, -69], [-70, -71, -72], [-73, -74, -75], [-76, -77, -78], [-79, -80, -81], [-82, -83, -84], [-85, -86, -87], [-88, -89, -90], [-91, -92, -93], [-94, -95, -96], [-97, -98, -99], [-100, -101, -102], [-103, -104, -105], [-106, -107, -108], [-109, -110, -111], [-112, -113, -114], [-115, -116, -117], [-118, -119, -120], [-121, -122, -123], [-124, -125, -126], [-127, -128, -129], [-130, -131, -132], [-133, -134, -135], [-136, -137, -138], [-139, -140, -141], [-142, -143, -144], [-145, -146, -147], [-148, -149, -150], [-151, -152, -153], [-154, -155, -156], [-157, -158, -159], [-160, -161, -162], [-163, -164, -165], [-166, -167, -168], [-169, -170, -171], [-172, -173, -174], [-175, -176, -177], [-178, -179, -180], [-181, -182, -183], [-184, -185, -186], [-187, -188, -189], [-190, -191, -192], [-193, -194, -195], [-196, -197, -198], [-199, -200, -201], [-202, -203, -204], [-205, -206, -207], [-208, -209, -210], [-211, -212, -213], [-214, -215, -216], [-217, -218, -219], [-220, -221, -222], [-223, -224, -225], [-226, -227, -228], [-229, -230, -231], [-232, -233, -234], [-235, -236, -237], [-238, -239, -240], [-241, -242, -243], [-244, -245, -246], [-247, -248, -249], [-250, -251, -252], [-253, -254, -255], [-256, -257, -258], [-259, -260, -261], [-262, -263, -264], [-265, -266, -267], [-268, -269, -270], [-271, -272, -273], [-274, -275, -276], [-277, -278, -279], [-280, -281, -282], [-283, -284, -285], [-286, -287, -288], [-289, -290, -291], [-292, -293, -294], [-295, -296, -297], [-298, -299, -300]]}]
````
