# Ejecucion

Desde la raiz del repositorio. Requiere Python y Ollama con `llama3.2:3b`; para figuras, `matplotlib`.

Un problema:
```powershell
python -B homework/hw2/Munoz/code/run_arms.py --arm all --id SAT-01
```

Experimento completo:
```powershell
python -B homework/hw2/Munoz/code/run_experiment.py
```

Agrega `--resume` para continuar resultados existentes o `--output otra_carpeta` para una nueva ejecucion.

Pruebas y figuras:
```powershell
python -B -m unittest discover -s homework/hw2/Munoz/code -p test_arms.py
python -B homework/hw2/Munoz/code/plot_results.py
```
