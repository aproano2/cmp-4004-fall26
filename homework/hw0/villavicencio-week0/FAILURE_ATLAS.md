# Failure Atlas

### [Wk0] El LLM devuelve los elementos correctos pero en el orden incorrecto

**Setup:** Se pidió al LLM ordenar una lista de enteros en orden ascendente. Se utilizó el backend y modelo configurados en el notebook. La instancia utilizada fue `n5-2`, con una lista de 5 elementos.

**Classical:** `[22, 215, 279, 285, 590]`. Este es el resultado correcto porque `sorted()` ordena la lista de entrada en orden ascendente y conserva exactamente los mismos elementos.

**LLM:** `[22, 279, 285, 215, 590]`

**Category:** wrong-but-confident

**Why it matters:** Si esta salida se utilizara directamente en un programa, una lista incorrectamente ordenada podría producir resultados o decisiones posteriores incorrectos.
