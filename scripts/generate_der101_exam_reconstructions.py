#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera preguntas DER101 reconstruidas desde un banco de exámenes anteriores.

Los enunciados defectuosos del banco complementario se usan únicamente como señal
de temas evaluados. Las respuestas y explicaciones se validan contra el compendio.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "Procesado/DER 101 - Introducción al Derecho/preguntas_examenes_anteriores.md"

SOURCE_FUENTES = (
    "introduccion_al_derecho_texto_completo.md, apartado «Las fuentes del Derecho "
    "y la normatividad jurídica», páginas extraídas 168-179; banco complementario "
    "atribuido a exámenes anteriores"
)
SOURCE_ORDEN = (
    "introduccion_al_derecho_texto_completo.md, apartado «El orden jurídico y la cultura»; "
    "banco complementario atribuido a exámenes anteriores"
)
SOURCE_FINES = (
    "introduccion_al_derecho_texto_completo.md, apartado «El Derecho, fines y principios»; "
    "banco complementario atribuido a exámenes anteriores"
)
SOURCE_RELACION = (
    "introduccion_al_derecho_texto_completo.md, apartado «Elementos de la relación jurídica»; "
    "cuestionario complementario contrastado con el compendio"
)


def single(qid, title, topic, prompt, options, correct, explanation, memory, source=SOURCE_FUENTES,
           difficulty="media", confusion="No confundas conceptos cercanos: identifica el elemento exacto que pide el enunciado."):
    return {
        "id": qid, "title": title, "topic": topic, "prompt": prompt,
        "options": options, "correct": [correct], "explanation": explanation,
        "memory": memory, "source": source, "difficulty": difficulty,
        "confusion": confusion, "type": "single",
    }


def multiple(qid, title, topic, prompt, options, correct, explanation, memory, source=SOURCE_FUENTES,
             difficulty="media", confusion="Revisa cada afirmación por separado; puede haber más de una correcta."):
    return {
        "id": qid, "title": title, "topic": topic, "prompt": prompt,
        "options": options, "correct": correct, "explanation": explanation,
        "memory": memory, "source": source, "difficulty": difficulty,
        "confusion": confusion, "type": "multiple",
    }


def ordering(qid, title, topic, prompt, items, explanation, memory, source=SOURCE_FUENTES,
             difficulty="media", confusion="No ordenes por importancia, sino por la secuencia histórica o expositiva solicitada."):
    return {
        "id": qid, "title": title, "topic": topic, "prompt": prompt,
        "items": items, "explanation": explanation, "memory": memory,
        "source": source, "difficulty": difficulty, "confusion": confusion,
        "type": "ordering",
    }


def matching(qid, title, topic, prompt, pairs, explanation, memory, source=SOURCE_FUENTES,
             difficulty="media", confusion="Relaciona cada concepto con su rasgo distintivo, no solo con palabras parecidas."):
    return {
        "id": qid, "title": title, "topic": topic, "prompt": prompt,
        "pairs": pairs, "explanation": explanation, "memory": memory,
        "source": source, "difficulty": difficulty, "confusion": confusion,
        "type": "matching",
    }


QUESTIONS = [
    ordering(
        "DER101-P126", "Estadios de evolución de las costumbres", "Costumbre jurídica",
        "Ordene los tres estadios de evolución de las costumbres descritos en el compendio.",
        [
            "Predominan inicialmente los motivos religiosos y luego los morales",
            "Se organizan las relaciones sociales y comienzan a diferenciarse los motivos moral y religioso",
            "Las costumbres, el Derecho y la moralidad se distinguen completamente",
        ],
        "El compendio presenta una evolución desde la influencia religiosa y moral, pasando por la organización social, hasta la separación entre costumbre, Derecho y moralidad.",
        "Primero motivos; después organización; finalmente diferenciación.",
    ),
    single(
        "DER101-P127", "Heterogénesis de los fines", "Costumbre jurídica",
        "Según la ley de heterogénesis de los fines, ¿qué ocurre con las costumbres?",
        [
            ("A", "Desaparecen cuando termina el motivo religioso que las originó"),
            ("B", "Sobreviven a sus motivos iniciales y producen efectos cada vez menos relacionados con ellos"),
            ("C", "Solo se conservan cuando una ley escrita las incorpora"),
            ("D", "Mantienen siempre exactamente el mismo propósito"),
        ], "B",
        "La heterogénesis explica que una costumbre puede continuar aun cuando desaparece o cambia el motivo que la originó.",
        "La costumbre puede sobrevivir a su finalidad original.",
    ),
    single(
        "DER101-P128", "Costumbre según Aftalión", "Costumbre jurídica",
        "¿Cómo define Aftalión la costumbre jurídica?",
        [
            ("A", "Como una repetición de conducta en interferencia intersubjetiva que adquiere carácter obligatorio"),
            ("B", "Como toda sentencia dictada por un tribunal superior"),
            ("C", "Como una declaración escrita del órgano legislativo"),
            ("D", "Como una práctica individual que no produce efectos sociales"),
        ], "A",
        "Para Aftalión, la repetición de la conducta se vuelve jurídicamente relevante cuando se le añade la idea de obligatoriedad.",
        "Aftalión: repetición más obligatoriedad.",
    ),
    single(
        "DER101-P129", "Costumbre según Latorre", "Costumbre jurídica",
        "Según Latorre, además de un uso repetido y antiguo, ¿qué se necesita para hablar de costumbre jurídica?",
        [
            ("A", "La autorización previa de un juez"),
            ("B", "La publicación del uso en el Registro Oficial"),
            ("C", "La conciencia de que el uso expresa una norma obligatoria para todos"),
            ("D", "La aceptación exclusiva de quienes iniciaron la práctica"),
        ], "C",
        "El simple uso no basta. Debe existir la convicción de que la práctica expresa una regla obligatoria.",
        "Latorre: uso más conciencia de obligatoriedad.",
    ),
    single(
        "DER101-P130", "Origen consuetudinario del Derecho", "Costumbre jurídica",
        "De acuerdo con el compendio, el Derecho surge históricamente como una diferenciación de:",
        [
            ("A", "Las costumbres"),
            ("B", "Los contratos mercantiles"),
            ("C", "Las decisiones administrativas"),
            ("D", "Los reglamentos legislativos"),
        ], "A",
        "El texto señala que las costumbres originan el Derecho y que este se diferencia progresivamente de ellas.",
        "La costumbre es el tronco histórico del Derecho.",
    ),
    single(
        "DER101-P131", "Fuente más antigua del Derecho", "Fuentes del Derecho",
        "¿Cuál es reconocida como la fuente más antigua del Derecho?",
        [
            ("A", "La doctrina"),
            ("B", "La jurisprudencia constitucional"),
            ("C", "La costumbre jurídica"),
            ("D", "El reglamento administrativo"),
        ], "C",
        "La costumbre jurídica antecede a las grandes codificaciones y fue una forma temprana de creación del Derecho.",
        "Antes de la ley escrita estuvo la costumbre.",
    ),
    single(
        "DER101-P132", "Leyes de evolución de las costumbres", "Costumbre jurídica",
        "¿Cuántas leyes señala el compendio para explicar la evolución de las costumbres?",
        [
            ("A", "Una"),
            ("B", "Dos"),
            ("C", "Tres"),
            ("D", "Cuatro"),
        ], "B",
        "El texto anuncia expresamente dos leyes que rigen la evolución de las costumbres.",
        "Evolución de las costumbres: dos leyes.",
        difficulty="básica",
    ),
    single(
        "DER101-P133", "Mito y costumbre", "Costumbre jurídica",
        "¿Cómo describe el compendio la influencia del mito sobre las costumbres?",
        [
            ("A", "Secundaria frente a la ley escrita"),
            ("B", "Preponderante, como la del sentimiento sobre la acción individual"),
            ("C", "Inexistente desde el primer estadio"),
            ("D", "Limitada únicamente a las normas penales"),
        ], "B",
        "El texto atribuye al mito una influencia preponderante en la formación temprana de las costumbres.",
        "En los primeros estadios, mito y sentimiento tienen gran influencia.",
    ),
    matching(
        "DER101-P134", "Ley en sentido formal y material", "La ley",
        "Relacione cada clase de ley con la descripción que le corresponde.",
        [
            ("Ley en sentido formal", "Acto emanado del órgano legislativo, independientemente de su contenido normativo"),
            ("Ley en sentido material", "Acto que contiene normas generales y abstractas, sin importar el órgano que lo emite"),
            ("Ley en sentido formal y material", "Acto del órgano legislativo que además está provisto de contenido normativo"),
        ],
        "La clasificación distingue el órgano que produce el acto —sentido formal— de su contenido general y abstracto —sentido material—.",
        "Formal mira al órgano; material mira al contenido.",
    ),
    single(
        "DER101-P135", "Definición legal de ley", "La ley",
        "Según el Código Civil ecuatoriano citado en el material, la ley es:",
        [
            ("A", "Una recomendación de los tribunales para orientar a la ciudadanía"),
            ("B", "Una declaración de la voluntad soberana que, manifestada en la forma prescrita por la Constitución, manda, prohíbe o permite"),
            ("C", "Toda práctica social repetida durante un periodo prolongado"),
            ("D", "Un acuerdo privado celebrado entre dos o más personas"),
        ], "B",
        "La definición legal destaca la voluntad soberana, la forma constitucional y sus tres posibles efectos: mandar, prohibir o permitir.",
        "La ley manda, prohíbe o permite.",
    ),
    single(
        "DER101-P136", "Aprobación de la ley", "La ley",
        "¿Qué caracteriza a la ley como acto normativo?",
        [
            ("A", "Es aprobada por el órgano legislativo competente mediante el procedimiento constitucional"),
            ("B", "Es emitida libremente por cualquier servidor público"),
            ("C", "Surge únicamente de la repetición de sentencias"),
            ("D", "Depende de la aceptación individual de cada ciudadano"),
        ], "A",
        "La ley requiere órgano competente y observancia del procedimiento de creación previsto constitucionalmente.",
        "Ley: órgano legislativo competente más procedimiento constitucional.",
    ),
    single(
        "DER101-P137", "Fuente del Derecho", "Fuentes del Derecho",
        "En el sentido explicado por el compendio, una fuente del Derecho es:",
        [
            ("A", "Cada acto o documento que produce normas, independientemente de su régimen jurídico"),
            ("B", "Solo una ley aprobada por la Asamblea Nacional"),
            ("C", "Cualquier opinión personal sobre la justicia"),
            ("D", "Únicamente una sentencia de la Corte Constitucional"),
        ], "A",
        "El concepto de fuente se refiere al origen productor de normas y no se limita a un único órgano o tipo documental.",
        "Fuente es aquello de donde nace una norma.",
    ),
    matching(
        "DER101-P138", "Etimología de jurisprudencia", "Jurisprudencia",
        "Relacione cada término con su significado.",
        [
            ("Ius", "Derecho"),
            ("Prudentia", "Sabiduría o conocimiento"),
            ("Iurisprudentia", "Sabiduría del Derecho"),
        ],
        "La voz latina iurisprudentia se forma con ius y prudentia, de donde proviene su significado etimológico.",
        "Ius más prudentia: sabiduría del Derecho.",
    ),
    single(
        "DER101-P139", "Reconocimiento del Derecho judicial", "Jurisprudencia",
        "¿Cuándo adquiere reconocimiento el Derecho judicial según el compendio?",
        [
            ("A", "Cuando se publica una sola sentencia"),
            ("B", "Ante la repetición constante de sentencias que revela un criterio general"),
            ("C", "Cuando una parte acepta voluntariamente el fallo"),
            ("D", "Cuando la doctrina sustituye completamente a la ley"),
        ], "B",
        "No basta una decisión aislada: la repetición constante, uniforme y coherente permite reconocer una pauta jurisprudencial.",
        "Jurisprudencia implica repetición y criterio constante.",
    ),
    single(
        "DER101-P140", "Importancia de la jurisprudencia judicial", "Jurisprudencia",
        "¿En qué radica la importancia de la jurisprudencia judicial?",
        [
            ("A", "En reemplazar todas las leyes vigentes"),
            ("B", "En dictar sentencias para casos concretos y desarrollar criterios de aplicación"),
            ("C", "En aprobar reglamentos administrativos"),
            ("D", "En recopilar exclusivamente opiniones académicas"),
        ], "B",
        "La jurisprudencia se forma mediante la solución de casos concretos y la consolidación de criterios para interpretar y aplicar el Derecho.",
        "La jurisprudencia lleva la norma al caso concreto.",
    ),
    ordering(
        "DER101-P141", "Desarrollo histórico de la doctrina jurídica", "Doctrina jurídica",
        "Ordene los hitos del desarrollo de la doctrina jurídica mencionados en el compendio.",
        [
            "Desarrollo de la doctrina jurídica romana desde el siglo II antes de Cristo",
            "Alto nivel de sofisticación durante el siglo III después de Cristo",
            "Redescubrimiento y estudio renovado en la Bolonia del siglo XI",
            "Consideración de la doctrina jurídica como disciplina científica durante la Edad Media",
        ],
        "El compendio presenta una secuencia que parte de Roma, continúa con su sofisticación, pasa por Bolonia y llega a su consideración científica medieval.",
        "Roma, sofisticación, Bolonia y ciencia medieval.",
    ),
    single(
        "DER101-P142", "Significado de doctrina", "Doctrina jurídica",
        "¿Qué significa doctrina en el ámbito del Derecho?",
        [
            ("A", "La formulación y desarrollo de enunciados teóricos para explicar, mantener o modificar una realidad"),
            ("B", "La repetición automática de decisiones judiciales"),
            ("C", "La sanción impuesta por incumplir una ley"),
            ("D", "El conjunto exclusivo de reglamentos del Ejecutivo"),
        ], "A",
        "La doctrina desarrolla explicaciones teóricas rigurosas sobre la realidad jurídica y orienta su comprensión o modificación.",
        "Doctrina es elaboración teórica sobre el Derecho.",
    ),
    single(
        "DER101-P143", "Inicio de la doctrina jurídica romana", "Doctrina jurídica",
        "¿Desde qué época se desarrolló la doctrina jurídica romana según el compendio?",
        [
            ("A", "Desde el siglo II antes de Cristo"),
            ("B", "Desde el siglo XI después de Cristo"),
            ("C", "Desde el siglo XIX"),
            ("D", "Desde el siglo III antes de Cristo"),
        ], "A",
        "El material sitúa el inicio de su desarrollo en el siglo II antes de Cristo.",
        "Doctrina romana: siglo II a. C.",
        difficulty="básica",
    ),
    single(
        "DER101-P144", "Doctrina durante la Edad Media", "Doctrina jurídica",
        "¿Cómo era considerada la doctrina jurídica durante la Edad Media?",
        [
            ("A", "Como una práctica sin valor académico"),
            ("B", "Como una disciplina científica"),
            ("C", "Como una costumbre exclusivamente religiosa"),
            ("D", "Como una actividad reservada al poder ejecutivo"),
        ], "B",
        "Durante la Edad Media, la interpretación autorizada otorgaba a la doctrina jurídica estatus de disciplina científica.",
        "En la Edad Media, la doctrina se consideraba ciencia.",
    ),
    matching(
        "DER101-P145", "Características de la ley", "La ley",
        "Relacione cada característica de la ley con su explicación.",
        [
            ("Generalidad", "Se aplica a todas las personas que se encuentran en las condiciones previstas"),
            ("Abstracción", "Regula categorías de casos no individualizados de antemano"),
            ("Impersonalidad", "No se crea para una persona determinada"),
            ("Permanencia", "Conserva vigencia hasta que sea modificada o derogada"),
        ],
        "Estas características permiten que la ley opere de manera general y estable, sin dirigirse a una persona o caso individual.",
        "General: personas; abstracta: casos; impersonal: sin nombre; permanente: hasta su cambio.",
    ),
    multiple(
        "DER101-P146", "Rasgos de las leyes", "La ley",
        "Seleccione todas las afirmaciones correctas sobre las características de las leyes.",
        [
            ("A", "Son obligatorias incluso cuando una persona no está de acuerdo con ellas"),
            ("B", "Se crean normalmente para una persona identificada por su nombre"),
            ("C", "Son abstractas porque contemplan categorías de casos no particularizados"),
            ("D", "Son impersonales porque no se dirigen a un individuo determinado"),
        ], ["A", "C", "D"],
        "La obligatoriedad, abstracción e impersonalidad son rasgos de la ley. Dirigirse a una persona concreta contradice su impersonalidad.",
        "La ley obliga y regula casos generales, no personas nombradas.",
    ),
    single(
        "DER101-P147", "Leyes imperativas", "Clasificación de la ley",
        "¿Qué son las leyes imperativas?",
        [
            ("A", "Normas cuyo cumplimiento es obligatorio"),
            ("B", "Consejos que pueden ignorarse libremente"),
            ("C", "Reglas aplicables solo si las partes las aceptan después"),
            ("D", "Opiniones académicas sin fuerza normativa"),
        ], "A",
        "Las leyes imperativas imponen una conducta obligatoria y no quedan a libre disposición de sus destinatarios.",
        "Imperativa significa cumplimiento obligatorio.",
    ),
    single(
        "DER101-P148", "Leyes prohibitivas", "Clasificación de la ley",
        "¿Qué función cumplen las leyes prohibitivas?",
        [
            ("A", "Autorizar cualquier conducta no escrita"),
            ("B", "Impedir la realización de determinados actos jurídicos"),
            ("C", "Explicar el significado histórico de una costumbre"),
            ("D", "Recomendar soluciones sin imponerlas"),
        ], "B",
        "La norma prohibitiva impide realizar la conducta o el acto señalado por el ordenamiento.",
        "Prohibitiva: establece lo que no debe hacerse.",
    ),
    single(
        "DER101-P149", "Concepto de antinomia", "Antinomias jurídicas",
        "¿Qué es una antinomia jurídica?",
        [
            ("A", "La ausencia total de una norma aplicable a un caso"),
            ("B", "La incompatibilidad entre normas que atribuyen consecuencias jurídicas contradictorias a un mismo supuesto"),
            ("C", "La coincidencia de dos normas con idéntico contenido"),
            ("D", "La pérdida de vigencia de una norma por falta de uso"),
        ], "B",
        "Existe antinomia cuando dos normas aplicables entran en contradicción y no pueden ejecutarse simultáneamente para el mismo supuesto.",
        "Antinomia es conflicto entre normas; laguna es ausencia de norma.",
        source=SOURCE_ORDEN,
    ),
    single(
        "DER101-P150", "Jerarquía ante conflicto normativo", "Jerarquía normativa",
        "Según el artículo 425 de la Constitución citado en el compendio, ¿cómo se resuelve un conflicto entre normas de distinta jerarquía?",
        [
            ("A", "Aplicando la norma jerárquicamente superior"),
            ("B", "Aplicando siempre la norma más antigua"),
            ("C", "Eligiendo la norma de menor rango"),
            ("D", "Dejando ambas normas sin efecto automáticamente"),
        ], "A",
        "El criterio jerárquico exige aplicar la norma superior, considerando también el principio de competencia cuando corresponda.",
        "En conflicto de jerarquía, prevalece la norma superior.",
        source=SOURCE_ORDEN,
    ),
    single(
        "DER101-P151", "Generalidad de la ley", "Características de la ley",
        "Una ley aplicable a todas las personas que reúnen las condiciones previstas manifiesta la característica de:",
        [
            ("A", "Generalidad"),
            ("B", "Retroactividad"),
            ("C", "Individualidad"),
            ("D", "Temporalidad"),
        ], "A",
        "La generalidad significa que la norma comprende a todos quienes se encuentren dentro del supuesto regulado.",
        "Generalidad: todos los que cumplen el supuesto.",
    ),
    matching(
        "DER101-P152", "Funciones de las fuentes del Derecho", "Fuentes del Derecho",
        "Relacione cada fuente o actividad jurídica con su función principal.",
        [
            ("Ley", "Acto normativo aprobado mediante el procedimiento legislativo correspondiente"),
            ("Costumbre jurídica", "Práctica reiterada acompañada por conciencia de obligatoriedad"),
            ("Jurisprudencia", "Interpretación y aplicación constante del Derecho mediante decisiones judiciales"),
            ("Doctrina", "Elaboración teórica que explica y orienta el conocimiento jurídico"),
        ],
        "Cada fuente cumple una función diferente: producción legislativa, práctica obligatoria, criterio judicial o explicación académica.",
        "Ley legisla; costumbre reitera; jurisprudencia interpreta; doctrina explica.",
    ),
    matching(
        "DER101-P153", "Autores y conceptos", "Fuentes del Derecho",
        "Relacione cada referencia doctrinaria con la idea correspondiente.",
        [
            ("Aftalión", "Costumbre como repetición de conducta en interferencia intersubjetiva"),
            ("Latorre", "El uso necesita conciencia de obligatoriedad para ser costumbre jurídica"),
            ("Fernández", "Jurisprudencia como interpretación correcta y válida de la ley"),
            ("López", "Distinción entre ley en sentido formal y ley en sentido material"),
        ],
        "El compendio atribuye a cada autor una explicación específica sobre costumbre, jurisprudencia o ley.",
        "Aftalión y Latorre: costumbre; Fernández: jurisprudencia; López: ley.",
    ),
    matching(
        "DER101-P154", "Mandar, prohibir y permitir", "La ley",
        "Relacione cada efecto de la ley con el tipo de conducta que expresa.",
        [
            ("Mandar", "Exigir la realización de una conducta"),
            ("Prohibir", "Impedir la realización de una conducta"),
            ("Permitir", "Autorizar una conducta dentro del ordenamiento"),
        ],
        "La definición legal resume los efectos de la ley en tres verbos: mandar, prohibir y permitir.",
        "Mandar exige; prohibir impide; permitir autoriza.",
    ),
    single(
        "DER101-P155", "Libertad y buen gobierno", "Fines y principios del Derecho",
        "La idea desarrollada a partir de las nociones de buen gobierno identificadas por los griegos corresponde al principio de:",
        [
            ("A", "Libertad"),
            ("B", "Coercibilidad"),
            ("C", "Jerarquía normativa"),
            ("D", "Irretroactividad"),
        ], "A",
        "El compendio relaciona el desarrollo histórico de las nociones de buen gobierno con la idea de libertad.",
        "Buen gobierno, en este apartado, conduce a la libertad.",
        source=SOURCE_FINES,
    ),
    single(
        "DER101-P156", "Evolución del Derecho", "Naturaleza del Derecho",
        "El hecho de que la sociedad cambie y las normas jurídicas se adapten a esos cambios expresa:",
        [
            ("A", "La evolución del Derecho"),
            ("B", "La desaparición del orden jurídico"),
            ("C", "La inmovilidad de la legislación"),
            ("D", "La autonomía de la norma moral"),
        ], "A",
        "El Derecho no es fijo: cambia a lo largo del tiempo para responder a nuevas realidades sociales.",
        "Si cambia la sociedad y cambia la norma, existe evolución del Derecho.",
        source=SOURCE_FINES,
    ),
    single(
        "DER101-P157", "Finalidad de la justicia social", "Justicia social",
        "¿Cuál es la finalidad inmediata de la justicia social según el compendio?",
        [
            ("A", "Concentrar los bienes y servicios en un solo grupo"),
            ("B", "Lograr una distribución equitativa y un trato humano en las relaciones sociales"),
            ("C", "Sustituir todas las normas jurídicas por normas morales"),
            ("D", "Eliminar las obligaciones del Estado"),
        ], "B",
        "La justicia social busca una distribución equitativa y condiciones humanas que favorezcan el bienestar colectivo.",
        "Justicia social: distribución equitativa y trato humano.",
        source=SOURCE_FINES,
    ),
    single(
        "DER101-P158", "Hecho jurídico en la relación jurídica", "Relación jurídica",
        "Dentro de los elementos de la relación jurídica, el hecho jurídico se entiende como:",
        [
            ("A", "La hipótesis o supuesto contemplado en la norma"),
            ("B", "La sanción que siempre aplica un juez penal"),
            ("C", "La opinión personal del sujeto activo"),
            ("D", "El documento que contiene exclusivamente doctrina"),
        ], "A",
        "El compendio presenta el hecho jurídico como el supuesto previsto por la norma cuya realización produce consecuencias jurídicas.",
        "Hecho jurídico: supuesto previsto; al cumplirse, nacen consecuencias.",
        source=SOURCE_RELACION,
    ),
    multiple(
        "DER101-P159", "Elementos de la costumbre jurídica", "Costumbre jurídica",
        "Seleccione todas las afirmaciones compatibles con la costumbre jurídica descrita en el compendio.",
        [
            ("A", "Supone una conducta reiterada en el tiempo"),
            ("B", "Requiere conciencia de que el uso expresa una regla obligatoria"),
            ("C", "Solo existe cuando ha sido redactada por el órgano legislativo"),
            ("D", "Puede adquirir relevancia jurídica y formar parte del ordenamiento"),
        ], ["A", "B", "D"],
        "La costumbre combina reiteración y convicción de obligatoriedad, y bajo determinadas condiciones puede convertirse en regla jurídica.",
        "Repetición más obligatoriedad puede producir costumbre jurídica.",
    ),
    multiple(
        "DER101-P160", "Identificación de antinomias", "Antinomias jurídicas",
        "Seleccione todas las afirmaciones correctas sobre las antinomias jurídicas.",
        [
            ("A", "Surgen por contradicción entre normas de un mismo ordenamiento"),
            ("B", "Pueden dificultar o impedir la aplicación simultánea de las normas"),
            ("C", "Siempre se resuelven aplicando la norma de menor jerarquía"),
            ("D", "Un ordenamiento coherente debe procurar reducirlas o eliminarlas"),
        ], ["A", "B", "D"],
        "Las antinomias son contradicciones normativas que afectan la aplicación coherente del Derecho. La norma inferior no prevalece por el solo hecho de ser inferior.",
        "Antinomia: contradicción que exige un criterio jurídico de solución.",
        source=SOURCE_ORDEN,
    ),
]


def option_text(options, letter):
    return next(text for current, text in options if current == letter)


def render_question(question):
    lines = [
        f"## {question['id']} — {question['title']}",
        "- Asignatura: DER101",
        f"- Tema: {question['topic']}",
        f"- Dificultad: {question['difficulty']}",
        "- Estado: revisada",
        f"- Fuente: {question['source']}",
        "- Procedencia: generated_from_compendium",
        "",
        "### Enunciado",
        question["prompt"],
        "",
        "### Alternativas",
    ]

    if question["type"] in {"single", "multiple"}:
        lines.extend(f"- {letter}. {text}" for letter, text in question["options"])
    elif question["type"] == "matching":
        lines.append("- Conceptos y descripciones se presentan en orden aleatorio durante el intento.")
    else:
        lines.append("- Los elementos se presentan en orden aleatorio durante el intento.")

    lines.extend(["", "### Respuesta correcta"])
    if question["type"] == "single":
        correct = question["correct"][0]
        lines.append(f"{correct}. {option_text(question['options'], correct)}")
    elif question["type"] == "multiple":
        letters = question["correct"]
        prefix = ", ".join(letters[:-1]) + f" y {letters[-1]}"
        texts = "; ".join(f"{letter}. {option_text(question['options'], letter)}" for letter in letters)
        lines.append(f"{prefix}. {texts}")
    elif question["type"] == "ordering":
        lines.append("; ".join(f"{index}. {item}" for index, item in enumerate(question["items"], 1)))
    else:
        lines.append("; ".join(f"{left} → {right}" for left, right in question["pairs"]))

    lines.extend([
        "",
        "### Retroalimentación sencilla",
        question["explanation"],
        "",
        "### Si responde incorrectamente",
        f"Revisa la idea central: {question['memory']}",
        "",
        "### Consejo opcional",
        question["memory"],
        "",
        "### Explicación",
        question["explanation"],
        "",
        "### Clave para recordar",
        question["memory"],
        "",
        "### Confusión común",
        question["confusion"],
    ])

    if question["type"] in {"single", "multiple"}:
        lines.extend(["", "### Por qué las otras opciones no corresponden"])
        for letter, text in question["options"]:
            if letter not in question["correct"]:
                lines.append(
                    f"- {letter}. «{text}» no responde al concepto o dato específico "
                    "confirmado en el compendio."
                )

    lines.extend(["", "---", ""])
    return "\n".join(lines)


def main():
    assert len(QUESTIONS) == 35
    assert [question["id"] for question in QUESTIONS] == [
        f"DER101-P{number:03d}" for number in range(126, 161)
    ]
    header = (
        "# Preguntas reconstruidas de exámenes anteriores — DER101\n\n"
        "Tanda reconstruida el 23 de julio de 2026 a partir de un banco complementario "
        "atribuido a exámenes anteriores. Los enunciados, alternativas y respuestas fueron "
        "corregidos y contrastados con los compendios disponibles. No se copiaron los errores "
        "de OCR ni se incorporaron preguntas sin contexto verificable.\n\n---\n\n"
    )
    OUTPUT.write_text(header + "".join(render_question(question) for question in QUESTIONS), encoding="utf-8")
    print(f"{OUTPUT} — {len(QUESTIONS)} preguntas reconstruidas")


if __name__ == "__main__":
    main()
