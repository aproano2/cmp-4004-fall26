# Registro de uso de IA

**Estudiante:** Antonio Munoz. Entrega individual.
**Herramienta de asistencia:** Codex. **Modelo experimental:** llama3.2:3b en Ollama.

## 2026-11-18 - Desarrollo y revision

**Solicitud:** construir y ejecutar HW2 con SAT, analizar fallos y redactar el informe.

**Aporte de la IA:**
- Redacto los 20 problemas, CNF y justificaciones; comprobo 1552 asignaciones y testigos con DPLL.
- Implemento los cuatro brazos, refinamiento, pruebas y registro de resultados.
- Ejecuto la primera repeticion y parte de la segunda; propuso tres repeticiones. El limite de refinamiento proviene de HW2.
- Clasifico los fallos, genero las figuras y redacto el informe.

**Aporte del estudiante:**
- Eligio SAT y Ollama, aprobo el dominio y solicito trabajo por etapas, codigo simple y salida legible.
- Reviso SAT-01 y SAT-02 con explicaciones de IA y confirmo la revision de los 20 enunciados, clausulas y testigos.
- Completo las ejecuciones con `--resume`, ejecuto los comandos de analisis y genero la taxonomia con asistencia.
- Solicito reducir explicaciones y comentarios. Se restauraron numeros sustituidos por marcas `x` en SAT-01; no se documentaron correcciones logicas independientes.

**Comprension documentada:** revision guiada de variables, negacion, disyuncion, implicacion y eleccion exclusiva en SAT-01 y SAT-02. No consta formalizacion ni clasificacion independiente del estudiante.

**Trazabilidad:** 240 resultados y 409 registros de intentos. Las pruebas previas de SAT-01 estan en la cache, fuera de los CSV; sus prompts de sistema coinciden con los finales. No hubo conjunto de desarrollo separado. Se elimino el generador del dataset; se conserva el dataset final.

### Revision adicional por IA

La IA comprobo 440 asignaciones de SAT-03, SAT-07, SAT-11, SAT-15 y SAT-19 sin discrepancias con el dataset, y diez fallos de B con clasificaciones coincidentes. No fue una revision ciega ni trabajo independiente del estudiante. Los archivos auxiliares de esta revision se retiraron a peticion del estudiante.

## 2026-11-19 - Depuracion

**Solicitud:** eliminar texto y codigo redundantes.
**Aporte de la IA:** compacto el informe, los README y este registro; elimino el script y la evidencia de revision adicional, explicaciones y copias repetidas. Conservo datos experimentales, pruebas, prompts y salidas originales.
