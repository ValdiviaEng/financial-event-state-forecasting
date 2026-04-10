# Auditoría profunda del proyecto de pronóstico EOD multimodal multi‑horizonte basado en “event state”

## Evidencia disponible y memoria del proyecto

### Qué está “establecido por evidencia del proyecto”
De acuerdo con la documentación central del repositorio, el proyecto se define explícitamente como un sistema de investigación **end‑of‑day (EOD)**, **multimodal** y **multi‑horizonte** para un trabajo de tesis de nivel Maestría; y se diferencia explícitamente de un “trading bot”, de HFT/intraday y de la predicción directa del **nivel de precio**. fileciteturn1file1L1-L70

El repositorio se auto‑ubica en una fase “late foundation / early experimentation” (fundación tardía / experimentación temprana) y enumera como implementados: estructura del proyecto, contratos de datos, ensamblaje de datasets raw/interim/final, manejo de splits, features de mercado, labels, cache de embeddings, agregación event‑state, soporte de company‑KB, baselines market‑only, un primer entrenamiento multimodal y herramientas iniciales de evaluación/ablación. Esta afirmación es evidencia **declarativa** (lo afirma la documentación); **no es evidencia de validez científica** por sí sola. fileciteturn1file1L5-L20

El “runbook” (ExecutionFlow) afirma que el flujo actual:
- usa **parquet/JSON/manifests** como capa de almacenamiento y **no usa** una base SQL,
- usa **Twelve Data** para mercado, **Finnhub** para news y **SEC EDGAR** para company KB,
- y reconoce explícitamente que aún **no existe CLI dedicada** para pasos críticos como ingesta de split events, generación masiva de precios ajustados, construcción del embedding cache y generación batch del event‑state (aunque dice que esos pasos están “soportados” vía snippets). fileciteturn1file11L1-L35

El plan de ejecución del repositorio indica que **stages 0–14** están implementados en “first‑pass form” y que la fase de “documentation hardening” también está completa en primera pasada. Además, codifica principios de disciplina científica/ingeniería como “split‑handling before labels” y “baselines before multimodal complexity”. fileciteturn1file9L9-L40

Finalmente, el árbol del repositorio evidencia una estructura que incluye `configs/`, `data/` (raw/interim/final/embeddings/kb/manifests), `docs/`, `runs/`, `reports/`, `src/` y un conjunto amplio de `tests/`. También muestra artefactos de panel “smoke” en `artifacts/` (por ejemplo, `panel_stage12_smoke.parquet`, `panel_stage13_smoke.parquet`) que sugieren que existen datasets finales sintéticos o de verificación rápida. fileciteturn1file6L1-L35

### Evolución del proyecto y pivotes
El archivo de “historial” del proyecto (project_extra_data) resume que el proyecto originalmente sufrió fricción por desalineación entre un repositorio viejo (con supuestos de AlphaVantage/estructuras incompletas) y el framing real deseado. Posteriormente, el repositorio fue restructurado hacia un “blueprint‑first scaffold” y luego avanzado hacia una implementación “first‑pass” con tests y pipeline. fileciteturn1file8L1-L110

**Punto clave (establecido por evidencia del proyecto):** el repositorio pretende ser una plataforma de investigación disciplinada (contratos de datos + capas raw/interim/final + tests offline + pruebas de leakage/alignment + ejecución reproducible). fileciteturn1file0L14-L75

## Definición académica y coherencia científica del planteamiento

### Formulación del problema (coherente con literatura, pero requiere disciplina de evaluación)
El framing del repositorio formula el problema como:

Para cada activo \(i\) y fecha de trading \(t\), construir un vector de información EOD \(x_{i,t}\) (OHLCV + derivados), y un conjunto de noticias \(\mathcal{N}_{i,\le t}\) disponibles **as‑of** el cierre, para predecir outcomes \(y_{i,t}^{(\Delta)}\) en \(\Delta \in \{1,5,20, (60)\}\) días. Se enfatiza que \(y\) no es “precio futuro”, sino retornos (posiblemente abnormal/excess), probabilidad de downside, y/o outputs con incertidumbre (escala/cuantiles). fileciteturn1file1L41-L75

Ese framing es consistente con el enfoque estándar en finanzas cuantitativas: trabajar con **retornos** (y variantes neutralizadas por mercado/factores) es más defendible que predecir niveles de precio por no‑estacionariedad y por confusiones de escala. Además, la hipótesis de mercados eficientes (en diversas formas) justifica ser extremadamente conservador al interpretar “predictibilidad” y obliga a evaluación fuera de muestra con control estricto de leakage. citeturn3search2turn10search7

### Por qué “event state” y no “impacto de noticia individual”
El repositorio explicita una postura metodológica: evitar el supuesto naïve de “una noticia → un impacto aislado”, porque el flujo de noticias es continuo, superpuesto y narrativo. Esto es coherente con lo que la literatura de **event studies** advierte: medir efectos “de un evento” es factible en ventanas relativamente limpias, pero se complica por confusores, eventos superpuestos y problemas de identificación. citeturn3search11

En términos de investigación, modelar un **estado informacional agregado** (un embedding/estado latente que resume noticias recientes) es una hipótesis **predictiva**, no causal: buscas “señal incremental” bajo evaluación estricta, no atribución limpia de causalidad a un artículo. Esa honestidad metodológica es una fortaleza del proyecto, siempre que la ingeniería de alineación temporal sea impecable (ver sección de riesgos). fileciteturn1file1L33-L40

### Por qué multimodalidad y multi‑horizonte tienen sentido aquí
Multimodalidad: el proyecto combina series numéricas EOD (mercado) con texto con timestamps (news) y potencialmente covariables estáticas o de evolución lenta (company KB/perfiles). La taxonomía clásica de multimodal ML sugiere que los desafíos centrales no son “modelos fancy”, sino: **representación**, **alineación**, **fusión**, y **generalización fuera de muestra**. citeturn4search5

Multi‑horizonte: el repositorio argumenta que \(1d\), \(5d\), \(20d\), \(60d\) reflejan mecanismos distintos (reacción inmediata vs drift vs repricing). Esto es consistente con enfoques modernos de forecasting multi‑paso donde se producen “heads” por horizonte y donde covariables estáticas/dinámicas se tratan explícitamente. Un referente conceptual fuerte es Temporal Fusion Transformer (TFT), aunque tu tesis no necesita “ser TFT”; necesita capturar el principio de **multi‑horizon outputs con covariables estáticas y dinámicas**. citeturn9view0turn1file1L100-L108

## Realidad del repositorio vs teoría declarada

### Lo que el repositorio **sí** parece soportar (evidencia directa)
1) **Disciplina de capas y reproducibilidad.** `ExecutionFlow.md` afirma que el almacenamiento es parquet/JSON/manifests y que el flujo actual está documentado como runbook, con pasos de validación previos (lint/tests offline) antes de consumir cuota de APIs. fileciteturn1file11L1-L20

2) **Cultura de testing estratificado.** `Expanded_Testing.md` describe cuatro capas: unit tests offline, integration tests sintéticos, smoke tests de entrenamiento/evaluación, y tests live opcionales con proveedores (consumen API real). También afirma que la mayoría de pruebas no requiere pre‑ejecutar el pipeline real; solo los tests live dependen de `.env` y cuota. fileciteturn1file0L16-L71

3) **Enfoque de “correctness→reproducibility→leakage safety→efficiency→sophistication”.** Esto se reitera como principio rector del proyecto (en README y execution plan), lo cual es consistente con una tesis defendible. fileciteturn1file1L15-L20turn1file9L33-L40

### Brechas y tensiones (donde la teoría puede estar más fuerte que la realidad operativa)
**Brecha crítica: corporate actions (splits/dividendos) vs confiabilidad de labels.**  
En README se establece explícitamente un hallazgo verificado: la serie almacenada “parece no estar split‑adjusted” (ejemplo: ventana de split de AAPL 2020‑08‑31). Y señala una consecuencia fuerte: “no serious label generation should trust raw OHLCV without resolving this issue.” fileciteturn1file1L110-L139

Al mismo tiempo, la documentación pública de Twelve Data indica que el endpoint `/time_series` tiene parámetro `adjust` con modos `all/splits/dividends/none`, con default `splits`. **Esto crea una tensión empírica:** si el parámetro realmente ajusta por splits, ¿por qué tu verificación local observó ausencia de back‑adjustment? Dos explicaciones plausibles (aun no verificadas) son: (a) el request no usó el valor correcto (en docs `adjust` es string, no boolean), o (b) la disponibilidad de ajuste o la cobertura de splits depende del plan/mercado/símbolo y no aplica a tu caso real. Cualquiera de las dos exige verificación, y hasta entonces la robustez científica del pipeline multi‑horizonte está en riesgo. citeturn8search0turn1file1

**Paso concreto de verificación (recomendado):** ejecutar un “A/B data check” controlado para 2–3 tickers con splits conocidos (AAPL 2020‑08‑31; NVDA 2021‑07‑20, etc.) comparando retornos diarios extremos y continuidad antes/después, manteniendo constante `interval` y variando solamente `adjust`. Si el ajuste funciona, desaparecerán retornos mecánicos de magnitud ~75% en splits 4:1 (o análogos). Si no desaparecen, el pipeline necesita split events explícitos + back‑adjust interno. Esta lógica está respaldada por prácticas estándar de ajuste de precios (CRSP/Yahoo muestran multiplicadores de split). citeturn11search0turn11search38

**Brecha operativa: el runbook admite pasos “manuales” en módulos clave.**  
ExecutionFlow admite que no hay CLI dedicada para ingesta de split events, generación masiva de precios ajustados, embedding cache y event‑state batch. Eso no invalida la tesis, pero sí sugiere que el repositorio puede estar **más cerca de un “research platform” que de un “pipeline fully productized”**, lo cual influye en qué tan “cerrada” puede ser la contribución empírica dentro del tiempo de una Maestría. fileciteturn1file11L21-L35

### Matriz conceptual de alineación (evidencia vs aspiración)
| Componente de investigación | Evidencia en artefactos del proyecto | Estado de alineación | Importancia científica | Riesgo si queda débil |
|---|---|---|---|---|
| Framing: EOD, multimodal, multi‑horizonte; no trading bot; no price‑level | README lo declara explícitamente | Alto | Alta | Bajo (si se mantiene) |
| Hipótesis: event‑state agrega señal sobre market‑only | README lo declara | Medio‑alto (depende de resultados OOS) | Alta | Alto si no hay disciplina de evaluación |
| Split/corporate actions como prerequisito de labels | README dice que la serie no está ajustada y que es blocking | Alto (como conciencia del riesgo) | Muy alta | Muy alto (labels contaminados) |
| Alineación temporal news “as‑of close” | README y ExecutionFlow lo declaran; no se evidencia aquí una auditoría real de calendarios en datos reales | Plausible pero no verificado en outputs | Muy alta | Muy alto (look‑ahead) |
| Testing y reproducibilidad | Expanded_Testing y ExecutionFlow lo estructuran | Alto en diseño; efectividad empírica depende de cobertura | Alta | Medio |
| Purge/embargo por horizontes solapados | Se enuncia como filosofía (leakage awareness); evidencia detallada de implementación no está disponible en los archivos revisados aquí | Plausible pero no verificado | Alta | Alto (contaminación silenciosa) |
| Company KB (SEC EDGAR) como branch opcional | ExecutionFlow lo menciona y dice que no es requerido para entrenamiento actual; README lo enmarca | Alto como diseño opcional | Media‑alta | Medio (principalmente leakage + scope) |

(Nota de honestidad: esta matriz está limitada a los artefactos disponibles en esta conversación; no incluye inspección directa del código fuente ni logs completos de experimentos reales de news/modeling.)

## Amenazas a la validez y errores comunes que este proyecto debe vencer

### Riesgos “nivel 0”: invalidan conclusiones si ocurren (prioridad máxima)
**Manejo incorrecto de splits/dividendos (contaminación mecánica de retornos).**  
Si usas precios no ajustados para labels multi‑horizonte, un split aparece como un retorno extremo falso y domina tanto el entrenamiento como la evaluación. Ese problema es especialmente peligroso si vas a estudiar “event‑driven forecasting”: el modelo podría “aprender” a asociar ruido corporativo o discontinuidades con señal. La práctica estándar (CRSP/Yahoo) define multiplicadores de splits y dividendos para construir precios ajustados. citeturn11search0turn11search38turn1file1

**Look‑ahead leakage por timestamps y market close (“as‑of close”).**  
En un sistema news→market EOD, el riesgo típico es incluir noticias post‑cierre como si fueran pre‑cierre. Eso genera un boost artificial enorme (porque efectivamente estás usando parte del futuro). La literatura y guías de backtesting tratan look‑ahead como uno de los sesgos más destructivos, frecuentemente por errores de alineación de tiempo y uso indebido de high/low del mismo día. citeturn10search47turn10search8

**Overlapping‑label leakage en multi‑horizonte.**  
Cuando etiquetas \(y_{t}^{(\Delta)}\) usan ventanas futuras, muestras cercanas comparten el mismo futuro parcial; si el split train/test está mal construido, el modelo “ve” información del test indirectamente. El enfoque de “purged CV/embargo” es central en literatura cuantitativa aplicada (e.g., López de Prado). citeturn10search7

**Backtest overfitting / data snooping por exceso de variantes.**  
Tu proyecto explícitamente quiere evaluar muchas ideas (fusion, KB, macro, opciones, etc.). Eso eleva el riesgo de “seleccionar” un ganador espurio. Bailey et al. proponen formalmente el concepto de Probability of Backtest Overfitting (PBO) y explican por qué el desempeño in‑sample no es confiable cuando se prueban muchas configuraciones. citeturn7search8turn7search3

### Riesgos “nivel 1”: distorsionan resultados sin que sea obvio
**Survivorship bias por universo “S&P 500 latest”.**  
El README fija que el universo actual es un snapshot de S&P 500 (~503 tickers) y un pilot subset. Si entrenas 2006–2026 solo con constituyentes actuales, excluyes empresas que salieron del índice por quiebras, M&A, o declive, sesgando conclusiones hacia “sobrevivientes”. En datos académicos, la solución suele ser CRSP/Compustat o constituyentes históricos (frecuentemente pagos). **En tu tesis, esto se debe declarar como limitación o resolverse explícitamente**. fileciteturn1file1L163-L190

**Duplicación/sindicación de noticias (inflación de señal).**  
Si articles llegan duplicados (mismo URL re‑hosted, syndication), el modelo puede usar “conteo de copias” como señal artificial. El repositorio afirma tener deduplicación como parte del diseño y tests para hashing y dedupe; eso es una defensa importante, pero su efectividad en datos reales debe medirse. fileciteturn1file0L88-L140

**Leakage por company profiles “actuales” aplicados al pasado.**  
La idea de company KB (SEC/Wikipedia) es atractiva, pero usar la descripción actual de una empresa para representar 2010 puede filtrar conocimiento post‑hoc (rebranding, M&A, cambios de líneas de negocio). SEC ofrece datos con timestamps de filings; si se usa un profile branch time‑varying, debe ser “point‑in‑time” (as‑of filing date). citeturn1search0turn1search1turn1file1

## Comparación con el estado del arte y lecciones importables

### Dónde cae este proyecto en el mapa de investigación
Este proyecto se ubica en la intersección de:
- **event‑driven forecasting con texto financiero**, donde existen precedentes directos (por ejemplo, Ding et al. proponen un pipeline de extracción/representación de eventos y un modelo profundo para influencias corto/largo plazo). citeturn3search0turn3search3  
- **modelos de representación textual financiera**, donde el “dominio” importa; FinBERT es un ejemplo claro de adaptación de modelos pre‑entrenados al lenguaje financiero para sentimiento (y, por extensión, embeddings más útiles que modelos generalistas). citeturn6view0  
- **forecasting multi‑horizonte con covariables estáticas/dinámicas**, donde TFT es un referente conceptual fuerte para multi‑output heads y mezcla de inputs. citeturn9view0  
- **multimodal ML** como disciplina general (p.ej., el survey de Baltrušaitis et al. organiza los retos de representación/alineación/fusión/co‑learning). citeturn4search5turn4search3  

### Dónde probablemente estás “rezagado” vs sistemas fuertes
**(1) Point‑in‑time data disciplina para todos los inputs.**  
La investigación fuerte en finanzas suele fallar o triunfar por esto: el modelo puede ser mediocre, pero si el pipeline es “as‑of correct” y la evaluación es purged/embargo, el resultado es defendible. Si no, incluso un modelo SOTA puede ser inválido.

**(2) Evaluación probabilística/calibración cuando produces riesgo/incertidumbre.**  
Si escalas hacia outputs \( \hat{\mu}_\Delta, \hat{\sigma}_\Delta \) o cuantiles, debes usar “proper scoring rules” (p. ej., el marco de scoring rules estrictamente apropiadas). citeturn5search1

**(3) Comparación estadística de precisión predictiva, no solo métricas puntuales.**  
Si la tesis discute “mejora vs baseline”, métodos como Diebold‑Mariano (DM) formalizan pruebas de comparación de precisión. Esto no sustituye walk‑forward, pero mejora credibilidad. citeturn5search9

### Lecciones importables, con honestidad sobre alcance
- **De Ding et al.**: la idea de modelar influencias corto/largo plazo de eventos es relevante, pero su pipeline de “event extraction” fino puede ser sobre‑scope para una Maestría; tu enfoque de “estado agregado” es más honesto y probablemente más robusto operacionalmente. citeturn3search0turn3search11  
- **De FinBERT**: (i) embeddings/sentiment financieros especializados suelen superar generalistas en tareas financieras; (ii) fine‑tuning end‑to‑end puede mejorar, pero eleva varianza de entrenamiento y riesgo de sobreajuste si los datos de news no son enormes. citeturn6view0  
- **De TFT**: no necesitas replicar TFT, pero sí adoptar la estructura mental: multi‑horizonte explícito, separar covariables estáticas vs dinámicas, gating/feature selection para robustez. citeturn9view0  
- **De PBO/backtest overfitting**: tu ambición de “torneos” y muchas variantes es científicamente peligrosa si no se controla el número de experimentos y si no se pre‑registra el plan de ablation. citeturn7search8turn7search3  

## Torneo de ocho direcciones de mejora desde el baseline actual

A continuación se construye un torneo de **8 variantes**, todas partiendo del baseline implementado/declared en el repositorio (market features + event‑state + evaluación walk‑forward/leakage‑aware como objetivo), pero cambiando **una dimensión principal** cada una. La lógica del torneo prioriza “accuracy” (predictive quality) y, si se espera empate, desempata por limpieza científica / menor leakage / mayor estabilidad.

### Las ocho variantes candidatas
**V1 — Corporate actions “first‑class” (precios ajustados + QA de discontinuidades).**  
Objetivo: reducir label noise mecánico por splits/dividendos, asegurando continuidad en retornos y features. Está directamente motivado por el hallazgo del proyecto (series no split‑adjusted) y por estándares CRSP/Yahoo. fileciteturn1file1L110-L139turn11search0turn11search38

**V2 — Targets factor‑neutral / abnormal returns como objetivo principal.**  
Objetivo: mover el problema hacia “alpha residual” (menos dominado por beta del mercado), potencialmente elevando señal útil para news y reduciendo ruido común. (Plausible, requiere test; puede fallar si el residual es aún más ruidoso.)

**V3 — Event‑state avanzado: novelty/conflict/density + pooling jerárquico.**  
Objetivo: hacer el estado de eventos sensible a “narrative persistence” y a saturación de noticias (muchas notas sobre el mismo tema). (Especulativo: puede mejorar robustez en períodos “event‑dense”, pero también puede sobreajustar.)

**V4 — Objetivo de ranking (cross‑sectional) como primera clase.**  
Objetivo: en lugar de minimizar error de retorno punto a punto, optimizar ordenar acciones por score esperado (por día y horizonte). Muchas estrategias cuantitativas se evalúan mejor por ranking/IC que por RMSE. (Plausible; requiere rediseñar evaluación y evitar interpretación como “predicción causal”.)

**V5 — Salidas con incertidumbre + calibración (mu/sigma o cuantiles).**  
Objetivo: mejorar decisiones de scoring bajo incertidumbre y evaluar con proper scoring rules (p.ej. cuantiles, CRPS/LogScore). Esto fortalece la tesis si tu framing incluye “risk‑aware outcomes”. citeturn5search1turn1file1

**V6 — Contexto macro/regímenes (features de régimen + interacciones con news).**  
Objetivo: permitir que el modelo “sepa” en qué entorno está (alta volatilidad, tightening, crisis), donde la semántica de news puede tener impacto distinto. (Plausible; riesgo: leakage si se usan revisiones macro o timestamps incorrectos.)

**V7 — Señales de opciones (implied volatility/skew/term structure).**  
Objetivo: añadir expectativas del mercado sobre cola/riesgo; en muchos activos líquidos, IV contiene información distinta al spot. (Alta promesa para horizontes cortos/medios; riesgo: disponibilidad histórica y costo/licencia; **incierto, verificar manualmente** en tu stack.)

**V8 — Company KB como prior/metadata branch (SEC‑timed profiles + aliases + relaciones).**  
Objetivo: mejorar (a) entity linking si incorporas news no “ticker‑tagged”, (b) cold‑start para nuevos tickers, (c) heterogeneidad cross‑sectional. SEC Submissions API contiene nombre actual, nombres anteriores, tickers y exchanges; el bulk ZIP facilita reproducibilidad. citeturn1search0turn1search1

### Bracket del torneo (cuartos → semis → final)
**Cuarto A: V1 vs V3**  
Gana **V1**. Razón: V3 (event‑state “más listo”) puede ser inútil si los labels están contaminados por discontinuidades mecánicas; V1 reduce un tipo de ruido que puede destruir tanto entrenamiento como evaluación. El costo adicional conceptual es bajo y la ganancia esperada en “accuracy real” es alta. fileciteturn1file1L110-L139

**Cuarto B: V2 vs V6**  
Gana **V2** (por poco). Razón: re‑definir targets hacia abnormal/factor‑neutral suele “limpiar” señal para un modelo que intenta capturar impacto informacional, y reduce riesgo de que el modelo solo aprenda beta/regímenes triviales. V6 puede ayudar, pero agrega riesgo de mala disciplina point‑in‑time en datos macro y puede desplazar el foco de tesis. (Plausible; requiere experimentación.)

**Cuarto C: V4 vs V5**  
Gana **V4** si el objetivo primario es “accuracy útil” para selección; gana **V5** si el foco de tesis es “riesgo/calibración”. Bajo tu criterio “accuracy is king”, el ranking suele ser más estable para el task cross‑sectional (sobre todo cuando los retornos son ruidosos). Sin embargo, V5 fortalece la “honestidad” bajo incertidumbre y reduce falsas conclusiones. Veredicto del torneo: **V4** avanza por potencial de mejora directa en utilidad predictiva. citeturn5search1turn1file1

**Cuarto D: V7 vs V8**  
Gana **V7** (alto potencial), con etiqueta: **“incierto, verificar manualmente”** para disponibilidad/costo. Razón: las opciones pueden aportar señal directa sobre incertidumbre/colas y sobre expectativas agregadas, que complementa news/spot. V8 es valioso, pero su beneficio marginal depende mucho de si ingieres news no ticker‑tagged y de si puedes construir perfiles “point‑in‑time” (difícil pero factible con SEC). citeturn1search0turn1search1

**Semifinal 1: V1 vs V2**  
Gana **V1**. Razón: V2 es muy atractivo científicamente, pero sigue dependiendo de precios ajustados correctos (y de un benchmark/factor model correcto). V1 es prerequisito transversal: sin V1, V2 puede construir residuals corruptos alrededor de corporate actions.

**Semifinal 2: V4 vs V7**  
Gana **V4** por robustez y menor superficie de dependencia de datos externos. V7 puede ser superior en “accuracy” si la cobertura de options es sólida; pero en una tesis de Maestría, la viabilidad y point‑in‑time correctness de opciones suele ser un gran riesgo operativo/licenciamiento.

**Final: V1 vs V4**  
Campeón del torneo: **V1 (corporate actions first‑class)**.  
Razón: V4 puede mejorar “utility accuracy”, pero si la base de labels está mecánicamente contaminada, cualquier mejora aparente puede ser ilusión o fragilidad. V1 es el multiplicador de credibilidad: reduce sesgo/ruido estructural y habilita comparaciones honestas entre market‑only vs multimodal.

### Resultados finales del torneo solicitados
- **Ganador del torneo (máxima prioridad por accuracy real y credibilidad):** V1.  
- **Runner‑up:** V4 (ranking objective).  
- **Mejor high‑risk / high‑reward:** V7 (opciones), condicionado a viabilidad de datos (**incierto, verificar manualmente**).  
- **Mejor low‑risk / high‑confidence:** V2 (targets abnormal/factor‑neutral) o V5 (incertidumbre + calibración), según el framing final de tesis.  
- **Mejor idea si la tesis debe ser estrecha:** V1 + V4 (data correctness + ranking).  
- **Mejor idea si la tesis puede expandirse moderadamente:** V1 + V4 + V5, manteniendo las demás como ablations.

## Unificación del pipeline, agenda priorizada y veredicto

### ¿Se puede unificar “lo mejor” en un solo pipeline?
**Conceptualmente sí**, pero con una condición: el diseño debe ser un **superset modular con branches ablatables**, no un “modelo monolítico” donde todo está siempre activo. Esto es coherente con el espíritu del repositorio (evaluación/ablaciones como parte central) y con la necesidad de evitar autoengaño. fileciteturn1file1L5-L20turn1file9L33-L40

**Ventajas de unificar (cuando se hace modular y ablatable):**
- Potencial de mayor accuracy por integración de señales complementarias (market + news + KB + macro + incertidumbre). citeturn4search5turn9view0  
- Mejor manejo de cold‑start y heterogeneidad cross‑sectional si KB se usa como prior y no como “oráculo”. citeturn1search0turn1search1  
- Storytelling más rico si se demuestra incrementalidad por ablation (y no solo “metí más datos”). citeturn7search8  

**Desventajas (y por qué pueden destruir una tesis):**
- **Scope explosion:** demasiadas fuentes y knobs → p‑hacking implícito y riesgo de PBO/backtest overfitting. citeturn7search8turn7search3  
- **Ablations menos limpias:** interacciones entre branches (macro×news, KB×news) hacen difícil atribuir mejoras y elevan ambigüedad.  
- **Mayor superficie de leakage:** cada nuevo join (macro releases, fundamentals filing dates, KB updates) es un nuevo vector de contaminación temporal. citeturn10search47turn1search0turn1search1  
- **Fragilidad:** un pipeline “todo‑en‑uno” puede verse bien en un período y fallar en otro por dependencia de una fuente.  
- **Narrativa de tesis se diluye:** si tu contribución central es “event‑state multimodal multi‑horizon”, añadir 6 modalidades más puede convertir la tesis en “ingeniería de dataset” sin hipótesis clara.

### Veredicto sobre unificación
**Recomendación fuerte (conservadora y defendible):**  
Mantén un **core pipeline estrecho** y científicamente limpio (market + news event‑state + multi‑horizon), y trata lo demás como **extensiones ablatables**. Esto maximiza probabilidad de una tesis sólida, reduce riesgo de sobreajuste por experimentación excesiva y mantiene claridad de contribución. fileciteturn1file1L33-L40turn1file9L33-L40

### Agenda priorizada (teoría‑only, sin instrucciones de código)
**Debe fortalecerse ya (bloqueantes científicos)**
1) **V1 Corporate actions correctness** como prerequisito (splits/dividendos/ajustes) y auditoría de discontinuidades. fileciteturn1file1L110-L139turn11search0turn11search38  
2) **Disciplina “as‑of close”** para news, con pruebas de timestamp y exchange calendar (objetivo: cero look‑ahead). citeturn10search47turn1file1turn1file11  
3) **Purging/embargo** explícito para horizontes solapados (si no está ya plenamente validado). citeturn10search7  

**Fuertemente recomendado después (alto valor, riesgo controlable)**
1) **V4 Ranking formulation** como objetivo primario o como evaluación principal complementaria.  
2) **V2 Abnormal/factor‑neutral labels** como alternativa principal a retornos crudos (sirve también como robustness check).  
3) **V5 Uncertainty + calibration** si tu tesis incluye “risk‑aware scoring” de forma central. citeturn5search1  

**Extensiones opcionales (solo si el core ya es sólido)**
1) **V8 Company KB** como prior y soporte de entity linking (especialmente si agregas news no ticker‑tagged). Debe ser point‑in‑time para evitar leakage. citeturn1search0turn1search1  
2) **V6 Macro/regime** con disciplina de publicación y sin revisiones futuras.  
3) **V7 Options** si consigues una fuente confiable con historial suficiente y licenciamiento viable (**incierto, verificar manualmente**).

**Issues no resueltos de mayor riesgo**
- El conflicto empírico entre “docs de Twelve Data sugieren ajuste por splits” y tu observación de que AAPL cercano a 2020‑08‑31 no aparece back‑adjusted: hasta resolverlo, cualquier conclusión sobre news→returns puede estar estructuralmente distorsionada. fileciteturn1file1L110-L139turn8search0  
- La ausencia de constituyentes históricos del índice (si el universo real es “latest snapshot”) puede introducir survivorship bias fuerte en horizontes largos. fileciteturn1file1L163-L190  

### Veredicto final “brutalmente honesto”
- **De qué se trata realmente este proyecto:** de demostrar (o refutar) que un **estado informacional agregado** derivado de news, correctamente alineado en tiempo y fusionado con señales de mercado, aporta señal incremental **multi‑horizonte** bajo evaluación fuera de muestra disciplinada. fileciteturn1file1L33-L40  
- **Fortaleza principal:** el framing es metodológicamente honesto (no causalidad de noticia individual), y el repositorio prioriza reproducibilidad/leakage safety por diseño. fileciteturn1file1L15-L20turn1file0L16-L36  
- **Debilidad conceptual número uno:** corporate actions (splits/dividendos) y point‑in‑time correctness aún parecen ser el factor que más puede invalidar resultados si no queda cerrado con pruebas duras. fileciteturn1file1L110-L139turn11search0turn11search38  
- **Dirección ganadora por accuracy (según torneo):** V1 (corporate actions correctness).  
- **Dirección ganadora por coherencia de tesis:** V1 + baseline multimodal event‑state (y, como extensión controlada, V4 ranking).  
- **¿Un pipeline unificado completo es sabio?:** posible, pero **peligroso** para Maestría si no se mantiene modular y ablatable; la estrategia más defendible es core estrecho + extensiones. citeturn7search8turn10search7  
- **Qué NO debe hacerse ahora:** expandir a múltiples nuevas modalidades (macro + options + KB + scraping masivo) antes de cerrar corporate actions + alineación temporal + evaluación purged/embargo; eso maximiza riesgo de “resultados bonitos” pero no defendibles. citeturn7search8turn10search47turn11search0