# HW2 — Enunciados públicos (20 problemas CSP de Ingeniería Industrial)

> Este archivo **no** contiene modelos ni soluciones. Es seguro mostrarlo a los LLM de los brazos B, B′ y C.

## F01 — Asignación de órdenes a máquinas

**Área:** Producción · **Dificultad:** Fácil

Un taller metalmecánico debe procesar hoy tres órdenes de producción: OP1 (un eje de acero), OP2 (una brida de aluminio con ranuras) y OP3 (una carcasa de polímero). Dispone de tres máquinas: un centro CNC, un torno y una fresadora. Cada orden se procesa completa en una sola máquina.

**Reglas:**

1. Cada máquina procesa exactamente una orden y cada orden va a exactamente una máquina.
2. El torno no puede hacer ranuras, por lo que la OP2 no puede asignarse al torno.
3. El torno está calibrado solo para metales, por lo que la OP3 no puede asignarse al torno.
4. La sujeción de la fresadora no es compatible con la carcasa de polímero, por lo que la OP3 no puede asignarse a la fresadora.

**Pregunta:** ¿Qué máquina procesa cada orden (OP1, OP2 y OP3)?

---

## F02 — Asignación de muelles de carga

**Área:** Logística · **Dificultad:** Fácil

Un centro de distribución recibe a la misma hora tres camiones: C1 (refrigerado), C2 (carga a granel) y C3 (paquetería). Hay tres muelles numerados 1, 2 y 3, ubicados uno junto al otro en ese orden, de modo que los muelles 1 y 2 son vecinos, y los muelles 2 y 3 también.

**Reglas:**

1. Cada muelle atiende exactamente a un camión.
2. Solo los muelles 1 y 3 tienen conexión eléctrica para equipos de frío, y el camión refrigerado C1 la necesita.
3. El camión de granel C2 necesita la rampa niveladora, que no existe en el muelle 3.
4. C3 debe quedar en un muelle vecino al de C1, porque ambos comparten el mismo montacargas.

**Pregunta:** ¿En qué muelle (1, 2 o 3) se descarga cada camión (C1, C2 y C3)?

---

## F03 — Calendario de mantenimiento preventivo

**Área:** Mantenimiento · **Dificultad:** Fácil

La jefatura de mantenimiento de una planta de alimentos debe programar el mantenimiento preventivo de cuatro equipos: el compresor, la caldera, la banda transportadora y la prensa. Hay cuatro días disponibles, numerados del 1 (lunes) al 4 (jueves), y la cuadrilla atiende exactamente un equipo por día.

**Reglas:**

1. Cada equipo recibe mantenimiento en un día distinto (uno por día).
2. La prensa es neumática, por lo que el compresor debe revisarse en un día anterior al de la prensa.
3. La caldera no puede detenerse el día 1 por un pedido urgente.
4. La banda debe revisarse exactamente el día siguiente al de la caldera, porque usa el mismo electricista.
5. La prensa no puede revisarse el día 4, porque ese día se usa para una auditoría.

**Pregunta:** ¿Qué día (1 a 4) recibe mantenimiento cada equipo?

---

## F04 — Secuencia de operaciones en una estación

**Área:** Producción · **Dificultad:** Fácil

En una estación de fabricación de soportes metálicos se realizan cuatro operaciones, una después de otra, ocupando las posiciones 1, 2, 3 y 4 de la secuencia (1 es la primera): corte, soldadura, pintura e inspección.

**Reglas:**

1. Cada operación ocupa una posición distinta.
2. El corte debe realizarse antes que la soldadura.
3. La soldadura debe realizarse antes que la pintura.
4. La inspección debe hacerse después de la soldadura.
5. La inspección no puede ir inmediatamente después de la pintura, porque la pintura aún estaría húmeda.

**Pregunta:** ¿En qué posición (1 a 4) se realiza cada operación?

---

## F05 — Ubicación de productos en zonas del almacén

**Área:** Inventarios · **Dificultad:** Fácil

Un almacén tiene tres zonas: A (con ventilación forzada), B (estándar) y C (refrigerada). Hay que ubicar cuatro productos: ácido, alimento, solvente y papel. Cada producto se guarda completo en una sola zona.

**Reglas:**

1. Cada zona puede contener como máximo dos de estos productos.
2. El alimento debe guardarse en la zona refrigerada.
3. Ni el ácido ni el solvente pueden compartir zona con el alimento.
4. El ácido y el solvente reaccionan entre sí y no pueden compartir zona.
5. El solvente es volátil y debe guardarse en la zona con ventilación forzada.
6. El papel no puede ir en la zona refrigerada (absorbe humedad) ni compartir zona con el solvente (es inflamable).

**Pregunta:** ¿En qué zona (A, B o C) se guarda cada producto?

---

## F06 — Asignación de inspectores de calidad

**Área:** Asignación de recursos · **Dificultad:** Fácil

Tres inspectores de calidad, Rosa, Pablo y Elena, deben revisar cuatro lotes recibidos hoy. LOTE1 y LOTE3 son de componentes eléctricos, LOTE2 es de insumos alimenticios y LOTE4 es metalmecánico. Rosa está certificada en eléctricos y metalmecánica; Pablo en alimentos y metalmecánica; Elena en eléctricos y alimentos. Cada lote es revisado por un solo inspector.

**Reglas:**

1. Cada lote solo puede ser revisado por un inspector certificado en su tipo de producto.
2. Los dos lotes eléctricos deben ser revisados por inspectores distintos.
3. Elena no puede revisar el LOTE2 por conflicto de interés con el proveedor.
4. El LOTE1 y el LOTE4 vienen del mismo proveedor y deben ser revisados por el mismo inspector.

**Pregunta:** ¿Qué inspector revisa cada lote (LOTE1 a LOTE4)?

---

## F07 — Asignación de operarios a turnos

**Área:** Turnos de trabajo · **Dificultad:** Fácil

Una planta de envasado opera en tres turnos: mañana, tarde y noche. Cuatro operarios, Ana, Bruno, Carla y Diego, deben asignarse cada uno a exactamente un turno para la próxima semana.

**Reglas:**

1. Cada turno debe tener al menos un operario.
2. Ana y Bruno no pueden estar en el mismo turno.
3. Carla no trabaja de noche.
4. Diego está en entrenamiento y debe estar en el mismo turno que Carla.
5. Bruno no puede trabajar en el turno de la mañana.
6. Ana no puede trabajar de noche.
7. Diego no puede trabajar en el turno de la tarde.

**Pregunta:** ¿En qué turno (mañana, tarde o noche) trabaja cada operario?

---

## M08 — Secuenciación de pedidos en una inyectora

**Área:** Producción · **Dificultad:** Intermedio

Una inyectora de plásticos debe procesar cinco pedidos, P1 a P5, uno tras otro. Cada pedido ocupa una posición de la secuencia del día, de la 1 (primera) a la 5 (última).

**Reglas:**

1. Cada pedido ocupa una posición distinta.
2. P2 es urgente y debe ir en una de las dos primeras posiciones.
3. P3 reutiliza el molde que se ajusta durante P1, así que P1 debe ir antes que P3.
4. P4 y P5 usan el mismo colorante y deben ir en posiciones consecutivas (en cualquier orden).
5. P3 debe ir antes que P5.
6. La materia prima de P1 llega tarde, por lo que P1 no puede ir en la posición 1.
7. P5 requiere una limpieza posterior larga, por lo que no puede ser el último pedido del día.

**Pregunta:** ¿En qué posición (1 a 5) se procesa cada pedido?

---

## M09 — Asignación de operarios a estaciones de trabajo

**Área:** Asignación de recursos · **Dificultad:** Intermedio

Una línea de ensamble de electrodomésticos tiene tres estaciones: ENSAMBLE, EMPAQUE y CONTROL (control de calidad). Seis operarios, Ana, Beto, Caro, Dani, Edu y Fer, deben asignarse cada uno a exactamente una estación. Solo Ana, Beto y Dani tienen la certificación de control de calidad.

**Reglas:**

1. Cada estación debe tener exactamente dos operarios.
2. En CONTROL solo pueden trabajar operarios certificados.
3. Ana y Beto son supervisores de relevo y no pueden estar en la misma estación.
4. Edu y Fer son nuevos y no pueden estar en la misma estación.
5. Caro es la tutora de Edu y debe estar en la misma estación que él.
6. Dani tiene una restricción médica y no puede trabajar en EMPAQUE.
7. Ana y Fer no pueden estar en la misma estación.
8. Beto no tiene el curso de la máquina de ensamble, así que no puede trabajar en ENSAMBLE.

**Pregunta:** ¿En qué estación trabaja cada operario?

---

## M10 — Asignación de clientes a vehículos de reparto

**Área:** Logística · **Dificultad:** Intermedio

Una distribuidora debe atender mañana a cinco clientes con tres vehículos. Capacidades: V1 = 10 toneladas, V2 = 8 toneladas y V3 = 6 toneladas. Demandas: C1 = 6 t, C2 = 3 t, C3 = 5 t, C4 = 2 t y C5 = 4 t. Cada cliente es atendido completo por un solo vehículo. Solo V1 tiene equipo de refrigeración.

**Reglas:**

1. La carga total asignada a cada vehículo no puede superar su capacidad.
2. El pedido de C2 es perecible y requiere refrigeración.
3. C4 está en el centro histórico, donde solo puede circular V3.
4. C1 y C3 están en direcciones opuestas de la ciudad y no pueden ir en el mismo vehículo.
5. C2 y C3 son sucursales de la misma cadena y deben ser atendidas por el mismo vehículo.
6. Los tres vehículos deben salir con al menos un cliente.

**Pregunta:** ¿Qué vehículo (V1, V2 o V3) atiende a cada cliente?

---

## M11 — Programa de mantenimiento con capacidad limitada

**Área:** Mantenimiento · **Dificultad:** Intermedio

Una planta textil debe dar mantenimiento a cinco equipos durante una parada de tres días (días 1, 2 y 3): el generador, el tablero eléctrico, el compresor, el secador de aire y el horno de termofijado. Cada equipo se atiende completo en un solo día.

**Reglas:**

1. La cuadrilla puede atender como máximo dos equipos por día.
2. El generador debe atenderse en un día anterior al del tablero, porque es la energía de respaldo durante esa intervención.
3. El compresor y el secador forman el mismo sistema neumático y se atienden el mismo día.
4. El horno no puede atenderse el día 1 porque todavía estará caliente.
5. El tablero no puede atenderse el día 3, porque ese día llega el inspector eléctrico externo para certificarlo ya reparado.

**Pregunta:** ¿Qué día (1, 2 o 3) se atiende cada equipo?

---

## M12 — Días libres del personal de bodega

**Área:** Turnos de trabajo · **Dificultad:** Intermedio

Una bodega trabaja de lunes a viernes (días 1 = lunes a 5 = viernes). Cada uno de sus cinco trabajadores, Luis, María, Jorge, Sofía y Pedro, tiene exactamente un día libre a la semana. Jorge y Sofía son los únicos operadores de montacargas.

**Reglas:**

1. Para mantener la cobertura, no puede haber dos trabajadores libres el mismo día.
2. Los días libres de los dos operadores de montacargas no pueden ser consecutivos ni iguales (debe haber al menos un día entre ellos).
3. María estudia y su día libre debe ser lunes o viernes.
4. Pedro es el encargado de recepción y no puede librar ni lunes ni viernes, que son días de mayor recepción.
5. Luis debe librar un día anterior al de Pedro.
6. Sofía libra después que Jorge.
7. María libra el día inmediatamente posterior al de Sofía.
8. Luis no puede librar el lunes, porque ese día hace el inventario semanal.

**Pregunta:** ¿Qué día de la semana (1 a 5) libra cada trabajador?

---

## M13 — Ubicación de productos en una estantería

**Área:** Inventarios · **Dificultad:** Intermedio

En una bodega de repuestos hay una estantería de tres niveles: nivel 1 (piso), nivel 2 (altura de la cintura) y nivel 3 (alto). Deben ubicarse seis productos: motor, tornillos, cable, pintura, filtros y guantes. El motor y la pintura pesan más de 20 kg, y los tornillos y los guantes son los de mayor rotación.

**Reglas:**

1. Cada nivel tiene espacio para exactamente dos productos.
2. Los productos de más de 20 kg no pueden ir en el nivel 3.
3. Los dos productos de mayor rotación no pueden ir en el nivel 3.
4. La pintura es líquida y no puede estar en un nivel superior al del cable, para no gotear sobre él.
5. El motor y la pintura no pueden compartir nivel (no caben juntos).
6. Los tornillos y los guantes no pueden compartir nivel, para separar los dos puntos de mayor tránsito.
7. La pintura no puede compartir nivel con los guantes, para evitar que se manchen.
8. Los tornillos no van en el nivel 1, para evitar que el operario se agache con tanta frecuencia.

**Pregunta:** ¿En qué nivel (1, 2 o 3) se ubica cada producto?

---

## M14 — Distribución en planta de departamentos

**Área:** Producción · **Dificultad:** Intermedio

Se va a redistribuir una nave industrial con seis espacios en línea recta, numerados del 1 al 6; dos espacios son vecinos si sus números difieren en 1. Deben ubicarse seis departamentos: recepción, corte, soldadura, ensamble, pintura y despacho, uno por espacio.

**Reglas:**

1. Cada departamento ocupa un espacio distinto.
2. Recepción y despacho deben estar en los dos extremos de la nave (espacios 1 y 6, en cualquier orden).
3. Corte debe estar junto a recepción, porque recibe la materia prima.
4. Soldadura debe estar junto a corte.
5. Pintura no puede estar junto a corte ni junto a soldadura, por el riesgo de chispas.
6. Ensamble debe estar junto a pintura.
7. La toma de corriente trifásica que necesita corte solo existe en los espacios 1, 2 y 3.

**Pregunta:** ¿En qué espacio (1 a 6) queda cada departamento?

---

## D15 — Programación de un taller de fabricación (job shop)

**Área:** Producción · **Dificultad:** Difícil

Un taller debe fabricar hoy tres pedidos, A, B y C, durante una jornada de 8 horas (las horas se cuentan desde 0, inicio de la jornada, hasta 8, fin de la jornada). Cada operación empieza en una hora entera y se ejecuta sin interrupción. Las operaciones son:
- A1: corte de A, 2 h; A2: doblado de A, 1 h.
- B1: corte de B, 1 h; B2: doblado de B, 2 h.
- C1: corte de C, 2 h; C2: doblado de C, 2 h; C3: pintura de C, 1 h.
Hay una sola cortadora, una sola dobladora y una sola cabina de pintura. La pregunta es la hora de inicio de cada operación.

**Reglas:**

1. Dentro de cada pedido, una operación solo puede empezar cuando terminó la anterior (A1 antes que A2; B1 antes que B2; C1 antes que C2 y C2 antes que C3).
2. La cortadora solo puede hacer una operación a la vez (A1, B1 y C1 no pueden solaparse).
3. La dobladora solo puede hacer una operación a la vez (A2, B2 y C2 no pueden solaparse).
4. Todas las operaciones deben terminar a más tardar en la hora 8 (fin de la jornada).
5. El doblado de B requiere cambiar el dado de la dobladora, por lo que B2 solo puede empezar después de que termine A2.
6. La pintura de C debe empezar exactamente cuando termina su doblado (C2), para que la pieza no se oxide.
7. La cabina de pintura está ocupada por otro cliente hasta la hora 7, así que C3 no puede empezar antes de la hora 7.

**Pregunta:** ¿A qué hora (0 a 7) empieza cada operación (A1, A2, B1, B2, C1, C2, C3)?

---

## D16 — Asignación de pedidos a líneas de producción con capacidad

**Área:** Producción · **Dificultad:** Difícil

Una planta de envases tiene tres líneas de producción: L1 y L2, con 8 horas disponibles cada una, y L3, con 6 horas disponibles. Debe asignar ocho pedidos, cada uno completo a una sola línea. Duración de cada pedido: P1 = 4 h, P2 = 3 h, P3 = 2 h, P4 = 5 h, P5 = 3 h, P6 = 2 h, P7 = 1 h y P8 = 2 h. P3 y P6 son envases para alimentos; P7 usa un recubrimiento con lubricante industrial.

**Reglas:**

1. La suma de las duraciones de los pedidos asignados a una línea no puede superar las horas disponibles de esa línea.
2. L3 es una línea pequeña y no puede procesar pedidos de más de 3 horas.
3. P2 y P5 son del mismo cliente y deben producirse en la misma línea.
4. Los envases para alimentos no pueden producirse en la misma línea que P7.
5. Si P1 se asigna a L1, entonces P8 debe asignarse a L3.

**Pregunta:** ¿A qué línea (L1, L2 o L3) se asigna cada pedido (P1 a P8)?

---

## D17 — Programación de turnos con habilidades y cobertura

**Área:** Turnos de trabajo · **Dificultad:** Difícil

Una planta química opera en tres turnos: mañana, tarde y noche. Ocho técnicos deben asignarse cada uno a exactamente un turno: Andrés, Beatriz, Carlos, Diana, Esteban, Fabiola, Gabriel y Helena. Andrés y Beatriz son supervisores; Carlos, Fabiola y Helena son los únicos electricistas.

**Reglas:**

1. La mañana y la tarde deben tener exactamente tres técnicos cada una, y la noche exactamente dos.
2. Cada turno debe tener exactamente un electricista.
3. Los dos supervisores no pueden estar en el mismo turno.
4. El turno de noche debe tener al menos un supervisor.
5. Diana y Esteban comparten transporte y deben estar en el mismo turno.
6. Gabriel tiene clases por la mañana y no puede trabajar en ese turno.
7. Si Helena trabaja de noche, entonces Andrés también debe trabajar de noche.
8. Fabiola no puede trabajar de noche.
9. Beatriz no puede trabajar en la tarde.
10. Fabiola está capacitando a Diana, así que ambas deben estar en el mismo turno.

**Pregunta:** ¿En qué turno (mañana, tarde o noche) trabaja cada técnico?

---

## D18 — Plan semanal de mantenimiento de equipos

**Área:** Mantenimiento · **Dificultad:** Difícil

Un taller de manufactura debe programar el mantenimiento de siete equipos en una semana laboral de cinco días (día 1 = lunes, ..., día 5 = viernes): dos tornos de la línea A (TORNO1 y TORNO2), dos fresadoras de la línea B (FRESA1 y FRESA2), una prensa, un compresor y un puente grúa. Cada equipo se atiende completo en un solo día.

**Reglas:**

1. Se pueden atender como máximo dos equipos por día.
2. El lunes (día 1) y el miércoles (día 3) hay capacitación del personal, así que esos días se atiende como máximo un equipo.
3. Para no detener una línea completa, dos equipos de la misma línea no pueden atenderse el mismo día.
4. La prensa se desmonta con el puente grúa recién revisado, así que la prensa se atiende exactamente el día siguiente al de la grúa.
5. La prensa fabrica los bujes de repuesto de los tornos, así que ambos tornos se atienden en días posteriores al de la prensa.
6. Los dos tornos usan el mismo kit de repuestos y se atienden en días consecutivos, primero TORNO1 y luego TORNO2.
7. Los tornos deben estar operativos el viernes, así que ninguno puede atenderse el día 5.
8. Tornos y fresadoras los atiende el mismo mecánico, así que ninguna fresadora puede atenderse el mismo día que un torno.
9. Las fresadoras se prueban con aire comprimido, así que ninguna puede atenderse el mismo día que el compresor.
10. El compresor y la prensa usan al mismo electricista, así que no pueden atenderse el mismo día.
11. FRESA1 es la de mayor uso y debe atenderse antes que FRESA2.

**Pregunta:** ¿Qué día (1 a 5) recibe mantenimiento cada equipo?

---

## D19 — Plan maestro de producción por semanas

**Área:** Producción · **Dificultad:** Difícil

Una fábrica de muebles debe programar nueve lotes (L1 a L9) en las próximas tres semanas (semanas 1, 2 y 3). Cada lote se produce completo en una sola semana. Horas requeridas: L1 = 10, L2 = 8, L3 = 12, L4 = 6, L5 = 10, L6 = 8, L7 = 14, L8 = 6 y L9 = 6. La planta dispone de 30 horas por semana. L1 fabrica los componentes que luego se ensamblan en L5. L2 y L6 pertenecen a la misma familia de productos (mismo acabado).

**Reglas:**

1. Las horas totales de los lotes de una misma semana no pueden superar 30.
2. L3 debe entregarse al final de la semana 1.
3. L7 debe entregarse a más tardar al final de la semana 2.
4. Los componentes de L1 deben producirse en una semana anterior a la del ensamble L5.
5. L2 y L6 deben producirse en la misma semana para aprovechar la preparación del acabado.
6. Por los cambios de formato, en cada semana se pueden producir como máximo cuatro lotes.
7. L8 usa los moldes que se fabrican en L4, así que L4 debe producirse en una semana anterior a la de L8.
8. L9 es la versión de exportación de L4 y debe producirse en la misma semana que L4.

**Pregunta:** ¿En qué semana (1, 2 o 3) se produce cada lote (L1 a L9)?

---

## D20 — Programación de ventanas en un centro de cross-docking

**Área:** Logística · **Dificultad:** Difícil

Un centro de cross-docking tiene dos muelles y cuatro ventanas horarias consecutivas (1, 2, 3 y 4). Ocho camiones, T1 a T8, deben recibir cada uno una ventana. T1 y T2 son refrigerados. T3 trae componentes que luego recoge T6. T4 y T5 se transfieren carga directamente de uno a otro.

**Reglas:**

1. Como hay dos muelles, en cada ventana pueden atenderse como máximo dos camiones.
2. Los camiones refrigerados deben atenderse en las ventanas 1 o 2.
3. T6 recoge lo que trae T3, así que T6 debe atenderse en una ventana posterior a la de T3.
4. T4 y T5 deben atenderse en la misma ventana para hacer la transferencia directa.
5. T7 llega desde otra ciudad y solo puede atenderse en las ventanas 3 o 4.
6. Si T8 se atiende en la ventana 1, entonces T2 debe atenderse en la ventana 2.
7. Los dos refrigerados no pueden atenderse en la misma ventana, porque solo hay una toma de frío.
8. T6 debe atenderse exactamente en la ventana siguiente a la de T3, para que la mercadería no espere en el andén.
9. T8 debe atenderse en una ventana anterior a la de T7.

**Pregunta:** ¿En qué ventana (1 a 4) se atiende cada camión (T1 a T8)?

---
