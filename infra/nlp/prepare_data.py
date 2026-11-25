#!/usr/bin/env python3
"""Genera y valida los datasets de prueba para HW8 (Text Analytics + CLU Restaurante)."""
import json
from pathlib import Path

OUT_DIR = Path(__file__).parent / "data"


def utf16_span(text: str, substr: str) -> tuple[int, int]:
    """Devuelve (offset, length) en unidades UTF-16 para una subcadena."""
    idx = text.index(substr)
    offset = len(text[:idx].encode("utf-16-le")) // 2
    length = len(substr.encode("utf-16-le")) // 2
    return offset, length


def make_utterance(text: str, intent: str, entities: list[tuple[str, str]]) -> dict:
    """Construye una frase etiquetada calculando sus offsets UTF-16."""
    ent_objs = []
    for category, substr in entities:
        offset, length = utf16_span(text, substr)
        ent_objs.append({
            "category": category,
            "offset": offset,
            "length": length,
        })
    return {
        "text": text,
        "language": "es",
        "intent": intent,
        "entities": ent_objs,
        "dataset": "Train",
    }


def build_clu_project() -> dict:
    raw = [
        # --- RealizarPedido (12) ---
        ("Quisiera ordenar una pizza familiar de pepperoni para llevar", "RealizarPedido",
         [("Cantidad", "una"), ("Plato", "pizza familiar de pepperoni"), ("TipoServicio", "para llevar")]),
        ("Me envías dos hamburguesas clásicas por delivery", "RealizarPedido",
         [("Cantidad", "dos"), ("Plato", "hamburguesas clásicas"), ("TipoServicio", "delivery")]),
        ("Deseo pedir un lomo saltado y una chicha morada", "RealizarPedido",
         [("Cantidad", "un"), ("Plato", "lomo saltado"), ("Cantidad", "una"), ("Plato", "chicha morada")]),
        ("Voy a llevar tres empanadas de carne y dos gaseosas", "RealizarPedido",
         [("Cantidad", "tres"), ("Plato", "empanadas de carne"), ("Cantidad", "dos"), ("Plato", "gaseosas")]),
        ("Mándame un ceviche mixto a domicilio por favor", "RealizarPedido",
         [("Cantidad", "un"), ("Plato", "ceviche mixto"), ("TipoServicio", "a domicilio")]),
        ("Quiero hacer un pedido de pollo a la brasa para comer en mesa", "RealizarPedido",
         [("Plato", "pollo a la brasa"), ("TipoServicio", "en mesa")]),
        ("Dame 2 pizzas hawaianas grandes para recoger en tienda", "RealizarPedido",
         [("Cantidad", "2"), ("Plato", "pizzas hawaianas grandes"), ("TipoServicio", "para recoger en tienda")]),
        ("Quisiera pedir una causa rellena y un arroz con pollo", "RealizarPedido",
         [("Cantidad", "una"), ("Plato", "causa rellena"), ("Cantidad", "un"), ("Plato", "arroz con pollo")]),
        ("Por favor agrégame una limonada frozen a mi orden", "RealizarPedido",
         [("Cantidad", "una"), ("Plato", "limonada frozen")]),
        ("Necesito pedir cuatro menús ejecutivos para la oficina", "RealizarPedido",
         [("Cantidad", "cuatro"), ("Plato", "menús ejecutivos")]),
        ("Quiero ordenar un tiramisú y un café americano", "RealizarPedido",
         [("Cantidad", "un"), ("Plato", "tiramisú"), ("Cantidad", "un"), ("Plato", "café americano")]),
        ("Me gustaría pedir una ensalada césar sin crutones", "RealizarPedido",
         [("Cantidad", "una"), ("Plato", "ensalada césar")]),

        # --- ConsultarMenu (12) ---
        ("¿Qué platos tienen disponibles en la carta?", "ConsultarMenu", []),
        ("Muéstrame el menú del día por favor", "ConsultarMenu", []),
        ("¿Qué opciones de almuerzo ofrecen hoy?", "ConsultarMenu", []),
        ("Quisiera ver los precios de las pizzas y pastas", "ConsultarMenu",
         [("Plato", "pizzas"), ("Plato", "pastas")]),
        ("¿Tienen platos vegetarianos o sin gluten?", "ConsultarMenu", []),
        ("¿Qué bebidas y postres hay en el restaurante?", "ConsultarMenu",
         [("Plato", "bebidas"), ("Plato", "postres")]),
        ("Pásame la carta de entradas y fondos", "ConsultarMenu", []),
        ("¿Cuánto cuesta el lomo saltado y qué incluye?", "ConsultarMenu",
         [("Plato", "lomo saltado")]),
        ("¿Cuál es la especialidad de la casa hoy?", "ConsultarMenu", []),
        ("Quisiera conocer los combos familiares disponibles", "ConsultarMenu", []),
        ("¿Qué sabores de pizza manejan?", "ConsultarMenu",
         [("Plato", "pizza")]),
        ("Me indicas el menú ejecutivo de esta semana", "ConsultarMenu", []),

        # --- ReservarMesa (10) ---
        ("Quiero reservar una mesa para 4 personas hoy a las 8 pm", "ReservarMesa",
         [("NumPersonas", "4 personas"), ("FechaHora", "hoy a las 8 pm")]),
        ("¿Tienen disponibilidad para reservar mañana a la 1 pm?", "ReservarMesa",
         [("FechaHora", "mañana a la 1 pm")]),
        ("Necesito apartar una mesa para dos personas esta noche", "ReservarMesa",
         [("NumPersonas", "dos personas"), ("FechaHora", "esta noche")]),
        ("Quisiera hacer una reservación el sábado por la noche para 6 personas", "ReservarMesa",
         [("FechaHora", "el sábado por la noche"), ("NumPersonas", "6 personas")]),
        ("Sepárame un espacio en terraza el viernes a las 7 pm", "ReservarMesa",
         [("FechaHora", "el viernes a las 7 pm")]),
        ("¿Puedo reservar mesa para un grupo de 8 personas este domingo?", "ReservarMesa",
         [("NumPersonas", "8 personas"), ("FechaHora", "este domingo")]),
        ("Deseo agendar una cena romántica para 2 personas a las 9 pm", "ReservarMesa",
         [("NumPersonas", "2 personas"), ("FechaHora", "a las 9 pm")]),
        ("Apártame una mesa cerca de la ventana para el almuerzo de mañana", "ReservarMesa",
         [("FechaHora", "mañana")]),
        ("Queremos reservar para 5 personas hoy a mediodía", "ReservarMesa",
         [("NumPersonas", "5 personas"), ("FechaHora", "hoy a mediodía")]),
        ("¿Cómo hago una reserva para el próximo fin de semana?", "ReservarMesa",
         [("FechaHora", "el próximo fin de semana")]),

        # --- ConsultarHorarioUbicacion (10) ---
        ("¿A qué hora abren los domingos?", "ConsultarHorarioUbicacion",
         [("FechaHora", "los domingos")]),
        ("¿Dónde está ubicado el restaurante?", "ConsultarHorarioUbicacion", []),
        ("¿Cuál es su dirección exacta y horario de atención?", "ConsultarHorarioUbicacion", []),
        ("¿Hasta qué hora atienden hoy por la noche?", "ConsultarHorarioUbicacion",
         [("FechaHora", "hoy por la noche")]),
        ("¿Atienden los días feriados?", "ConsultarHorarioUbicacion", []),
        ("¿Tienen local en Miraflores o San Isidro?", "ConsultarHorarioUbicacion", []),
        ("¿A qué hora cierran la cocina entre semana?", "ConsultarHorarioUbicacion", []),
        ("Me compartes la ubicación para llegar al local", "ConsultarHorarioUbicacion", []),
        ("¿Cuál es el horario de delivery?", "ConsultarHorarioUbicacion",
         [("TipoServicio", "delivery")]),
        ("¿Abren temprano para desayunos?", "ConsultarHorarioUbicacion", []),

        # --- CancelarPedido (10) ---
        ("Quiero cancelar mi pedido por favor", "CancelarPedido", []),
        ("Necesito anular la orden de pizza que acabo de hacer", "CancelarPedido",
         [("Plato", "pizza")]),
        ("Por favor cancela el delivery, surgió un inconveniente", "CancelarPedido",
         [("TipoServicio", "delivery")]),
        ("Ya no voy a querer el pedido, deseo anularlo", "CancelarPedido", []),
        ("¿Puedo cancelar mi orden de hamburguesas antes de que salga?", "CancelarPedido",
         [("Plato", "hamburguesas")]),
        ("Anula mi solicitud actual, hice el pedido por error", "CancelarPedido", []),
        ("Quisiera dar de baja la compra que registré hace un momento", "CancelarPedido", []),
        ("Cancela el pedido número 452, gracias", "CancelarPedido", []),
        ("No envíen el lomo saltado, necesito cancelar", "CancelarPedido",
         [("Plato", "lomo saltado")]),
        ("Deseo suspender mi orden para llevar", "CancelarPedido",
         [("TipoServicio", "para llevar")]),

        # --- None (10) ---
        ("¿Cuál es la capital de Francia?", "None", []),
        ("¿Cómo está el clima en Lima hoy?", "None", []),
        ("Necesito ayuda para instalar Python en Fedora", "None", []),
        ("¿A qué hora juega la selección peruana?", "None", []),
        ("Explícame qué es una base de datos relacional", "None", []),
        ("Buenos días, ¿quién ganó el partido de ayer?", "None", []),
        ("¿Cuánto vale el dólar hoy en Perú?", "None", []),
        ("Recomiéndame una película de ciencia ficción", "None", []),
        ("¿Cómo llego al aeropuerto Jorge Chávez?", "None", []),
        ("Cuéntame un chiste corto", "None", []),
    ]

    utterances = [make_utterance(t, i, e) for t, i, e in raw]
    intents = [
        {"category": "RealizarPedido"},
        {"category": "ConsultarMenu"},
        {"category": "ReservarMesa"},
        {"category": "ConsultarHorarioUbicacion"},
        {"category": "CancelarPedido"},
        {"category": "None"},
    ]
    entities = [
        {"category": "Plato"},
        {"category": "Cantidad"},
        {"category": "TipoServicio"},
        {"category": "NumPersonas"},
        {"category": "FechaHora"},
    ]

    return {
        "projectFileVersion": "2022-05-01",
        "stringIndexType": "Utf16CodeUnit",
        "metadata": {
            "projectKind": "Conversation",
            "settings": {"confidenceThreshold": 0.0},
            "projectName": "hw8-restaurante-luis",
            "multilingual": False,
            "description": "Aplicacion CLU (sucesor de LUIS) para atencion de restaurante - HW8 SENATI",
            "language": "es",
        },
        "assets": {
            "projectKind": "Conversation",
            "intents": intents,
            "entities": entities,
            "utterances": utterances,
        },
    }


def build_holdout() -> list[dict]:
    return [
        # Incluye explícitamente los ejemplos del enunciado de la tarea
        {"text": "Quiero pedir una pizza", "true_intent": "RealizarPedido"},
        {"text": "Tráeme dos platos de ceviche para llevar", "true_intent": "RealizarPedido"},
        {"text": "Quisiera ordenar un pollo a la brasa por delivery", "true_intent": "RealizarPedido"},
        {"text": "Me gustaría pedir una chicha morada y tres empanadas", "true_intent": "RealizarPedido"},

        {"text": "¿Cuál es el menú de hoy?", "true_intent": "ConsultarMenu"},
        {"text": "¿Qué bebidas tienen en la carta?", "true_intent": "ConsultarMenu"},
        {"text": "Muéstrame los precios de las hamburguesas", "true_intent": "ConsultarMenu"},

        {"text": "Quiero reservar una mesa para 3 personas mañana a las 8 pm", "true_intent": "ReservarMesa"},
        {"text": "¿Tienen mesa libre hoy por la noche para dos?", "true_intent": "ReservarMesa"},
        {"text": "Necesito apartar una mesa este domingo", "true_intent": "ReservarMesa"},

        {"text": "¿Cuál es la dirección del restaurante?", "true_intent": "ConsultarHorarioUbicacion"},
        {"text": "¿A qué hora abren hoy?", "true_intent": "ConsultarHorarioUbicacion"},
        {"text": "¿Hasta qué hora hacen delivery los sábados?", "true_intent": "ConsultarHorarioUbicacion"},

        {"text": "Quiero cancelar el pedido que acabo de hacer", "true_intent": "CancelarPedido"},
        {"text": "Por favor anulen mi orden de pizza", "true_intent": "CancelarPedido"},
        {"text": "Ya no necesito el delivery, cancelen la compra", "true_intent": "CancelarPedido"},

        {"text": "¿Cuál es la fórmula del agua?", "true_intent": "None"},
        {"text": "¿Quién escribió Don Quijote de la Mancha?", "true_intent": "None"},
    ]


def build_text_analytics_samples() -> list[dict]:
    return [
        {
            "id": "1",
            "text": "Excelente atención en el restaurante El Sabor Peruano en Miraflores, Lima. El lomo saltado estuvo delicioso y la chicha morada muy fresca.",
        },
        {
            "id": "2",
            "text": "La pizza llegó fría después de una hora de espera y el repartidor no encontró la dirección en San Isidro. Muy mala experiencia con el delivery.",
        },
        {
            "id": "3",
            "text": "El menú ejecutivo tiene un precio razonable, aunque las porciones podrían ser un poco más grandes. La atención del mozo fue correcta.",
        },
        {
            "id": "4",
            "text": "El estudiante Diego Val de SENATI desarrolló un asistente virtual con Microsoft Azure AI Language para automatizar pedidos de restaurante.",
        },
        {
            "id": "5",
            "text": "Great food and fast service! The pepperoni pizza and lemonade were awesome.",
        },
        {
            "id": "6",
            "text": "A comida estava maravilhosa e o atendimento foi excelente em São Paulo.",
        },
    ]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clu = build_clu_project()
    holdout = build_holdout()
    ta = build_text_analytics_samples()

    (OUT_DIR / "clu_restaurant_project.json").write_text(
        json.dumps(clu, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "clu_test_holdout.json").write_text(
        json.dumps(holdout, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "text_analytics_samples.json").write_text(
        json.dumps(ta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Generados: {len(clu['assets']['utterances'])} utterances train, "
          f"{len(holdout)} hold-out, {len(ta)} muestras Text Analytics.")


if __name__ == "__main__":
    main()
