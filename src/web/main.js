document.addEventListener('DOMContentLoaded', () => {
    // Translation Dictionary
    const TRANSLATIONS = {
        en: {
            logo_title: "PySearchNLP",
            subtitle: "Information Retrieval & NLP Processing Engine from Scratch",
            tab_search: "Search Portal",
            tab_analytics: "Corpus Analytics",
            tab_inspector: "Index Inspector",
            tab_performance: "Engine Performance",
            search_placeholder: "Enter your natural language query (e.g., 'articles de la rubrique Focus parlant d'innovation')...",
            sort_relevance: "Sort by Relevance",
            sort_newest: "Newest First",
            sort_oldest: "Oldest First",
            search_btn: "Search",
            try_queries: "Try these queries:",
            nlp_title: "NLP Pipeline Stepper",
            step1_title: "Tokenization & Noise Filtering",
            step1_desc: "No keywords processed yet.",
            step2_title: "Spelling Correction & Stemming",
            step2_desc: "Awaiting query input...",
            step3_title: "Structural Metadata Constraints",
            step3_desc: "No constraints detected.",
            step4_title: "Parsed Boolean Logic",
            step4_desc: "Awaiting evaluation...",
            btn_show_json: "Show Structured Query JSON",
            btn_hide_json: "Hide Query JSON",
            btn_show_logs: "Show Engine Log Streams",
            btn_hide_logs: "Hide Engine Logs",
            json_header: "Structured Query Representation",
            logs_header: "Real-Time Execution Logs",
            stat_total_docs: "Total Documents Indexed",
            stat_vocab_size: "Vocabulary Size (Stems)",
            stat_image_ratio: "Articles with Images",
            chart_rubrics: "Document Rubric Distribution",
            chart_stems: "Top High-Weight Vocabulary Stems (TF-IDF)",
            inspect_title: "Inverted Index Lookup Tool",
            inspect_desc: "Query the underlying binary or hash-map index structures directly. Type a stemmed keyword or metadata term to inspect its occurrences and posting lists across the corpus.",
            lbl_term: "Term / Word",
            lbl_field: "Index Field",
            btn_inspect: "Query Inverted Index",
            opt_text: "Content (text)",
            opt_title: "Title (title)",
            opt_rubric: "Category (rubric)",
            opt_author: "Author (author)",
            opt_date: "Publish Date (date)",
            opt_images: "Image metadata (images)",
            inspect_matches: "matches found in the",
            inspect_index: "index.",
            inspect_postings_title: "Posting List Representation (Document ID & Term Freq)",
            perf_title: "Engine Performance Benchmarks",
            perf_desc: "Measure the search retrieval latency, precision, and recall of the NLP search engine. Compare pre-computed validation statistics with live real-time latency tests.",
            btn_live_benchmark: "⚡ Run Live Benchmark",
            btn_running_benchmark: "⏱️ Running Live Benchmark...",
            lbl_pre_latency: "Pre-computed Latency",
            lbl_live_latency: "Live Test Latency",
            lbl_accuracy: "System Accuracy",
            perf_table_title: "Query Performance & Validation Test Suite",
            th_id: "ID",
            th_query: "Validation Query Text",
            th_docs: "Docs Returned",
            th_precision: "Precision",
            th_recall: "Recall",
            th_pre_speed: "Pre-computed Speed",
            th_live_speed: "Live Speed (10 runs avg)",
            loading_metrics: "Loading performance metrics...",
            awaiting_test: "Awaiting test...",
            measuring: "Measuring...",
            running: "Running...",
            failed: "Failed",
            error: "Error",
            
            // Dynamic/JS Strings
            analyzing_query: "Analyzing query grammar and executing retrieval...",
            err_execution: "Error executing request: ",
            no_logs: "No execution logs available.",
            matched_msg: "article matched",
            matched_msg_plural: "articles matched",
            no_results_found: "No matching documents found. Check your filters or spelling suggestions.",
            no_tokens: "No tokenized keywords found (metadata-only query).",
            no_stems: "No stems generated.",
            no_meta_filters: "No structural metadata filters active.",
            empty_eq: "Empty equation (metadata filter matches all)",
            loading_rubrics: "Loading rubric insights...",
            no_rubrics: "No rubric categories indexed.",
            loading_vocab: "Loading vocabulary weights...",
            no_vocab: "Vocabulary indices empty.",
            scanning_indexes: "Scanning indexes...",
            no_postings_found: "No postings entries found for term",
            db_notice: "Note: Since the database is 100% in French, search results will be returned in French.",
            init_starting: "Starting search engine pipeline...",
            init_phase1: "Phase 1: Generating XML Corpus from source bulletins...",
            init_phase2: "Phase 2: Tokenizing and filtering stopwords...",
            init_phase3: "Phase 3: Stemming & computing TF-IDF indexes...",
            init_phase4: "Phase 4: Loading search components and dictionary...",
            init_phase5: "Phase 5: Automatically executing evaluation benchmark tests...",
            init_err_connect: "Connecting to search backend..."
        },
        pt: {
            logo_title: "PySearchNLP",
            subtitle: "Motor de Busca e Processamento de PLN do Zero",
            tab_search: "Portal de Busca",
            tab_analytics: "Estatísticas do Corpus",
            tab_inspector: "Inspetor de Índices",
            tab_performance: "Performance da Engine",
            search_placeholder: "Digite sua busca em linguagem natural (ex: 'articles de la rubrique Focus parlant d'innovation')...",
            sort_relevance: "Ordenar por Relevância",
            sort_newest: "Mais Recentes Primeiro",
            sort_oldest: "Mais Antigos Primeiro",
            search_btn: "Buscar",
            try_queries: "Tente estas buscas:",
            nlp_title: "Passos do Pipeline de PLN",
            step1_title: "Tokenização e Filtragem de Ruído",
            step1_desc: "Nenhuma palavra-chave processada ainda.",
            step2_title: "Correção Ortográfica e Stemização",
            step2_desc: "Aguardando entrada de busca...",
            step3_title: "Restrições Estruturais de Metadados",
            step3_desc: "Nenhuma restrição detectada.",
            step4_title: "Lógica Booleana Processada",
            step4_desc: "Aguardando avaliação...",
            btn_show_json: "Mostrar JSON Estruturado",
            btn_hide_json: "Ocultar JSON da Busca",
            btn_show_logs: "Mostrar Logs de Execução",
            btn_hide_logs: "Ocultar Logs da Engine",
            json_header: "Representação Estruturada da Busca",
            logs_header: "Logs de Execução em Tempo Real",
            stat_total_docs: "Total de Documentos Indexados",
            stat_vocab_size: "Tamanho do Vocabulário (Stems)",
            stat_image_ratio: "Artigos com Imagens",
            chart_rubrics: "Distribuição de Rubricas dos Documentos",
            chart_stems: "Palavras de Maior Peso no Vocabulário (TF-IDF)",
            inspect_title: "Ferramenta de Consulta ao Índice Invertido",
            inspect_desc: "Consulte as estruturas de índice invertido ou hash-map diretamente. Digite um termo stemizado ou metadado para inspecionar suas ocorrências no corpus.",
            lbl_term: "Termo / Palavra",
            lbl_field: "Campo de Índice",
            btn_inspect: "Consultar Índice Invertido",
            opt_text: "Conteúdo (text)",
            opt_title: "Título (title)",
            opt_rubric: "Categoria (rubric)",
            opt_author: "Autor (author)",
            opt_date: "Data de Publicação (date)",
            opt_images: "Metadados de Imagem (images)",
            inspect_matches: "ocorrências encontradas no índice",
            inspect_index: ".",
            inspect_postings_title: "Lista de Postings (ID do Documento e Frequência)",
            perf_title: "Benchmarks de Performance",
            perf_desc: "Meça a latência de busca, precisão e recall do motor de busca de PLN. Compare as estatísticas de validação pré-computadas com testes de latência ao vivo.",
            btn_live_benchmark: "⚡ Rodar Benchmark ao Vivo",
            btn_running_benchmark: "⏱️ Executando Benchmark...",
            lbl_pre_latency: "Latência Pré-computada",
            lbl_live_latency: "Latência ao Vivo",
            lbl_accuracy: "Precisão do Sistema",
            perf_table_title: "Suite de Testes de Validação e Performance",
            th_id: "ID",
            th_query: "Texto da Busca de Validação",
            th_docs: "Docs Retornados",
            th_precision: "Precisão",
            th_recall: "Recall",
            th_pre_speed: "Velocidade Pré-computada",
            th_live_speed: "Velocidade ao Vivo (média de 10 execuções)",
            loading_metrics: "Carregando métricas de performance...",
            awaiting_test: "Aguardando teste...",
            measuring: "Medindo...",
            running: "Executando...",
            failed: "Falhou",
            error: "Erro",
            
            // Dynamic/JS Strings
            analyzing_query: "Analisando gramática da busca e executando recuperação...",
            err_execution: "Erro ao executar requisição: ",
            no_logs: "Nenhum log de execução disponível.",
            matched_msg: "artigo correspondente",
            matched_msg_plural: "artigos correspondentes",
            no_results_found: "Nenhum documento correspondente encontrado. Verifique os filtros ou correções sugeridas.",
            no_tokens: "Nenhuma palavra-chave identificada (busca apenas de metadados).",
            no_stems: "Nenhum radical gerado.",
            no_meta_filters: "Nenhum filtro estrutural ativo.",
            empty_eq: "Equação vazia (filtros de metadados correspondem a tudo)",
            loading_rubrics: "Carregando estatísticas de rubricas...",
            no_rubrics: "Nenhuma categoria de rubrica indexada.",
            loading_vocab: "Carregando pesos do vocabulário...",
            no_vocab: "Índice de vocabulário vazio.",
            scanning_indexes: "Escaneando índices...",
            no_postings_found: "Nenhum posting encontrado para o termo",
            err_connect: "Falha ao conectar com o serviço de busca do backend.",
            db_notice: "Nota: Como a base de dados está 100% em francês, os resultados da busca também serão retornados em francês.",
            init_starting: "Iniciando o pipeline do motor de busca...",
            init_phase1: "Fase 1: Gerando corpus XML a partir dos boletins...",
            init_phase2: "Fase 2: Tokenizando e filtrando stopwords...",
            init_phase3: "Fase 3: Stemização e computação dos índices TF-IDF...",
            init_phase4: "Fase 4: Carregando componentes de busca e dicionário...",
            init_phase5: "Fase 5: Executando automaticamente os testes de benchmark...",
            init_err_connect: "Conectando ao serviço de busca..."
        },
        fr: {
            logo_title: "PySearchNLP",
            subtitle: "Moteur de Recherche & Pipeline NLP à partir de zéro",
            tab_search: "Portail de Recherche",
            tab_analytics: "Statistiques du Corpus",
            tab_inspector: "Inspecteur d'Index",
            tab_performance: "Performance du Moteur",
            search_placeholder: "Entrez votre requête en langage naturel (ex: 'articles de la rubrique Focus parlant d'innovation')...",
            sort_relevance: "Trier par pertinence",
            sort_newest: "Plus récents en premier",
            sort_oldest: "Plus anciens en premier",
            search_btn: "Rechercher",
            try_queries: "Essayer ces requêtes :",
            nlp_title: "Pipeline NLP Étape par Étape",
            step1_title: "Tokenisation & Filtrage du Bruit",
            step1_desc: "Aucun mot-clé traité pour l'instant.",
            step2_title: "Correction Orthographique & Racinisation (Stemming)",
            step2_desc: "En attente d'une requête...",
            step3_title: "Contraintes structurelles (Métadonnées)",
            step3_desc: "Aucune contrainte détectée.",
            step4_title: "Logique Booléenne Résolue",
            step4_desc: "En attente d'évaluation...",
            btn_show_json: "Afficher le JSON structuré",
            btn_hide_json: "Masquer le JSON",
            btn_show_logs: "Afficher les flux de logs",
            btn_hide_logs: "Masquer les logs",
            json_header: "Représentation structurée de la requête",
            logs_header: "Logs d'exécution en temps réel",
            stat_total_docs: "Total des documents indexés",
            stat_vocab_size: "Taille du vocabulaire (Racines)",
            stat_image_ratio: "Articles contenant des images",
            chart_rubrics: "Distribution des rubriques des documents",
            chart_stems: "Racines de vocabulaire à poids élevé (TF-IDF)",
            inspect_title: "Outil de recherche d'index inversé",
            inspect_desc: "Interrogez directement les structures d'index inversé. Tapez un terme racinisé ou une métadonnée pour inspecter sa liste de postings.",
            lbl_term: "Terme / Mot",
            lbl_field: "Champ d'index",
            btn_inspect: "Interroger l'index",
            opt_text: "Contenu (text)",
            opt_title: "Titre (title)",
            opt_rubric: "Rubrique (rubric)",
            opt_author: "Auteur (author)",
            opt_date: "Date de publication (date)",
            opt_images: "Métadonnées d'image (images)",
            inspect_matches: "correspondances trouvées dans l'index",
            inspect_index: ".",
            inspect_postings_title: "Représentation de la liste de postings (ID Doc & Freq)",
            perf_title: "Benchmarks de performance",
            perf_desc: "Mesurez la latence, la précision et le rappel du moteur de recherche NLP. Comparez les statistiques pré-calculées avec les tests en temps réel.",
            btn_live_benchmark: "⚡ Lancer le benchmark",
            btn_running_benchmark: "⏱️ Exécution du benchmark...",
            lbl_pre_latency: "Latence pré-calculée",
            lbl_live_latency: "Latence en direct",
            lbl_accuracy: "Précision du système",
            perf_table_title: "Suite de tests de validation & performance",
            th_id: "ID",
            th_query: "Requête de validation",
            th_docs: "Docs retournés",
            th_precision: "Précision",
            th_recall: "Rappel",
            th_pre_speed: "Vitesse pré-calculée",
            th_live_speed: "Vitesse en direct (moyenne de 10 exécutions)",
            loading_metrics: "Chargement des métriques de performance...",
            awaiting_test: "En attente du test...",
            measuring: "Mesure...",
            running: "Calcul...",
            failed: "Échoué",
            error: "Erreur",
            
            // Dynamic/JS Strings
            analyzing_query: "Analyse grammaticale de la requête et exécution de la recherche...",
            err_execution: "Erreur lors de l'exécution de la requête : ",
            no_logs: "Aucun log d'exécution disponible.",
            matched_msg: "article correspondant",
            matched_msg_plural: "articles correspondants",
            no_results_found: "Aucun document trouvé. Vérifiez vos filtres ou suggestions orthographiques.",
            no_tokens: "Aucun mot-clé trouvé (requête métadonnées uniquement).",
            no_stems: "Aucune racine générée.",
            no_meta_filters: "Aucun filtre métadonnées actif.",
            empty_eq: "Équation vide (les filtres de métadonnées correspondent à tout)",
            loading_rubrics: "Chargement des données de rubrique...",
            no_rubrics: "Aucune rubrique indexée.",
            loading_vocab: "Chargement des poids du vocabulaire...",
            no_vocab: "Index de vocabulaire vide.",
            scanning_indexes: "Recherche dans les index...",
            no_postings_found: "Aucune entrée de postings trouvée pour le terme",
            err_connect: "Impossible de se connecter au service de recherche.",
            db_notice: "Remarque : La base de données étant 100% en français, les résultats de recherche seront également retournés en français.",
            init_starting: "Démarrage du pipeline du moteur de recherche...",
            init_phase1: "Phase 1: Génération du corpus XML à partir des bulletins...",
            init_phase2: "Phase 2: Tokenisation et filtrage des stopwords...",
            init_phase3: "Phase 3: Racinisation et calcul des index TF-IDF...",
            init_phase4: "Phase 4: Chargement des composants de recherche...",
            init_phase5: "Phase 5: Exécution automatique des tests de validation...",
            init_err_connect: "Connexion au service de recherche..."
        },
        es: {
            logo_title: "PySearchNLP",
            subtitle: "Motor de Búsqueda y Procesamiento de PLN desde cero",
            tab_search: "Portal de Búsqueda",
            tab_analytics: "Estadísticas del Corpus",
            tab_inspector: "Inspector de Índices",
            tab_performance: "Rendimiento del Motor",
            search_placeholder: "Ingrese su consulta en lenguaje natural (ej: 'articles de la rubrique Focus parlant d'innovation')...",
            sort_relevance: "Ordenar por relevancia",
            sort_newest: "Más recientes primero",
            sort_oldest: "Más antiguos primero",
            search_btn: "Buscar",
            try_queries: "Pruebe estas consultas:",
            nlp_title: "Pipeline de PLN Paso a Paso",
            step1_title: "Tokenización y Filtrado de Ruido",
            step1_desc: "Ninguna palabra clave procesada aún.",
            step2_title: "Corrección Ortográfica y Stemming",
            step2_desc: "Esperando entrada de búsqueda...",
            step3_title: "Restricciones de Metadatos Estructurales",
            step3_desc: "Ninguna restricción detectada.",
            step4_title: "Lógica Booleana Procesada",
            step4_desc: "Esperando evaluación...",
            btn_show_json: "Mostrar JSON estructurado",
            btn_hide_json: "Ocultar JSON de búsqueda",
            btn_show_logs: "Mostrar logs del sistema",
            btn_hide_logs: "Ocultar logs",
            json_header: "Representación estructurada de la búsqueda",
            logs_header: "Logs de ejecución en tiempo real",
            stat_total_docs: "Total de documentos indexados",
            stat_vocab_size: "Tamaño del vocabulario (Stems)",
            stat_image_ratio: "Artículos con imágenes",
            chart_rubrics: "Distribución de categorías (rubrics)",
            chart_stems: "Términos del vocabulario de mayor peso (TF-IDF)",
            inspect_title: "Herramienta de consulta del índice invertido",
            inspect_desc: "Consulte directamente las estructuras del índice invertido. Escriba un término o metadato para inspeccionar su lista de postings.",
            lbl_term: "Término / Palabra",
            lbl_field: "Campo del índice",
            btn_inspect: "Consultar índice invertido",
            opt_text: "Contenido (text)",
            opt_title: "Título (title)",
            opt_rubric: "Categoría (rubric)",
            opt_author: "Autor (author)",
            opt_date: "Fecha de publicación (date)",
            opt_images: "Metadatos de imagen (images)",
            inspect_matches: "coincidencias encontradas en el índice",
            inspect_index: ".",
            inspect_postings_title: "Representación de la lista de postings (ID Doc y Freq)",
            perf_title: "Benchmarks de rendimiento",
            perf_desc: "Mida la latencia de búsqueda, la precisión y el recall del motor NLP. Compare estadísticas de validación pre-calculadas con pruebas en vivo.",
            btn_live_benchmark: "⚡ Ejecutar benchmark en vivo",
            btn_running_benchmark: "⏱️ Ejecutando benchmark...",
            lbl_pre_latency: "Latencia pre-calculada",
            lbl_live_latency: "Latencia en vivo",
            lbl_accuracy: "Precisión del sistema",
            perf_table_title: "Suite de pruebas de validación y rendimiento",
            th_id: "ID",
            th_query: "Texto de la consulta de validación",
            th_docs: "Docs retornados",
            th_precision: "Precisión",
            th_recall: "Recall",
            th_pre_speed: "Velocidad pre-calculada",
            th_live_speed: "Velocidad en vivo (media de 10 ejecuciones)",
            loading_metrics: "Cargando métricas de rendimiento...",
            awaiting_test: "Esperando prueba...",
            measuring: "Midiendo...",
            running: "Ejecutando...",
            failed: "Falló",
            error: "Error",
            
            // Dynamic/JS Strings
            analyzing_query: "Analizando la gramática de la consulta y ejecutando la recuperación...",
            err_execution: "Error al ejecutar la consulta: ",
            no_logs: "No hay logs de ejecución disponibles.",
            matched_msg: "artículo coincidente",
            matched_msg_plural: "artículos coincidentes",
            no_results_found: "No se encontraron documentos. Verifique sus filtros o sugerencias ortográficas.",
            no_tokens: "No se encontraron palabras clave (búsqueda de metadatos únicamente).",
            no_stems: "No se generaron raíces léxicas.",
            no_meta_filters: "No hay filtros estructurales de metadatos activos.",
            empty_eq: "Ecuación vacía (los filtros de metadatos coinciden con todo)",
            loading_rubrics: "Cargando datos de categorías...",
            no_rubrics: "No hay categorías de rubricas indexadas.",
            loading_vocab: "Cargando pesos del vocabulario...",
            no_vocab: "Índice de vocabulario vacío.",
            scanning_indexes: "Buscando en los índices...",
            no_postings_found: "No se encontraron postings para el término",
            err_connect: "Error al conectar con el servicio de búsqueda.",
            db_notice: "Nota: Como la base de datos está 100% en francés, los resultados de la búsqueda también se devolverán en francés.",
            init_starting: "Iniciando el pipeline del motor de búsqueda...",
            init_phase1: "Fase 1: Generando corpus XML a partir de boletines...",
            init_phase2: "Fase 2: Tokenizando y filtrando stopwords...",
            init_phase3: "Fase 3: Stemming y computación de índices TF-IDF...",
            init_phase4: "Fase 4: Cargando componentes de búsqueda y diccionario...",
            init_phase5: "Fase 5: Ejecutando automáticamente pruebas de benchmark...",
            init_err_connect: "Conectando al servicio de búsqueda..."
        },
        de: {
            logo_title: "PySearchNLP",
            subtitle: "NLP-Suchmaschine & Verarbeitungs-Pipeline von Grund auf neu entwickelt",
            tab_search: "Suchportal",
            tab_analytics: "Korpus-Statistiken",
            tab_inspector: "Index-Inspektor",
            tab_performance: "Motorleistung",
            search_placeholder: "Geben Sie Ihre Suchanfrage in natürlicher Sprache ein (z. B. 'articles de la rubrique Focus parlant d'innovation')...",
            sort_relevance: "Nach Relevanz sortieren",
            sort_newest: "Neueste zuerst",
            sort_oldest: "Älteste zuerst",
            search_btn: "Suchen",
            try_queries: "Probieren Sie diese Abfragen:",
            nlp_title: "NLP-Pipeline Schritt für Schritt",
            step1_title: "Tokenisierung & Rauschfilterung",
            step1_desc: "Noch keine Schlüsselwörter verarbeitet.",
            step2_title: "Rechtschreibprüfung & Stemming",
            step2_desc: "Warten auf Sucheingabe...",
            step3_title: "Strukturelle Metadatenbeschränkungen",
            step3_desc: "Keine Einschränkungen erkannt.",
            step4_title: "Verarbeitete Boolesche Logik",
            step4_desc: "Warten auf Auswertung...",
            btn_show_json: "Strukturiertes JSON anzeigen",
            btn_hide_json: "JSON ausblenden",
            btn_show_logs: "Ausführungslogs anzeigen",
            btn_hide_logs: "Logs ausblenden",
            json_header: "Strukturierte Suchanfrage",
            logs_header: "Ausführungs-Logs in Echtzeit",
            stat_total_docs: "Gesamtzahl indexierter Dokumente",
            stat_vocab_size: "Vokabulargröße (Stems)",
            stat_image_ratio: "Artikel mit Bildern",
            chart_rubrics: "Kategorieverteilung (Rubrics) der Dokumente",
            chart_stems: "Häufigste Vokabelstämme mit hohem Gewicht (TF-IDF)",
            inspect_title: "Invertiertes Index-Suchwerkzeug",
            inspect_desc: "Fragen Sie die zugrunde liegenden Indexstrukturen direkt ab. Geben Sie ein Wort oder Metadatum ein, um die Postingliste anzuzeigen.",
            lbl_term: "Begriff / Wort",
            lbl_field: "Indexfeld",
            btn_inspect: "Index abfragen",
            opt_text: "Inhalt (text)",
            opt_title: "Titel (title)",
            opt_rubric: "Kategorie (rubric)",
            opt_author: "Autor (author)",
            opt_date: "Veröffentlichungsdatum (date)",
            opt_images: "Bild-Metadaten (images)",
            inspect_matches: "Treffer im Index gefunden",
            inspect_index: ".",
            inspect_postings_title: "Posting-Listen-Darstellung (Doc ID & Häufigkeit)",
            perf_title: "Leistungs-Benchmarks",
            perf_desc: "Messen Sie die Latenz, Präzision und Recall der NLP-Suchmaschine. Vergleichen Sie vorberechnete Statistiken mit Live-Latenztests.",
            btn_live_benchmark: "⚡ Live-Benchmark ausführen",
            btn_running_benchmark: "⏱️ Benchmark läuft...",
            lbl_pre_latency: "Vorberechnete Latenz",
            lbl_live_latency: "Live-Test-Latenz",
            lbl_accuracy: "Systemgenauigkeit",
            perf_table_title: "Validierungs- & Leistungstests Suite",
            th_id: "ID",
            th_query: "Validierungsabfragetext",
            th_docs: "Dokumente zurückgegeben",
            th_precision: "Präzision",
            th_recall: "Recall",
            th_pre_speed: "Vorberechnete Geschwindigkeit",
            th_live_speed: "Live-Geschwindigkeit (Mittelwert aus 10 Läufen)",
            loading_metrics: "Leistungsdaten werden geladen...",
            awaiting_test: "Warten auf Test...",
            measuring: "Messung...",
            running: "Ausführung...",
            failed: "Fehlgeschlagen",
            error: "Fehler",
            
            // Dynamic/JS Strings
            analyzing_query: "Suchanfrage-Grammatik wird analysiert und Dokumente werden abgerufen...",
            err_execution: "Fehler beim Ausführen der Anfrage: ",
            no_logs: "Keine Ausführungslogs verfügbar.",
            matched_msg: "passender Artikel",
            matched_msg_plural: "passende Artikel",
            no_results_found: "Keine passenden Dokumente gefunden. Prüfen Sie Filter oder Rechtschreibkorrekturen.",
            no_tokens: "Keine Schlüsselwörter gefunden (nur Metadaten-Filterung).",
            no_stems: "Keine Stammformen generiert.",
            no_meta_filters: "Keine Metadatenbeschränkungen aktiv.",
            empty_eq: "Leere Gleichung (Metadaten-Filter passen auf alle Dokumente)",
            loading_rubrics: "Kategoriedaten werden geladen...",
            no_rubrics: "Keine Kategorien indexiert.",
            loading_vocab: "Häufigkeiten werden geladen...",
            no_vocab: "Vokabular-Indizes leer.",
            scanning_indexes: "Indexe werden gescannt...",
            no_postings_found: "Keine Posting-Einträge gefunden für Begriff",
            err_connect: "Verbindung zur Such-API fehlgeschlagen.",
            db_notice: "Hinweis: Da die Datenbank zu 100% auf Französisch ist, werden die Suchergebnisse ebenfalls auf Französisch ausgegeben.",
            init_starting: "Suchmaschinen-Pipeline wird gestartet...",
            init_phase1: "Phase 1: XML-Korpus wird aus Newslettern generiert...",
            init_phase2: "Phase 2: Tokenisierung und Stoppwort-Filterung...",
            init_phase3: "Phase 3: Stemming und Berechnung der TF-IDF-Indizes...",
            init_phase4: "Phase 4: Suchkomponenten und Wörterbuch werden geladen...",
            init_phase5: "Phase 5: Validierungs- und Benchmarktests werden ausgeführt...",
            init_err_connect: "Verbindung zum Backend wird aufgebaut..."
        }
    };

    // State Variables
    let currentTheme = localStorage.getItem('theme') || 'dark';
    let currentLang = localStorage.getItem('lang') || 'en';
    let cachedBenchmarkData = null;

    // Apply Saved Theme immediately on startup
    if (currentTheme === 'light') {
        document.body.classList.add('light-theme');
    }

    // UI Elements
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsList = document.getElementById('results-list');
    const resultsInfo = document.getElementById('results-info');
    
    // Code blocks & Stepper
    const diagnosticsPanel = document.getElementById('diagnostics-panel');
    const jsonOutput = document.getElementById('json-output');
    const logsOutput = document.getElementById('logs-output');
    const toggleJsonBtn = document.getElementById('toggle-json-btn');
    const toggleLogsBtn = document.getElementById('toggle-logs-btn');
    const jsonView = document.getElementById('json-view');
    const logsView = document.getElementById('logs-view');
    
    const stepTokens = document.getElementById('step-tokens');
    const stepStems = document.getElementById('step-stems');
    const stepMetadata = document.getElementById('step-metadata');
    const stepEquation = document.getElementById('step-equation');
    
    // Tabs elements
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // Index Inspector
    const inspectorTerm = document.getElementById('inspector-term');
    const inspectorField = document.getElementById('inspector-field');
    const inspectBtn = document.getElementById('inspect-btn');
    const inspectorLoader = document.getElementById('inspector-loader');
    const inspectorResults = document.getElementById('inspector-results');
    const postingsList = document.getElementById('postings-list');
    const inspectorCount = document.getElementById('inspector-results-count');
    const inspectorFieldSpan = document.getElementById('inspector-results-field');

    // Controls
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const langSelect = document.getElementById('lang-select');

    if (langSelect) {
        langSelect.value = currentLang;
    }

    // Translation logic
    function translateUI(lang) {
        const trans = TRANSLATIONS[lang] || TRANSLATIONS.en;
        
        // 1. Elements with data-i18n
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (trans[key]) {
                if (key.startsWith('tab_') || key.startsWith('btn_') || key === 'logo_title' || key === 'search_btn' || key === 'btn_live_benchmark') {
                    el.innerHTML = trans[key];
                } else {
                    el.textContent = trans[key];
                }
            }
        });

        // 2. Placeholder attributes
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (trans[key]) {
                el.placeholder = trans[key];
            }
        });
    }

    // Translate dynamic string helper
    function getDynamicString(key) {
        const trans = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
        return trans[key] || TRANSLATIONS.en[key] || '';
    }

    // Bind theme and language controls
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            if (document.body.classList.contains('light-theme')) {
                document.body.classList.remove('light-theme');
                localStorage.setItem('theme', 'dark');
                currentTheme = 'dark';
            } else {
                document.body.classList.add('light-theme');
                localStorage.setItem('theme', 'light');
                currentTheme = 'light';
            }
        });
    }

    if (langSelect) {
        langSelect.addEventListener('change', (e) => {
            currentLang = e.target.value;
            localStorage.setItem('lang', currentLang);
            translateUI(currentLang);
            // Redraw active views if needed
            if (document.getElementById('benchmark-tab').classList.contains('active')) {
                loadBenchmarks();
            }
        });
    }

    // Trigger Initial Translation
    translateUI(currentLang);
    checkInitStatus();

    // Suggestions click handlers
    const suggestions = document.querySelectorAll('.suggestion-tag');
    suggestions.forEach(btn => {
        btn.addEventListener('click', () => {
            searchInput.value = btn.textContent;
            performSearch();
        });
    });

    // 1. Navigation Tab Logic
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            // Toggle buttons state
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Toggle panes visibility
            tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === targetTab) {
                    pane.classList.add('active');
                    
                    // Trigger specific API calls on tab activation
                    if (targetTab === 'analytics-tab') {
                        loadCorpusAnalytics();
                    } else if (targetTab === 'benchmark-tab') {
                        loadBenchmarks();
                    }
                }
            });
        });
    });

    // 2. Query Diagnostics Panel Toggle Logs/JSON
    toggleJsonBtn.addEventListener('click', () => {
        if (jsonView.style.display === 'none') {
            jsonView.style.display = 'block';
            toggleJsonBtn.textContent = getDynamicString('btn_hide_json');
        } else {
            jsonView.style.display = 'none';
            toggleJsonBtn.textContent = getDynamicString('btn_show_json');
        }
    });

    toggleLogsBtn.addEventListener('click', () => {
        if (logsView.style.display === 'none') {
            logsView.style.display = 'block';
            toggleLogsBtn.textContent = getDynamicString('btn_hide_logs');
        } else {
            logsView.style.display = 'none';
            toggleLogsBtn.textContent = getDynamicString('btn_show_logs');
        }
    });

    // 3. Search Engine Execution
    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        // Reset views
        resultsList.innerHTML = '';
        resultsInfo.textContent = '';
        diagnosticsPanel.style.display = 'none';
        loader.style.display = 'block';

        // Load loader text translation
        loader.querySelector('p').textContent = getDynamicString('analyzing_query');

        try {
            const sort = document.getElementById('sort-select').value;
            const response = await fetch(`/search?q=${encodeURIComponent(query)}&sort=${sort}`);
            const data = await response.json();
            
            loader.style.display = 'none';
            
            if (data.error) {
                resultsInfo.textContent = getDynamicString('err_execution') + data.error;
                return;
            }
            
            // Render Query Diagnostics Stepper
            diagnosticsPanel.style.display = 'block';
            jsonOutput.textContent = JSON.stringify(data.structured, null, 4);
            logsOutput.textContent = data.logs ? data.logs.join('\n') : getDynamicString('no_logs');
            
            // Set initial state of buttons
            toggleJsonBtn.textContent = getDynamicString('btn_show_json');
            toggleLogsBtn.textContent = getDynamicString('btn_show_logs');
            jsonView.style.display = 'none';
            logsView.style.display = 'none';
            
            renderPipelineStepper(data.structured);
            
            // Render Results Info
            const count = data.results.length;
            const matchedText = count === 1 ? getDynamicString('matched_msg') : getDynamicString('matched_msg_plural');
            resultsInfo.innerHTML = `<span>${count} ${matchedText}</span> <span style="font-size: 0.85rem; opacity: 0.6; margin-left: 10px;">(${data.time_ms} ms)</span>`;
            
            if (count === 0) {
                resultsList.innerHTML = `
                    <div class="no-results-card">
                        <span class="no-results-icon">🔍</span>
                        <h3 style="margin-bottom: 8px;">No matches found</h3>
                        <p style="color:var(--text-muted); max-width: 400px; margin: 0 auto; line-height: 1.4;">${getDynamicString('no_results_found')}</p>
                    </div>
                `;
            } else {
                data.results.forEach(res => {
                    const card = document.createElement('div');
                    card.className = 'result-card';
                    
                    const highlights = data.structured.highlight_keywords || [];
                    const highlightedTitle = highlightText(res.title, highlights);
                    const highlightedSnippet = highlightText(res.snippet, highlights);
                    
                    card.innerHTML = `
                        <div class="result-header">
                            <span class="result-date">${escapeHtml(res.date || 'Unspecified')}</span>
                            <span class="result-rubric">${escapeHtml(res.rubric || 'General')}</span>
                        </div>
                        <h3><a href="/data/BULLETINS/${escapeHtml(res.filename)}" target="_blank">${highlightedTitle}</a></h3>
                        <p class="result-snippet">${highlightedSnippet}</p>
                        <div class="result-footer">
                            <span class="result-score">Relevance score: <strong>${escapeHtml(res.score)}</strong></span>
                            <span class="result-author">Author: ${escapeHtml(res.author || 'Anonymous')}</span>
                        </div>
                    `;
                    resultsList.appendChild(card);
                });
            }
        } catch (err) {
            loader.style.display = 'none';
            resultsInfo.textContent = getDynamicString('err_connect');
            console.error(err);
        }
    }

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    // 4. Render Visual NLP Stepper
    function renderPipelineStepper(struct) {
        // Step 1: Tokenization
        if (struct.keywords && struct.keywords.length > 0) {
            document.querySelectorAll('.step')[0].classList.add('active');
            const kwHtml = struct.keywords.map(k => `<span class="nlp-token">${escapeHtml(k)}</span>`).join('');
            stepTokens.innerHTML = kwHtml;
        } else {
            document.querySelectorAll('.step')[0].classList.remove('active');
            stepTokens.innerHTML = getDynamicString('no_tokens');
        }

        // Step 2: Spelling Correction & Stemming
        if (struct.highlight_keywords && struct.highlight_keywords.length > 0) {
            document.querySelectorAll('.step')[1].classList.add('active');
            const highlightHtml = struct.highlight_keywords.map((w, idx) => {
                const mappedStem = struct.keywords[idx] || '';
                return `
                    <div style="display:flex; justify-content:space-between; margin-bottom: 5px; font-size: 0.85rem;">
                        <span style="color:var(--text-primary); font-weight:600;">${escapeHtml(w)}</span>
                        <span style="color:var(--secondary); font-family:var(--font-code);">${escapeHtml(mappedStem)}</span>
                    </div>
                `;
            }).join('');
            stepStems.innerHTML = highlightHtml;
        } else {
            document.querySelectorAll('.step')[1].classList.remove('active');
            stepStems.innerHTML = getDynamicString('no_stems');
        }

        // Step 3: Structural Metadata constraints
        const filters = [];
        if (struct.rubric) filters.push(`Rubric: <strong>${escapeHtml(struct.rubric)}</strong>`);
        if (struct.date_min || struct.date_max) filters.push(`Date range: <strong>${escapeHtml(struct.date_min || '*')}</strong> to <strong>${escapeHtml(struct.date_max || '*')}</strong>`);
        if (struct.image !== null) filters.push(`Images required: <strong>${struct.image ? 'Yes' : 'No'}</strong>`);
        if (struct.search_field) filters.push(`Search target field: <strong>${escapeHtml(struct.search_field)}</strong>`);

        if (filters.length > 0) {
            document.querySelectorAll('.step')[2].classList.add('active');
            stepMetadata.innerHTML = filters.join('<br>');
        } else {
            document.querySelectorAll('.step')[2].classList.remove('active');
            stepMetadata.innerHTML = getDynamicString('no_meta_filters');
        }

        // Step 4: Boolean Equation
        const eq = struct.equation || '';
        if (eq) {
            document.querySelectorAll('.step')[3].classList.add('active');
            stepEquation.textContent = eq;
        } else {
            document.querySelectorAll('.step')[3].classList.remove('active');
            stepEquation.textContent = getDynamicString('empty_eq');
        }
    }

    // 5. Corpus Analytics Dashboard
    async function loadCorpusAnalytics() {
        const totalDocsSpan = document.getElementById('stat-total-docs');
        const vocabSizeSpan = document.getElementById('stat-vocab-size');
        const imageRatioSpan = document.getElementById('stat-image-ratio');
        const rubricChart = document.getElementById('rubric-chart');
        const termsChart = document.getElementById('terms-chart');

        rubricChart.innerHTML = `<p class="chart-loading">${getDynamicString('loading_rubrics')}</p>`;
        termsChart.innerHTML = `<p class="chart-loading">${getDynamicString('loading_vocab')}</p>`;

        try {
            const res = await fetch('/api/analytics');
            const data = await res.json();

            totalDocsSpan.textContent = data.total_documents;
            vocabSizeSpan.textContent = data.vocabulary_size;
            
            const imagePercent = ((data.documents_with_images / data.total_documents) * 100).toFixed(1);
            imageRatioSpan.textContent = `${imagePercent}% (${data.documents_with_images})`;

            // Render Rubrics Chart
            rubricChart.innerHTML = '';
            if (data.rubrics_distribution && data.rubrics_distribution.length > 0) {
                const maxVal = Math.max(...data.rubrics_distribution.map(r => r[1]));
                data.rubrics_distribution.forEach(r => {
                    const rubricName = r[0];
                    const count = r[1];
                    const barPercent = ((count / maxVal) * 100).toFixed(0);

                    const barItem = document.createElement('div');
                    barItem.className = 'chart-bar-item';
                    barItem.innerHTML = `
                        <div class="chart-bar-label">${escapeHtml(rubricName)} (${count})</div>
                        <div class="chart-bar-track">
                            <div class="chart-bar-fill" style="width: 0%;"></div>
                        </div>
                    `;
                    rubricChart.appendChild(barItem);
                    setTimeout(() => {
                        barItem.querySelector('.chart-bar-fill').style.width = `${barPercent}%`;
                    }, 50);
                });
            } else {
                rubricChart.innerHTML = `<p class="chart-loading">${getDynamicString('no_rubrics')}</p>`;
            }

            // Render Vocabulary stems weights
            termsChart.innerHTML = '';
            if (data.top_terms && data.top_terms.length > 0) {
                const maxVal = Math.max(...data.top_terms.map(t => t.score));
                data.top_terms.forEach(t => {
                    const barPercent = ((t.score / maxVal) * 100).toFixed(0);

                    const barItem = document.createElement('div');
                    barItem.className = 'chart-bar-item';
                    barItem.innerHTML = `
                        <div class="chart-bar-label" style="font-family:var(--font-code);">${escapeHtml(t.term)} (${t.score})</div>
                        <div class="chart-bar-track">
                            <div class="chart-bar-fill" style="width: 0%; background:var(--secondary);"></div>
                        </div>
                    `;
                    termsChart.appendChild(barItem);
                    setTimeout(() => {
                        barItem.querySelector('.chart-bar-fill').style.width = `${barPercent}%`;
                    }, 50);
                });
            } else {
                termsChart.innerHTML = `<p class="chart-loading">${getDynamicString('no_vocab')}</p>`;
            }

        } catch (err) {
            console.error("Corpus stats loading failed: ", err);
        }
    }

    // 6. Inverted Index Lookup Inspector
    async function queryInvertedIndex() {
        const term = inspectorTerm.value.trim();
        const field = inspectorField.value;

        if (!term) return;

        inspectorLoader.style.display = 'block';
        inspectorResults.style.display = 'none';
        postingsList.innerHTML = '';

        try {
            const res = await fetch(`/api/index-lookup?term=${encodeURIComponent(term)}&field=${field}`);
            const data = await res.json();

            inspectorLoader.style.display = 'none';
            inspectorResults.style.display = 'block';

            if (data.error) {
                inspectorCount.textContent = getDynamicString('error');
                inspectorFieldSpan.textContent = field;
                postingsList.innerHTML = `<p style="color:#ef4444; grid-column: 1/-1;">Error lookup: ${data.error}</p>`;
                return;
            }

            inspectorCount.textContent = data.postings_count;
            inspectorFieldSpan.textContent = data.field;

            if (data.postings && data.postings.length > 0) {
                data.postings.forEach(post => {
                    const card = document.createElement('div');
                    card.className = 'posting-card';
                    card.innerHTML = `
                        <div class="posting-doc">Doc #${escapeHtml(post.doc_id)}</div>
                        <div class="posting-freq">${escapeHtml(post.frequency)}</div>
                    `;
                    postingsList.appendChild(card);
                });
            } else {
                postingsList.innerHTML = `<p style="color:var(--text-muted); grid-column: 1/-1; font-style:italic;">${getDynamicString('no_postings_found')} "${escapeHtml(term)}" ${getDynamicString('inspect_index')}</p>`;
            }
        } catch (err) {
            inspectorLoader.style.display = 'none';
            console.error("Index lookup failed: ", err);
        }
    }

    inspectBtn.addEventListener('click', queryInvertedIndex);
    inspectorTerm.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') queryInvertedIndex();
    });

    // 6. Engine Performance Benchmarking
    async function loadBenchmarks() {
        const tableBody = document.getElementById('benchmark-table-body');
        const avgLatencySpan = document.getElementById('benchmark-avg-latency');
        const precisionRecallSpan = document.getElementById('benchmark-precision-recall');
        const liveLatencySpan = document.getElementById('benchmark-live-latency');

        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="table-loading">${getDynamicString('loading_metrics')}</td>
            </tr>
        `;
        avgLatencySpan.textContent = '-';
        precisionRecallSpan.textContent = '-';
        liveLatencySpan.textContent = '-';

        try {
            const res = await fetch('/api/benchmark-results');
            if (!res.ok) {
                let errMsg = "Could not fetch benchmark results (HTTP " + res.status + ")";
                try {
                    const errData = await res.json();
                    if (errData.error) {
                        errMsg = errData.error;
                        if (errData.searched_paths) {
                            console.warn("Searched paths:", errData.searched_paths);
                            errMsg += "<br><br><strong>Checked paths:</strong><br>" + errData.searched_paths.map(p => `<code>${escapeHtml(p)}</code>`).join("<br>");
                        }
                    }
                } catch(e) {}
                throw new Error(errMsg);
            }
            const data = await res.json();
            cachedBenchmarkData = data;

            // Compute summary metrics
            let totalLatency = 0;
            let totalPrecision = 0;
            let totalRecall = 0;
            let validQueryCount = 0;

            tableBody.innerHTML = '';
            data.forEach(q => {
                const tr = document.createElement('tr');
                
                // Query 9 has no relevant documents, so precision/recall are technically undefined (reported as 0)
                const isQ9 = q.query_id === 9;
                const pVal = isQ9 ? "N/A" : `${(q.precision * 100).toFixed(0)}%`;
                const rVal = isQ9 ? "N/A" : `${(q.recall * 100).toFixed(0)}%`;
                
                if (!isQ9) {
                    totalPrecision += q.precision;
                    totalRecall += q.recall;
                    validQueryCount++;
                }
                totalLatency += q.average_response_time_ms;

                tr.innerHTML = `
                    <td><strong>#${q.query_id}</strong></td>
                    <td style="color: var(--text-primary); font-weight: 500;">${escapeHtml(q.query)}</td>
                    <td class="latency-highlight">${q.nb_returned}</td>
                    <td><span class="badge ${q.precision === 1 ? 'badge-success' : 'badge-info'}">${pVal}</span></td>
                    <td><span class="badge ${q.recall === 1 ? 'badge-success' : 'badge-info'}">${rVal}</span></td>
                    <td class="latency-highlight">${q.average_response_time_ms.toFixed(3)} ms</td>
                    <td id="live-time-q${q.query_id}" style="font-style: italic; color: var(--text-muted);">${getDynamicString('awaiting_test')}</td>
                `;
                tableBody.appendChild(tr);
            });

            const avgLatency = totalLatency / data.length;
            avgLatencySpan.textContent = `${avgLatency.toFixed(2)} ms`;

            const avgPrecision = (totalPrecision / validQueryCount) * 100;
            const avgRecall = (totalRecall / validQueryCount) * 100;
            precisionRecallSpan.textContent = `${avgPrecision.toFixed(0)}% / ${avgRecall.toFixed(0)}%`;

        } catch (err) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="table-loading" style="color: #f43f5e; padding: 25px; line-height: 1.5; text-align: left;">
                        <strong>Failed to load benchmarks:</strong><br>${err.message}<br><br>
                        <strong>Troubleshooting Checklist:</strong><br>
                        1. <strong>Restart the Flask server</strong> (you must stop the terminal process and start it again via <code>python src/web/app.py</code> to load the new API endpoints).<br>
                        2. Force-refresh the browser page (Ctrl + F5 or Cmd + Shift + R) to make sure you have the newest JavaScript file loaded.<br>
                        3. Run the evaluation script if you haven't: <code>python src/evaluation.py --runs 100 --inspect --top 50</code>
                    </td>
                </tr>
            `;
            console.error(err);
        }
    }

    const runLiveBtn = document.getElementById('run-live-benchmark-btn');
    runLiveBtn.addEventListener('click', async () => {
        const liveLatencySpan = document.getElementById('benchmark-live-latency');
        
        runLiveBtn.disabled = true;
        runLiveBtn.textContent = getDynamicString('btn_running_benchmark');
        liveLatencySpan.textContent = getDynamicString('measuring');

        // Clear all previous live times
        if (cachedBenchmarkData) {
            cachedBenchmarkData.forEach(q => {
                const td = document.getElementById(`live-time-q${q.query_id}`);
                if (td) td.textContent = getDynamicString('running');
            });
        }

        try {
            const res = await fetch('/api/run-benchmark', { method: 'POST' });
            if (!res.ok) throw new Error("Could not execute live benchmark");
            const data = await res.json();

            data.results.forEach(q => {
                const td = document.getElementById(`live-time-q${q.query_id}`);
                if (td) {
                    td.className = 'live-latency-highlight';
                    td.textContent = `${q.live_time_ms.toFixed(3)} ms`;
                }
            });

            liveLatencySpan.textContent = `${data.average_system_latency_ms.toFixed(2)} ms`;
        } catch (err) {
            alert("Live benchmark failed: " + err.message);
            liveLatencySpan.textContent = getDynamicString('error');
            if (cachedBenchmarkData) {
                cachedBenchmarkData.forEach(q => {
                    const td = document.getElementById(`live-time-q${q.query_id}`);
                    if (td) td.textContent = getDynamicString('failed');
                });
            }
        } finally {
            runLiveBtn.disabled = false;
            runLiveBtn.textContent = getDynamicString('btn_live_benchmark');
        }
    });

    // 7. Helper Utilities
    function escapeHtml(text) {
        return String(text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function escapeRegex(text) {
        return String(text).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function highlightText(rawText, keywords) {
        const safeText = escapeHtml(rawText || '');
        if (!Array.isArray(keywords) || keywords.length === 0) {
            return safeText;
        }

        const literalKeywords = keywords
            .map(k => String(k || '').trim())
            .filter(Boolean)
            .filter(k => k.length >= 2)
            .map(escapeRegex);

        if (literalKeywords.length === 0) {
            return safeText;
        }

        const pattern = new RegExp(`(${literalKeywords.join('|')})`, 'gi');
        return safeText.replace(pattern, '<strong>$1</strong>');
    }

    // Poll initialization status
    function checkInitStatus() {
        const initOverlay = document.getElementById('init-overlay');
        const initStatusMsg = document.getElementById('init-status-msg');

        if (!initOverlay) return;

        const interval = setInterval(async () => {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();

                if (data.ready) {
                    clearInterval(interval);
                    initOverlay.classList.add('hidden');
                    // Refresh data for the active view if needed
                    const activeTab = document.querySelector('.tab-btn.active');
                    if (activeTab) {
                        const targetTab = activeTab.getAttribute('data-tab');
                        if (targetTab === 'analytics-tab') {
                            loadCorpusAnalytics();
                        } else if (targetTab === 'benchmark-tab') {
                            loadBenchmarks();
                        }
                    }
                } else if (data.status && data.status.startsWith("Error:")) {
                    clearInterval(interval);
                    
                    const initCard = document.querySelector('.init-card');
                    if (initCard) {
                        initCard.classList.add('error-state');
                        const spinner = initCard.querySelector('.spinner');
                        if (spinner) {
                            spinner.style.display = 'none';
                        }
                    }
                    
                    // Build error presentation HTML in the selected language
                    let errTitle = "Pipeline Initialization Failed";
                    let errHelp = "Please verify your setup. If deploying on Render, check if the bulletins are committed under <code>data/BULLETINS/</code> or examine the logs in the Render dashboard.";
                    let retryText = "Retry Connection";
                    
                    if (currentLang === 'pt') {
                        errTitle = "Falha na Inicialização do Pipeline";
                        errHelp = "Por favor, verifique as configurações. Se estiver implantando no Render, verifique se os boletins estão comitados na pasta <code>data/BULLETINS/</code> ou consulte os logs no painel do Render.";
                        retryText = "Tentar Conectar Novamente";
                    } else if (currentLang === 'fr') {
                        errTitle = "Échec de l'initialisation du pipeline";
                        errHelp = "Veuillez vérifier votre configuration. Si vous déployez sur Render, vérifiez si les bulletins sont commités dans le dossier <code>data/BULLETINS/</code> ou examinez les logs dans le tableau de bord Render.";
                        retryText = "Réessayer la connexion";
                    } else if (currentLang === 'es') {
                        errTitle = "Fallo en la inicialización del pipeline";
                        errHelp = "Por favor, verifique la configuración. Si está desplegando en Render, compruebe si los boletines están confirmados en la carpeta <code>data/BULLETINS/</code> o consulte los logs en el panel de Render.";
                        retryText = "Reintentar conexión";
                    } else if (currentLang === 'de') {
                        errTitle = "Pipeline-Initialisierung fehlgeschlagen";
                        errHelp = "Bitte überprüfen Sie Ihr Setup. Wenn Sie auf Render bereitstellen, prüfen Sie, ob die Bulletins im Ordner <code>data/BULLETINS/</code> committet sind oder überprüfen Sie die Logs im Render-Dashboard.";
                        retryText = "Verbindung erneut versuchen";
                    }
                    
                    let errHtml = `
                        <div class="error-title-row" style="display: flex; align-items: center; gap: 10px; justify-content: center; margin-bottom: 10px;">
                            <span class="error-warning-icon" style="font-size: 1.5rem;">⚠️</span>
                            <h3 style="color: #ef4444; margin: 0; font-size: 1.3rem; font-weight: 800;">${errTitle}</h3>
                        </div>
                        <p style="color: #fca5a5; font-size: 0.95rem; margin-top: 10px; font-weight: 600;">${data.status}</p>
                    `;
                    
                    if (data.error) {
                        errHtml += `
                            <div class="error-stack-container" style="text-align: left; width: 100%; margin-top: 15px;">
                                <pre style="background: rgba(0,0,0,0.45); padding: 15px; border-radius: var(--radius-sm); font-family: var(--font-code); font-size: 0.8rem; overflow-x: auto; max-height: 220px; border: 1px solid rgba(239,68,68,0.25); color: #fecaca; margin: 0; white-space: pre-wrap; word-break: break-all;">${data.error}</pre>
                            </div>
                        `;
                    }
                    
                    errHtml += `
                        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4; margin-top: 15px;">${errHelp}</p>
                        <button onclick="window.location.reload()" class="primary-btn" style="margin-top: 20px; background: #ef4444; box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4); border-color: #ef4444;">🔄 ${retryText}</button>
                    `;
                    
                    initStatusMsg.innerHTML = errHtml;
                } else {
                    let statusText = data.status;
                    if (statusText.includes("Phase 1")) {
                        statusText = getDynamicString("init_phase1") || statusText;
                    } else if (statusText.includes("Phase 2")) {
                        statusText = getDynamicString("init_phase2") || statusText;
                    } else if (statusText.includes("Phase 3")) {
                        statusText = getDynamicString("init_phase3") || statusText;
                    } else if (statusText.includes("Phase 4")) {
                        statusText = getDynamicString("init_phase4") || statusText;
                    } else if (statusText.includes("Phase 5")) {
                        statusText = getDynamicString("init_phase5") || statusText;
                    } else if (statusText.includes("Starting")) {
                        statusText = getDynamicString("init_starting") || statusText;
                    }
                    
                    if (data.detail) {
                        initStatusMsg.innerHTML = `${statusText}<br><span class="init-detail" style="font-size: 0.85rem; opacity: 0.7; color: var(--secondary); margin-top: 5px; display: block;">${escapeHtml(data.detail)}</span>`;
                    } else {
                        initStatusMsg.textContent = statusText;
                    }
                }
            } catch (err) {
                console.error("Error checking initialization status: ", err);
                initStatusMsg.textContent = getDynamicString("init_err_connect") || "Reconnecting to search backend...";
            }
        }, 800);
    }
});
