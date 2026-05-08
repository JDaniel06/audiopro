"""
Comando para cargar datos de ejemplo de productos de audio.
Uso: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from apps.products.models import Category, Product


CATEGORIES = [
    {"name": "Mezcladores", "slug": "mezcladores", "description": "Consolas y mezcladores de audio"},
    {"name": "Micrófonos", "slug": "microfonos", "description": "Micrófonos profesionales y de estudio"},
    {"name": "Monitores", "slug": "monitores", "description": "Monitores de estudio y altavoces"},
    {"name": "Interfaces de Audio", "slug": "interfaces-audio", "description": "Interfaces de audio USB y Thunderbolt"},
    {"name": "Amplificadores", "slug": "amplificadores", "description": "Amplificadores de potencia y de guitarra"},
    {"name": "Procesadores", "slug": "procesadores", "description": "Ecualizadores, compresores y efectos"},
]

PRODUCTS = [
    {
        "name": "MG10XU Mezclador 10 Canales",
        "slug": "yamaha-mg10xu",
        "brand": "Yamaha",
        "model_number": "MG10XU",
        "category_slug": "mezcladores",
        "description": "Mezclador analógico de 10 canales con efectos SPX integrados y conectividad USB. Ideal para presentaciones en vivo y grabación.",
        "specifications": {
            "Canales": "10",
            "Buses": "2",
            "Efectos": "SPX integrado",
            "USB": "Sí, 2 canales",
            "Phantom Power": "+48V",
            "Dimensiones": "309 x 67 x 256 mm",
        },
        "price": "349.99",
        "stock": 15,
        "featured": True,
    },
    {
        "name": "SM58 Micrófono Vocal",
        "slug": "shure-sm58",
        "brand": "Shure",
        "model_number": "SM58",
        "category_slug": "microfonos",
        "description": "El micrófono vocal dinámico más popular del mundo. Respuesta de frecuencia contorneada para voz, con filtro de viento y pop integrado.",
        "specifications": {
            "Tipo": "Dinámico",
            "Patrón polar": "Cardioide",
            "Respuesta de frecuencia": "50 Hz - 15 kHz",
            "Impedancia": "300 Ω",
            "Conector": "XLR",
        },
        "price": "99.00",
        "stock": 30,
        "featured": True,
    },
    {
        "name": "HS8 Monitor de Estudio",
        "slug": "yamaha-hs8",
        "brand": "Yamaha",
        "model_number": "HS8",
        "category_slug": "monitores",
        "description": "Monitor de campo cercano de 8 pulgadas con woofer de 8\" y tweeter de 1\". Respuesta plana para mezclas precisas.",
        "specifications": {
            "Woofer": "8 pulgadas",
            "Tweeter": "1 pulgada",
            "Potencia LF": "75W",
            "Potencia HF": "45W",
            "Respuesta de frecuencia": "47 Hz - 24 kHz",
            "Entradas": "XLR + TRS",
        },
        "price": "399.00",
        "stock": 8,
        "featured": True,
    },
    {
        "name": "Scarlett 2i2 Interfaz de Audio",
        "slug": "focusrite-scarlett-2i2",
        "brand": "Focusrite",
        "model_number": "Scarlett 2i2 4th Gen",
        "category_slug": "interfaces-audio",
        "description": "Interfaz de audio USB de 2 entradas y 2 salidas. Preamplificadores de alta calidad con Air Mode para sonido brillante.",
        "specifications": {
            "Entradas": "2 (XLR/TRS combo)",
            "Salidas": "2 (TRS)",
            "Resolución": "24-bit / 192kHz",
            "Conexión": "USB-C",
            "Phantom Power": "+48V",
            "Latencia": "< 2ms",
        },
        "price": "179.99",
        "stock": 20,
        "featured": True,
    },
    {
        "name": "C414 XLII Micrófono de Condensador",
        "slug": "akg-c414-xlii",
        "brand": "AKG",
        "model_number": "C414 XLII",
        "category_slug": "microfonos",
        "description": "Micrófono de condensador de diafragma grande con 9 patrones polares seleccionables. Referencia en estudios profesionales.",
        "specifications": {
            "Tipo": "Condensador",
            "Patrones polares": "9 seleccionables",
            "Respuesta de frecuencia": "20 Hz - 20 kHz",
            "Rango dinámico": "134 dB",
            "Phantom Power": "+48V requerido",
        },
        "price": "699.00",
        "stock": 5,
        "featured": False,
    },
    {
        "name": "QSC K12.2 Altavoz Activo",
        "slug": "qsc-k12-2",
        "brand": "QSC",
        "model_number": "K12.2",
        "category_slug": "monitores",
        "description": "Altavoz activo de 12 pulgadas con 2000W de potencia. DSP integrado con presets para diferentes aplicaciones.",
        "specifications": {
            "Woofer": "12 pulgadas",
            "Potencia": "2000W",
            "Respuesta de frecuencia": "45 Hz - 20 kHz",
            "SPL máximo": "132 dB",
            "Entradas": "XLR + TRS",
            "Peso": "16.4 kg",
        },
        "price": "849.00",
        "stock": 6,
        "featured": False,
    },
    {
        "name": "DBX 166XS Compresor/Gate",
        "slug": "dbx-166xs",
        "brand": "DBX",
        "model_number": "166XS",
        "category_slug": "procesadores",
        "description": "Compresor/limitador/gate de 2 canales con OverEasy y control de ganancia automático.",
        "specifications": {
            "Canales": "2",
            "Ratio": "1:1 a infinito",
            "Attack": "0.5ms - 200ms",
            "Release": "50ms - 3s",
            "Formato": "1U rack",
        },
        "price": "199.00",
        "stock": 10,
        "featured": False,
    },
    {
        "name": "Crown XTi 2002 Amplificador",
        "slug": "crown-xti-2002",
        "brand": "Crown",
        "model_number": "XTi 2002",
        "category_slug": "amplificadores",
        "description": "Amplificador de potencia de 2 canales con DSP integrado. 800W por canal a 4 ohms.",
        "specifications": {
            "Potencia (4Ω)": "800W x 2",
            "Potencia (8Ω)": "500W x 2",
            "Respuesta de frecuencia": "20 Hz - 20 kHz",
            "THD": "< 0.5%",
            "Formato": "2U rack",
            "Peso": "8.6 kg",
        },
        "price": "599.00",
        "stock": 4,
        "featured": False,
    },
]


class Command(BaseCommand):
    help = 'Carga datos de ejemplo de productos de audio profesional'

    def handle(self, *args, **options):
        self.stdout.write("Cargando categorías...")
        cat_map = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data["slug"],
                defaults=cat_data
            )
            cat_map[cat.slug] = cat
            status = "creada" if created else "ya existe"
            self.stdout.write(f"  Categoría '{cat.name}' {status}.")

        self.stdout.write("\nCargando productos...")
        for prod_data in PRODUCTS:
            cat_slug = prod_data.pop("category_slug")
            category = cat_map.get(cat_slug)
            prod, created = Product.objects.get_or_create(
                slug=prod_data["slug"],
                defaults={**prod_data, "category": category}
            )
            status = "creado" if created else "ya existe"
            self.stdout.write(f"  Producto '{prod.name}' {status}.")

        self.stdout.write(self.style.SUCCESS("\n✅ Datos de ejemplo cargados correctamente."))
