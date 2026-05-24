# Diseño e implementación rigurosa de un sistema multimodal multi‑horizonte para pronóstico EOD impulsado por estado de eventos

## Planteamiento de investigación y encuadre metodológico

**Definición del problema (en términos académicos).** Se busca aprender una función de predicción \(f_\theta\) que, para cada activo \(i\) y fecha de negociación \(t\), consuma: (a) un contexto de mercado EOD construido de OHLCV y derivados (\(\mathbf{x}_{i,t}\) y/o \(\mathbf{x}_{i,t-L:t}\)), (b) un conjunto de noticias con marcas de tiempo disponibles “as‑of” el cierre (\(\mathcal{N}_{i,\le t}\)), y (c) opcionalmente un perfil de empresa (conocimiento “lento” o estático) \(\mathbf{p}_{i,t}\). El objetivo es predecir **outcomes multi‑horizonte** \(y^{(\Delta)}_{i,t}\) para \(\Delta\in\{1,5,20,(60)\}\) días, donde \(y\) no se define como “precio futuro” sino como retornos/abnormal returns y/o probabilidades de eventos de downside y/o parámetros de una distribución de retorno. Este framing es consistente con la idea de mercados eficientes (es decir, precios incorporan información disponible y la predictibilidad sistemática es difícil) y con la práctica académica de formular resultados en términos de retornos, no niveles de precio. citeturn10search3turn10search10

**Qué se predice y qué no se predice.**  
- **No** se busca “predecir el precio” directamente (nivel de precio), porque introduce no‑estacionariedad y escalamiento, y además tiende a confundir evaluación. citeturn10search3  
- **Sí** se busca evaluar si una representación temporal de información (estado de eventos) agrega señal incremental para predecir **retornos a futuro, retornos ajustados (exceso o residual) y riesgos de cola** en múltiples horizontes, bajo evaluación estrictamente fuera de muestra. citeturn10search3turn10search0

**Por qué “estado de eventos” vs aislar impactos individuales.** La literatura de *event studies* muestra una metodología para estudiar impactos alrededor de eventos, pero también deja claro que el análisis se complica cuando hay múltiples eventos confusores y ventanas no limpias; en flujos continuos de noticias, la identificación causal de “una noticia = un efecto” suele ser metodológicamente frágil. Modelar un **estado agregado** es una forma más honesta: no afirma causalidad limpia, sino que representa un contexto informativo cambiante. citeturn10search2turn9search0

**Por qué multimodalidad está justificada.** El problema es multimodal por diseño: (i) series numéricas EOD y (ii) texto no estructurado, además de (iii) metadatos corporativos opcionales. Los desafíos clásicos de multimodalidad incluyen representación, alineación temporal, fusión y co‑aprendizaje; tu sistema cae exactamente en esa taxonomía (alineación asíncrona y fusión bajo ruido). citeturn9search3turn9search7

**Por qué multi‑horizonte es central.** Multi‑horizonte no es “predecir más lejos”, es **predecir distintos objetivos** (corto/medio/largo) que pueden tener drivers distintos. Arquitecturas y diseños de pérdida multi‑horizonte (p. ej., predicción explícita por horizonte con cabezas separadas) están bien establecidos en forecasting moderno; el punto clave es que la evaluación debe ser por horizonte y con protocolos temporales estrictos. citeturn9search2turn1search1

---

## Fuentes de datos y qué debe aportar cada una

### Mercado EOD OHLCV con Twelve Data

**Qué campos da /time_series para EOD.** El endpoint `/time_series` entrega una serie temporal con Open/High/Low/Close y, para instrumentos aplicables, volumen. Esto encaja con tu necesidad: EOD daily bars y no necesitas intradía. citeturn0search0turn0search19turn3search21

**Límites y costos de API (relevantes para ingeniería).** En el plan Basic gratuito, la propia página de pricing indica **8 créditos API por minuto y 800 por día**; además, el sistema de créditos se reinicia por minuto y hay límite diario en Basic. citeturn13view2turn13view0  
- La doc de “Credits” explicita que `/time_series` consume peso 1 por símbolo por request, y que si excede créditos responde 429 y el cupo se restaura al inicio del siguiente minuto; el límite diario se reinicia a 800 a medianoche UTC. citeturn13view0turn13view2  
- La doc de “Getting historical data” establece que **máximo 5,000 puntos** por request y recomienda `start_date/end_date` para rangos específicos. citeturn13view1

**Implicación directa para tu pipeline.** Con 503 tickers, un “full refresh” diario NO es viable en Basic (503 requests ya te consume casi todo el límite diario). Por tanto, el diseño debe ser incremental: (a) cargar historia una sola vez, (b) después solo traer “últimos N días” o rango por fechas con `start_date/end_date`, y (c) mantener ledger + caching local. citeturn13view0turn13view1turn13view2

**Splits/dividendos: estado realista y punto crítico.**  
- Tu verificación local inspeccionando AAPL alrededor de 2020‑08‑31 sugiere que los precios guardados no quedaron back‑adjusted por split (es decir, hay discontinuidad corporativa).  
- Además, Twelve Data documenta endpoints explícitos de corporate actions: `/splits` (fecha y factor) y `/dividends`, pero están listados bajo **Grow/Venture** (no Basic). Esto hace probable que en plan Basic no tengas acceso a splits “gratis”, así que debes tratar el split‑handling como requisito abierto. citeturn4view0turn13view0  
- Hay evidencia externa de discrepancias prácticas sobre si series vienen ajustadas o no en ciertos casos; por eso, incluso si existe un parámetro “adjust”, no debes asumir comportamiento sin pruebas por ticker (y tu test local es exactamente el tipo de prueba correcta). citeturn3search20turn13view1  

**Verificación mínima recomendada (no asumir).** Para cualquier fuente, verifica split‑adjustment con un ticker con split conocido (AAPL 2020‑08‑31, TSLA 2020‑08‑31, NVDA 2021‑07‑20, etc.) comparando ventanas antes/después y buscando “saltos mecánicos” (retornos diarios extremadamente grandes). citeturn13view1

### Noticias por ticker con Finnhub

**Qué endpoint usar y qué campos esperar.** La API de “Company News” típicamente retorna items con campos como `category`, `datetime` (UNIX timestamp), `headline`, `summary`, `url`, `image`, `source`, `related` e `id` (usable como incremental cursor). Esto está documentado en SDKs oficiales/compatibles y es coherente con el endpoint `/company-news` (por símbolo y rangos de fechas). citeturn3search5turn0search2

**Limitaciones operativas y rate limiting.** Finnhub documenta que si excedes el límite recibes HTTP 429, y además existe un **límite superior de 30 llamadas por segundo** “por encima de los límites del plan”. El diseño del downloader debe incorporar backoff y reintentos, y un scheduler por minuto/segundo. citeturn6search1turn6search7

**Dedupe y chunking.** Para descargas históricas, el patrón estándar es chunk por rango (semanal o mensual) por símbolo y deduplicación por `url` (primario) y por hash de `(headline, datetime, source)` como fallback. Esto es especialmente importante porque feeds de noticias suelen re‑publicar y sindicar. (Esto no lo asumas: debes medir duplicados y documentar la tasa). citeturn3search5

**Alineación temporal EOD sin leakage.** Aquí la regla es “as‑of close”: para features del día \(t\), solo noticias publicadas antes del cierre del mercado correspondiente a ese ticker/bolsa. Cualquier noticia “after hours” debe entrar a \(t+1\) (siguiente día hábil). Este punto es un foco clásico de leakage en proyectos de news‑to‑market. citeturn12search9turn2view1

### Conocimiento corporativo con EDGAR de la SEC

**Acceso, límites y ética de scraping.** entity["organization","U.S. Securities and Exchange Commission","us regulator"] documenta acceso gratuito a datos EDGAR y especifica “fair access”: **máximo 10 requests/segundo**, declarar `User-Agent` en headers, y evitar crawling abusivo. citeturn2view1turn0search3turn0search31

**Endpoints que realmente importan para tu KB.** La página oficial de “EDGAR Application Programming Interfaces” indica que `data.sec.gov` aloja APIs REST JSON sin API keys, y detalla:  
- **Submissions history** por entidad: `data.sec.gov/submissions/CIK##########.json` (CIK 10 dígitos).  
- Esa estructura incluye metadatos como **nombre actual, nombres anteriores, exchanges y tickers** de compañías públicas, y su historial de filings recientes; además hay un ZIP “bulk” actualizado nightly (~3:00am ET). citeturn2view0

**XBRL APIs para fundamentals (opcional).** Para un proyecto centrado en evento‑estado de noticias, XBRL no es obligatorio, pero la SEC expone `companyfacts`, `companyconcept` y `frames` para hechos agregados, comparables entre compañías y tiempo (con taxonomías estándar). Esto puede servir para: (i) targets de “fundamental drift”, (ii) features lentas, o (iii) validación auxiliar, siempre respetando timestamps de publicación del filing. citeturn2view0

**Qué aporta un “Company KB” en tu caso (juicio honesto).**  
- **Si las noticias ya vienen por ticker** (tu caso con Finnhub company‑news), el KB ayuda más como **priors estáticos** o para cold‑start, que para entity linking.  
- **Si en el futuro ingieres noticias no taggeadas** (RSS general, scraped, etc.), el KB sí puede ser crucial para entity linking robusto e interpretabilidad. (Recomendación plausible; debe testearse). citeturn2view0turn9search3

### Wikipedia/Wikidata y licenciamiento

**Riesgo de leakage temporal.** Wikipedia cambia con el tiempo; usar descripciones actuales para representar una empresa en 2008 introduce “future knowledge leakage” (no necesariamente de precio, pero sí de información no disponible en ese momento). Si se usa, debe ser time‑stamped (ej. revision history) o claramente documentado como limitación. citeturn12search9turn11search3

**Licencia y atribución.** Contenido de Wikipedia suele estar bajo CC BY‑SA (p. ej. CC BY‑SA 4.0) que exige atribución y share‑alike. Si vas a almacenar/desplegar texto derivado, debes planear atribución y compatibilidad de licencia (y evitar redistribuir texto entero innecesariamente). citeturn11search11turn11search3

---

## Arquitectura de datos reproducible y pipeline de ingeniería

**Principio rector (hallazgo establecido en ingeniería de datos).** Para investigación reproducible necesitas: dumps crudos inmutables, datasets “interim” derivados determinísticamente, y datasets “final” versionados para entrenamiento/evaluación. Esto reduce debugging y evita “silent drift” del dataset. (Recomendación plausible respaldada por buenas prácticas; la implementación concreta depende de tu repo). citeturn2view0turn13view0

**Formato de almacenamiento recomendado: Parquet + Arrow.**  
- entity["organization","Apache Parquet","columnar file format"] es un formato columnar diseñado para almacenamiento/lectura eficiente (solo leer columnas necesarias, compresión/encoding). citeturn14search4turn14search18  
- entity["organization","Apache Arrow","in-memory columnar format"] define un formato columnar en memoria y ecosistema para intercambio/analítica eficiente, base natural para pipelines Python (pyarrow) y para interoperabilidad. citeturn14search1turn14search16  
Esto es especialmente apropiado para un panel stock×día×features donde la lectura selectiva por columnas y compresión importan. citeturn14search4turn14search3

**Herramientas de transformación: pandas vs Polars vs DuckDB.**  
- pandas es excelente para prototipos y datasets medianos; para joins/aggregations grandes, entity["organization","Polars","dataframe library"] y entity["organization","DuckDB","in-process analytics db"] pueden dar mejoras por lazy execution y pushdown sobre Parquet. citeturn14search14turn14search3turn14search7  
- DuckDB documenta lectura eficiente de Parquet con “filter/projection pushdown” y ejecución paralela; útil para construir features/labels sin cargar todo en RAM. citeturn14search3turn14search7  
- Polars permite scan “lazy” de Parquet y puede operar en modo streaming para resultados > RAM; muy relevante si escalas embeddings/event states a panel completo. citeturn14search14turn14search6

**Esquemas canónicos recomendados (debes fijarlos temprano).**  
- `prices_daily.parquet` (o particionado por ticker): `date, ticker, open, high, low, close, volume, source, ingest_ts` (y eventualmente `adj_*` si ajustas). citeturn0search0turn14search4  
- `news.parquet`: `article_id, ticker, published_ts_utc, headline, summary, source, url, image, related, provider_id`. citeturn3search5  
- `company_kb.parquet` (SEC): `ticker, cik, name_current, former_names[], exchanges[], sic, addresses, effective_date, source`. La SEC confirma que submissions JSON incluye nombre actual, nombres anteriores, exchanges y tickers. citeturn2view0turn2view1  
- `splits.parquet`: `ticker, split_date, split_factor` (new/old). Si obtienes desde Twelve Data `/splits` o alterno, guárdalo normalizado. citeturn4view0turn17search0  
- `embeddings.parquet`: `article_id, model_id, embed_dim, embedding (vector), embed_ts, text_hash`. (Recomendación plausible; el detalle depende de tu stack). citeturn16search16turn14search1  
- `event_state.parquet`: `ticker, date, state_vec, news_count, novelty, conflict, density...` (y metadatos de ventana). (Recomendación plausible; se valida por ablation). citeturn9search3turn9search0  
- `labels.parquet`: `ticker, date, y_ret_1, y_ret_5, y_ret_20, y_ret_60, y_downside_*` etc. (Recomendación plausible; evaluación requiere CV temporal). citeturn1search1turn12search9

**Diseño de descargas eficiente para Twelve Data.**  
- Registra en ledger por ticker: status, n_rows, headers `api-credits-used` y `api-credits-left` (la doc indica que esos headers existen). citeturn13view0turn13view2  
- Usa `start_date/end_date` para actualizaciones incrementales y respeta el máximo de 5000 puntos por request. citeturn13view1turn13view0

**Diseño de descargas eficiente para SEC.**  
- Respeta 10 req/s y declara User‑Agent. citeturn2view1turn0search31  
- Usa el bulk ZIP nightly (cuando te convenga) para reproducibilidad y para evitar millones de requests. citeturn2view0

---

## Splits y acciones corporativas como amenaza principal a validez

### Por qué importa para labels multi‑horizonte y evaluación

**Hallazgo establecido (práctica financiera).** Stock splits generan discontinuidades mecánicas en precios y saltos inversos en volumen. Si no ajustas, un split puede aparecer como un retorno extremo “falso” y contaminar labels a 1/5/20/60 días, métricas de error y cualquier backtest de ranking. Esto es especialmente crítico si tu sistema aprende patrones de “eventos” coincidentes con fechas corporativas. (La existencia de métodos estándar de split‑adjustment está documentada en herramientas estadísticas y en la práctica). citeturn3search11turn12search9

### Estrategias viables (ordenadas por robustez)

**Opción robusta (recomendada): obtener splits explícitos y back‑adjust.**  
- Twelve Data documenta `/splits` “date and split factor” pero bajo Grow/Venture (es decir, probablemente no disponible en Basic). Si migras a un plan con acceso, esta es la ruta más limpia dentro del mismo proveedor. citeturn4view0turn13view0  
- Alternativa: usar un proveedor separado **solo** para splits (p. ej., entity["company","Financial Modeling Prep","financial data api provider"] documenta un endpoint “splits?symbol=…” para historial de splits). Esto minimiza el impacto en tu pipeline: mantienes OHLCV de Twelve Data y solo traes corporate actions de un endpoint barato. citeturn17search0

**Opción “data source swap” (válida si quieres simplificar): usar precios ya ajustados.** Algunos proveedores ofrecen series EOD ajustadas por dividendos y/o splits; por ejemplo, FMP describe APIs con precios ajustados por dividendos y menciona mantener OHLCV ajustados para análisis más “total return”. Aun así, debes verificar si está ajustado por splits, dividendos o ambos, y si OHLC completos son ajustados o solo “adjusted close”. citeturn3search13turn17search1

**Opción mitigación temporal (solo si no hay corporate actions): excluir ventanas de splits.** Si no puedes obtener splits pronto, una mitigación para investigación (no ideal) es filtrar observaciones alrededor de retornos absurdamente grandes y auditar si coinciden con splits. Esto reduce contaminación pero introduce sesgo de selección y no resuelve el problema para todos los casos; úsalo como “stop‑gap” y documenta fuerte. citeturn12search9turn3search11

### Matemática exacta de back‑adjustment (split‑only)

Sea un split en fecha \(d\) con factor \(s=\frac{\text{new shares}}{\text{old shares}}\). Para hacer la serie continua en el pasado (“back‑adjust”):

- Para toda fecha \(t < d\):  
  - `open/high/low/close` \(\leftarrow\) dividir por \(s\)  
  - `volume` \(\leftarrow\) multiplicar por \(s\)

Con múltiples splits, usa el **producto acumulado de splits futuros** aplicado a cada fecha \(t\). (Este es el esquema estándar en herramientas de ajuste de series). citeturn3search11turn17search0

### Cómo verificar que el ajuste funcionó

Diseña pruebas automáticas (“unit tests” de datos):

- **Test de discontinuidad**: calcula \(|r_{t,1}|\) y marca outliers; tras ajustar, los spikes mecánicos de split deberían desaparecer. citeturn12search9turn3search11  
- **Test de fecha conocida**: selecciona splits conocidos por ticker (desde tabla de splits) y verifica que no haya salto de ~‑75% o similar en el día del split. citeturn17search0turn3search11  
- **Test de volumen**: volumen pre‑split debe escalar, y la liquidez no debe volverse absurda por error de signo. citeturn3search11

---

## Arquitectura de modelo, entrenamiento en GPU y eficiencia computacional

### Plan de modelado por etapas (para Máster y para evitar autoengaño)

**Etapa base: baselines market‑only fuertes.** Primero, modelos simples (ridge/elastic net, MLP pequeño) con features de mercado; en finanzas, estos suelen ser duros de batir y sirven para detectar leakage. La evaluación debe ser con split temporal (TimeSeriesSplit/walk‑forward) porque CV estándar entrena en futuro y evalúa en pasado. citeturn1search1turn1search9turn12search9

**Etapa principal: market + event state.** El estado de eventos se construye agregando embeddings de noticias con decaimiento temporal. La motivación se alinea con trabajos de predicción event‑driven (extracción y representación de eventos + modelado de influencias temporales), aunque tu enfoque explícitamente evita afirmar que cada noticia tenga efecto aislable. citeturn9search0turn9search16

**Etapa extendida: market + event state + company profile.** La encuesta de multimodalidad enfatiza “alineación/fusión/co‑learning”; el perfil corporativo puede actuar como covariable estática (similar a “static covariates” en modelos multi‑horizonte) y mejorar cold‑start o generalización cross‑sector. citeturn9search3turn9search2turn2view0

### Representaciones de texto: sentimiento vs embeddings densos

**Hallazgo establecido (NLP financiero).** Modelos tipo FinBERT muestran que la adaptación de LM preentrenados al dominio financiero mejora tareas de sentimiento frente a métodos generales, apoyando el uso de embeddings contextualizados como representación base del “contenido” noticioso. citeturn9search1turn9search5

**Recomendación plausible.** Para tu tesis, la estrategia más estable es:  
1) congelar un encoder textual (no fine‑tuning end‑to‑end al inicio),  
2) precomputar embeddings de headlines (y opcional summary),  
3) construir estados agregados por ticker‑día offline,  
4) entrenar el modelo multimodal sobre esos vectors.  
Esto reduce varianza de entrenamiento, evita costos enormes, y hace ablations limpias. citeturn16search16turn15search1turn9search3

### Diseño multi‑horizonte y cabezas múltiples

**Hallazgo establecido en forecasting multi‑paso.** TFT formaliza el enfoque de predicción multi‑horizonte con componentes para covariables estáticas y dinámicas, y sugiere que separar horizontes (outputs por horizonte) es natural. Tú no necesitas copiar TFT; sí necesitas su principio: misma representación con heads por horizonte, y evaluación por horizonte. citeturn9search2turn9search6

**Diseño concreto recomendado (realista).**  
- Encoder mercado: MLP o TCN/GRU pequeño sobre ventana \(L\) de features.  
- Encoder estado‑evento: MLP sobre vector agregado + scalars (news_count, novelty…).  
- Fusión: concatenación + gating (para apagar noticias cuando hay pocas/ruidosas).  
- Outputs: heads por horizonte para:
  - \(\hat{\mu}_{\Delta}\) (retorno esperado)  
  - opcional \(\hat{\sigma}_{\Delta}\) (escala de riesgo) o cuantiles  
  - opcional \(p_\Delta(\text{downside})\)  
(Esto es recomendación plausible; se valida por ablations). citeturn10search0turn9search2turn9search3

### GPU/CUDA: dónde importa de verdad y cómo hacerlo eficiente

**Instalación y compatibilidad CUDA.** La guía oficial de instalación de entity["organization","PyTorch","deep learning framework"] recomienda seleccionar Linux + pip/conda + versión CUDA adecuada; eso fija “torch con CUDA”. citeturn1search0turn1search4

**Dónde GPU SÍ es crítica.**  
- Precomputar embeddings con Transformers sobre millones de tokens.  
- Entrenar modelos profundos (aunque tu arquitectura principal podría ser mediana).  
En cambio, joins/ETL de Parquet suelen ser CPU‑bound (o DuckDB/Polars) y no ganan mucho en GPU. (Recomendación plausible basada en arquitectura). citeturn14search3turn16search0turn16search21

**Mixed precision (alto impacto, bajo riesgo si se hace bien).** PyTorch documenta AMP (`torch.amp`) para ejecutar partes en FP16/BF16, acelerar y reducir memoria; y Hugging Face también recomienda mixed precision para throughput. citeturn15search0turn16search21turn16search1

**Tokenización y throughput.** Hugging Face documenta “fast tokenizers” (Tokenizers en Rust) que son significativamente más rápidos en tokenización batched; esto importa mucho en el precompute de embeddings. citeturn16search16turn16search0

**DataLoader y transferencia CPU→GPU.** PyTorch tiene guías sobre `pin_memory()` y `non_blocking=True` para acelerar transferencias; NVIDIA también discute tradeoffs de pinned/mapped memory en GPUs discretas. Esto se aplica sobre todo a entrenamiento, no tanto a ETL. citeturn15search6turn15search3turn15search2

**Escalado multi‑GPU (solo si lo necesitas).** Para un Máster, normalmente basta 1 GPU. Si entrenas modelos grandes o haces fine‑tuning de LM, `DistributedDataParallel` sincroniza gradientes entre replicas y requiere que tú “shardees” el input (p. ej. con `DistributedSampler`). Hugging Face Accelerate simplifica ejecutar el mismo código en setups distribuidos. citeturn16search2turn15search1turn15search5

**Optimización adicional:** `torch.compile` puede acelerar entrenamiento al compilar el grafo a kernels optimizados con cambios mínimos de código (pero debes perfilar porque no siempre ayuda). citeturn16search7turn16search3

---

## Validación, evaluación, errores comunes y roadmap reproducible

### Validación temporal y prevención de leakage

**Hallazgo establecido:** CV estándar falla en data temporal; scikit‑learn recomienda esquemas “time‑series aware” y `TimeSeriesSplit` para no entrenar con futuro y evaluar en pasado. citeturn1search1turn1search9

**Recomendación fuerte (finanzas): purging + embargo cuando hay labels forward‑looking.** Cuando etiquetas dependen de ventanas futuras (multi‑horizonte), existe contaminación por solapamiento; en finanzas se recomienda purgar observaciones cuyo horizonte de label se superpone con test, y aplicar embargo posterior. Esto es central en entity["book","Advances in Financial Machine Learning","lopez de prado 2018"]. citeturn1search20turn12search10turn12search2

**Backtest overfitting como riesgo estructural.** Un hallazgo clave: con muchos grados de libertad (muchas variantes de features/modelos), es fácil seleccionar un “ganador” espurio. El framework de “Probability of Backtest Overfitting (PBO)” formaliza este riesgo y por qué hold‑out simple puede ser insuficiente en backtests. citeturn1search3turn1search15

### Métricas recomendadas (alineadas a tu hipótesis)

**Regresión:** MAE/RMSE por horizonte + correlación (Pearson/Spearman) entre predicción y retorno realizado. Comparaciones de modelos pueden apoyarse en tests de precisión predictiva (Diebold–Mariano) sobre diferenciales de pérdida. citeturn10search12turn10search1

**Dirección y downside:** AUC/PR‑AUC y Brier si produces probabilidades (más relevante si el foco es “riesgo”). La evaluación probabilística debe usar *proper scoring rules*; Gneiting & Raftery proveen base teórica de scoring rules “strictly proper”. citeturn10search0turn16search1

**Ranking / decisión:** IC (Spearman cross‑sectional por día) y estabilidad temporal (ICIR). (Recomendación plausible, requiere definición exacta y reporte de distribución, no solo media). citeturn1search3turn12search9

### Errores comunes (prioridad alta → media) y cómo evitarlos

1) **Look‑ahead bias (la forma más destructiva).** Ocurre cuando usas información no disponible en \(t\) para construir features/labels en \(t\). Ejemplos documentados: usar datos fundamentales sin considerar fecha de publicación o usar estadísticas globales del dataset. Prevención: “as‑of joins”, splits estrictos, tests de leakage, y normalización fit‑solo‑train. citeturn12search1turn12search9  
2) **Solapamiento de labels multi‑horizonte (contaminación por construcción).** Si tienes \(y_{t,20}\), muestras cercanas comparten parte del futuro; necesitas purging/embargo o, como mínimo, gaps temporales. citeturn1search20turn12search2  
3) **Survivorship bias por universo “S&P 500 latest”.** Si entrenas 2006–2026 con el universo actual, excluyes empresas que salieron (quiebra, M&A) y sesgas resultados. Si no tienes constituyentes históricos, documenta limitación o integra una fuente histórica (muchas son pagas). La propia literatura/industria discute que backtests con universos de índices tienden a tener survivorship bias. citeturn12search12turn12search8  
4) **Manejo incorrecto de splits/dividendos.** Contamina retornos y targets; tu check local ya detectó este riesgo. Prevención: corporate actions explícitas + back‑adjust y pruebas de discontinuidad. citeturn3search11turn17search0turn4view0  
5) **Errores de timezone y “market close”.** Noticias after‑hours mal asignadas causa leakage o degradación. Prevención: calendarios de trading y reglas “as‑of close”; tests de timestamp. citeturn2view1turn12search9  
6) **Dedupe deficiente de news.** Sindicación replica artículos; sin dedupe el modelo aprende “peso por duplicación” y no señal. Prevención: dedupe por URL/ID y auditoría de duplicados. citeturn3search5  
7) **Hostilidad de evaluación por “data snooping”.** Demasiadas variantes y reportar solo la mejor. Prevención: pre‑registrar ablations, usar un set test único final, y reportar distribución de folds walk‑forward. citeturn1search3turn1search15turn12search6  
8) **Confundir mejora estadística con valor real.** Un delta pequeño puede ser ruido; usa CIs y pruebas de comparación (p. ej. DM) y evita conclusiones fuertes. citeturn10search12turn1search3  
9) **Normalización global (train+test).** Error común: z‑score sobre todo el dataset. Prevención: fit solo train, aplicar a val/test. citeturn12search9turn1search9  
10) **Metadatos corporativos con leakage temporal (Wikipedia/10‑K “futuro”).** Prevención: perfiles time‑indexed (solo info disponible hasta \(t\)), o declarar explícitamente la limitación si usas snapshot actual. citeturn11search11turn12search9  

### Roadmap recomendado (enfocado en “máxima probabilidad de éxito”)

**Fase de datos (bloqueante):**  
- Congelar OHLCV con pipeline incremental (ya tienes historia). citeturn13view1turn13view2  
- Resolver splits: preferible con `/splits` (si upgrade) o con un proveedor alterno de splits (FMP `splits?symbol=`). citeturn4view0turn17search0  
- Construir panel final en Parquet y cobertura; usar DuckDB/Polars si escala. citeturn14search3turn14search14  

**Fase de news y estado de eventos:**  
- Descarga Finnhub company news por ticker por rangos; dedupe. citeturn3search5turn6search1  
- Alineación EOD estricta (as‑of close). citeturn2view1turn12search9  
- Precompute embeddings (GPU) con fast tokenizers y mixed precision cuando aplique; cache. citeturn16search16turn15search0turn16search21  

**Fase de modelado y evaluación:**  
- Baselines market‑only + walk‑forward. citeturn1search1turn1search9  
- Multimodal principal (market+event state), luego KB (SEC). citeturn2view0turn9search0turn9search3  
- Evaluación robusta y control de overfitting/backtest selection. citeturn1search3turn1search20turn10search12  

---

**Resumen honesto de puntos aún “no resueltos” (a verificar manualmente).**  
- Acceso real a endpoints de splits/dividends en tu plan de Twelve Data (la documentación sugiere que `/splits` es Grow/Venture). Verificar con una llamada real y revisar respuesta/errores. citeturn4view0turn13view0  
- Límites exactos de tasa del plan gratuito de Finnhub (la doc indica 429 y un ceiling de 30 calls/s, pero el límite por plan puede variar; validar por headers/experimento controlado). citeturn6search1turn6search7  
- Si decides incorporar Wikipedia/Wikidata: el plan de compliance de licencia y el plan de “time‑stamping” para evitar leakage, porque CC BY‑SA requiere atribución y share‑alike. citeturn11search11turn11search3