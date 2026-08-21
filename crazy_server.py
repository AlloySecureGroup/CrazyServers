#!/usr/bin/env python3
"""
crazy_server.py

A zero-dependency fake HTTP server that emits absurd multilingual Unicode
errors, fake .NET stack traces, and optional ASP.NET-style developer error pages.

This does NOT run .NET and does not expose a real ASP.NET application.
It only generates fictional diagnostics for demos, screenshots, testing, and fun.
"""

from __future__ import annotations

import argparse
import html
import json
import random
import secrets
import socket
import sys
import threading
import time
import unicodedata
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


# ============================================================
# VOCABULARY
# ============================================================

ENGLISH = [
    "banana", "spoon", "microwave", "penguin", "bureaucrat", "toaster",
    "forbidden", "suspicious", "moist", "orb", "cheese", "goblin",
    "algorithm", "tax", "wizard", "pickle", "cabbage", "elevator",
    "lasagna", "sock", "moon", "shrimp", "horse", "keyboard", "void",
    "mayonnaise", "rectangle", "grandmother", "satellite", "mushroom",
    "hamster", "prophecy", "waffle", "pigeon", "basement", "accordion",
    "committee", "dimension", "refrigerator", "beetle", "skeleton",
    "carpet", "mustard", "meatball", "turnip", "molecule", "invoice",
    "cucumber", "nightmare", "pancake", "obelisk", "dentist", "frog",
    "trousers", "recursive", "fermented", "haunted", "interdimensional",
]

FRENCH = [
    "bonjour", "fromage", "grenouille", "baguette", "escargot",
    "papillon", "chapeau", "ordinateur", "pamplemousse", "fantôme",
    "moustache", "croissant", "catastrophe", "chaussette", "cornichon",
    "saucisson", "incroyable", "bizarre", "magnifique", "oiseau",
    "poubelle", "sorcier", "lune", "patate", "truc", "machin",
]

SPANISH = [
    "hola", "queso", "murciélago", "pepino", "fantasma", "calcetín",
    "cucaracha", "patata", "señor", "biblioteca", "sandía", "misterioso",
    "absurdo", "peligroso", "cebolla", "caballo", "cuchara", "luna",
    "payaso", "mapache", "tostadora", "churro", "locura", "berenjena",
]

GERMAN = [
    "Kartoffel", "Käse", "Gurke", "Schmetterling", "Staubsauger",
    "Krankenwagen", "Donaudampfschiff", "Wurst", "Socken", "Mond",
    "Frosch", "Kühlschrank", "Quatsch", "Unsinn", "Zauberer",
    "Schnitzel", "Achtung", "plötzlich", "unglaublich", "Brötchen",
    "Waschmaschine", "Kopfkissen", "Rhabarber", "Katze", "Trompete",
]

ITALIAN = [
    "ciao", "formaggio", "patata", "pipistrello", "fantasma",
    "spaghetti", "ravioli", "polpetta", "cucchiaio", "luna",
    "scarpa", "pinguino", "pomodoro", "misterioso", "ridicolo",
    "assurdo", "fungo", "gatto", "melanzana", "prosciutto",
]

PORTUGUESE = [
    "olá", "queijo", "batata", "fantasma", "morcego", "abacaxi",
    "geladeira", "sapato", "lua", "maluco", "estranho", "pipoca",
    "jacaré", "bigode", "garfo", "feijão", "pombo",
]

RUSSIAN = [
    "привет", "картошка", "сыр", "лягушка", "пингвин", "луна",
    "огурец", "носок", "призрак", "бабушка", "чайник", "кот",
    "странный", "безумие", "волшебник", "табуретка", "арбуз",
    "пельмень", "космос", "блин", "шлёп", "жабка", "гриб",
]

UKRAINIAN = [
    "привіт", "картопля", "сир", "жаба", "місяць", "кіт",
    "огірок", "шкарпетка", "привид", "дивний", "вареник",
    "кавун", "борщ", "паляниця",
]

POLISH = [
    "dzieńdobry", "ziemniak", "ser", "żaba", "księżyc", "skarpetka",
    "duch", "ogórek", "dziwny", "pieróg", "chrząszcz", "grzyb",
    "naleśnik", "czarodziej",
]

JAPANESE = [
    "こんにちは", "じゃがいも", "チーズ", "カエル", "ペンギン",
    "月", "幽霊", "猫", "キノコ", "すごい", "変な", "やばい",
    "バナナ", "ゴリラ", "たこ焼き", "冷蔵庫", "魔法", "混沌",
    "宇宙", "謎", "豆腐", "爆発",
]

CHINESE = [
    "你好", "土豆", "奶酪", "青蛙", "企鹅", "月亮", "幽灵",
    "猫", "蘑菇", "奇怪", "疯狂", "香蕉", "宇宙", "神秘",
    "冰箱", "饺子", "龙", "豆腐", "混沌", "爆炸", "筷子",
]

KOREAN = [
    "안녕", "감자", "치즈", "개구리", "펭귄", "달", "유령",
    "고양이", "버섯", "이상한", "미친", "바나나", "우주",
    "냉장고", "김치", "마법", "혼돈", "폭발",
]

ARABIC = [
    "مرحبا", "بطاطا", "جبن", "ضفدع", "بطريق", "قمر", "شبح",
    "قطة", "فطر", "غريب", "مجنون", "موز", "فضاء", "سحر",
    "ثلاجة", "فوضى", "انفجار", "ياصديقي",
]

HEBREW = [
    "שלום", "תפוחאדמה", "גבינה", "צפרדע", "פינגווין",
    "ירח", "רוח", "חתול", "פטרייה", "מוזר", "בננה",
    "חלל", "קסם", "כאוס",
]

GREEK = [
    "γεια", "πατάτα", "τυρί", "βάτραχος", "πιγκουίνος",
    "φεγγάρι", "φάντασμα", "γάτα", "μανιτάρι", "περίεργο",
    "μπανάνα", "χάος", "μαγεία", "διάστημα",
]

TURKISH = [
    "merhaba", "patates", "peynir", "kurbağa", "penguen",
    "ay", "hayalet", "kedi", "mantar", "garip", "çılgın",
    "muz", "uzay", "büyü", "kaos",
]

DUTCH = [
    "hallo", "aardappel", "kaas", "kikker", "pinguïn", "maan",
    "spook", "kat", "paddenstoel", "vreemd", "banaan",
    "ruimte", "magie", "chaos", "stroopwafel",
]

SWEDISH = [
    "hej", "potatis", "ost", "groda", "pingvin", "måne",
    "spöke", "katt", "svamp", "konstig", "banan", "rymd",
    "magi", "kaos",
]

FINNISH = [
    "hei", "peruna", "juusto", "sammakko", "pingviini", "kuu",
    "aave", "kissa", "sieni", "outo", "banaani", "avaruus",
    "taika", "kaaos",
]

LATIN = [
    "salve", "luna", "caseus", "rana", "phantasma", "feles",
    "fungus", "absurdum", "magia", "chaos", "bananum",
    "imperium", "orbita", "mysterium",
]

HINGLISH = [
    "arre", "bhai", "kya", "aloo", "pagal", "jadoo",
    "chappal", "samose", "chai", "bakwaas", "achha", "jalebi",
]

LANGUAGE_POOLS = [
    ENGLISH, FRENCH, SPANISH, GERMAN, ITALIAN, PORTUGUESE,
    RUSSIAN, UKRAINIAN, POLISH, JAPANESE, CHINESE, KOREAN,
    ARABIC, HEBREW, GREEK, TURKISH, DUTCH, SWEDISH,
    FINNISH, LATIN, HINGLISH,
]

VERBS = [
    "whispered", "screamed", "declared", "evaporated", "ascended",
    "vibrated", "teleported", "accused", "summoned", "consumed",
    "politely threatened", "orbited", "misunderstood", "downloaded",
    "became", "unbecame", "recompiled", "fermented", "moonwalked",
    "levitated", "buffered", "respawned", "glitched", "sneezed at",
    "filed taxes against", "challenged", "encrypted", "misfiled",
]

CONNECTORS = [
    "while", "because", "although", "meanwhile", "therefore",
    "and then", "despite this", "for tax reasons", "at 03:77 PM",
    "under protest", "during the forbidden Tuesday", "without warning",
    "in violation of geometry", "according to the prophecy",
    "for reasons nobody documented", "inside the Wi-Fi",
    "beyond the concept of Tuesday", "during firmware update",
    "after consulting the moon", "as required by international goblin law",
]

WEIRD_ADJECTIVES = [
    "moist", "forbidden", "non-Euclidean", "government-certified",
    "haunted", "recursive", "fermented", "quantum", "sentient",
    "legally ambiguous", "electrically suspicious", "boneless",
    "interdimensional", "ceremonial", "tax-deductible", "unlicensed",
    "subterranean", "cosmically incorrect", "weaponized", "velvet",
    "prehistoric", "mathematically illegal", "Wi-Fi enabled",
    "emotionally spherical", "approximately alive", "JPEG-flavored",
]

EMOJIS = [
    "🫠", "🦆", "🐸", "🧀", "🥔", "🍌", "🪿", "🦐", "🦇",
    "👁️", "👹", "🧌", "🗿", "🌚", "🌝", "🌪️", "🌀", "💥",
    "🔥", "⚠️", "🧿", "🪬", "🛸", "🛰️", "🪐", "🌮", "🥐",
    "🧅", "🍄", "🦑", "🪱", "🐌", "🐙", "🧠", "🫀", "🦷",
    "🧙", "🧚", "🧛", "🤡", "👽", "🤖", "🫧", "🪩", "📡",
]

SYMBOLS = [
    "꧁༺", "༻꧂", "𓂀", "𓆏", "𓅓", "𓃠", "𓀀", "𓁹",
    "☠︎", "☾", "☼", "☿", "♄", "♆", "♁", "⚚", "⚕",
    "⌘", "⌬", "⌁", "⌇", "⌖", "⎈", "⏃", "⟟", "⍜",
    "⍙", "⌰", "⎅", "⟒", "⟊", "⌿", "∴", "∵", "∞",
    "≈", "≠", "∅", "∆", "∇", "∑", "Ω", "Σ", "Ψ", "λ",
    "φ", "Ж", "Ѫ", "҂", "ꙮ", "Ӝ", "※", "〆", "々",
    "ヲ", "ゑ", "ヶ", "〠", "༒", "࿇", "࿊", "࿔", "࿈",
    "᯽", "❂", "✺", "✧", "✦", "⭒", "⛧", "⛥", "⚶",
]

RUNES = list("ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊᛏᛒᛖᛗᛚᛜᛞᛟ")

KAOMOJI = [
    "(╯°□°）╯︵ ┻━┻", "ಠ_ಠ", "༼ つ ◕_◕ ༽つ", "ʕ•ᴥ•ʔ",
    "(ง'̀-'́)ง", "¯\\_(ツ)_/¯", "(☞ﾟヮﾟ)☞", "☜(ﾟヮﾟ☜)",
    "(づ｡◕‿‿◕｡)づ", "༼つಠ益ಠ༽つ", "ᕕ( ᐛ )ᕗ", "ಥ_ಥ",
]

GLITCH_WORDS = [
    "B̵A̷N̸A̶N̵A̷", "V̷O̶I̵D̸", "M̵O̵O̷N̶", "C̸H̴E̷E̸S̶E̵",
    "F̶R̵O̸G̷", "R̸E̷A̵L̴I̴T̶Y̵", "P̷O̷T̵A̷T̴O̴",
]

FAKE_PROTOCOLS = [
    "goblin://localhost:666", "cheese://moon/root", "frog://NULL",
    "banana://etc/reality", "orb://forbidden/sector",
    "udp://grandmother", "ssh://penguin@void", "file:///dev/lasagna",
]

NUMERIC_NONSENSE = [
    "⅞π", "∞²", "-0°C²", "42.000banana", "NaN%", "3⅓ moons",
    "0xDEADBEEF", "0b101010frog", "√pickle", "π³ kilograms",
    "9¾ dimensions", "404 radians", "⅓ of a Tuesday",
]

ZALGO_UP = ["\u030d", "\u030e", "\u0304", "\u0305", "\u033f", "\u0311",
            "\u0306", "\u0310", "\u0352", "\u0357", "\u0351", "\u0307",
            "\u0308", "\u030a", "\u0342", "\u0343", "\u0344", "\u034a"]
ZALGO_MID = ["\u0315", "\u031b", "\u0340", "\u0341", "\u0358", "\u0321",
             "\u0322", "\u0327", "\u0328", "\u0334", "\u0335", "\u0336"]
ZALGO_DOWN = ["\u0316", "\u0317", "\u0318", "\u0319", "\u031c", "\u031d",
              "\u031e", "\u031f", "\u0320", "\u0324", "\u0325", "\u0326",
              "\u0329", "\u032a", "\u032b", "\u032c", "\u0331", "\u0332"]


# ============================================================
# FAKE .NET DATA
# ============================================================

DOTNET_EXCEPTIONS = [
    "System.NullReferenceException",
    "System.InvalidOperationException",
    "System.ArgumentException",
    "System.ArgumentNullException",
    "System.IndexOutOfRangeException",
    "System.OutOfMemoryException",
    "System.IO.IOException",
    "System.IO.FileNotFoundException",
    "System.UnauthorizedAccessException",
    "System.NotSupportedException",
    "System.TimeoutException",
    "System.DivideByZeroException",
    "System.FormatException",
    "System.AggregateException",
    "System.Threading.Tasks.TaskCanceledException",
    "System.Reflection.TargetInvocationException",
    "Microsoft.CSharp.RuntimeBinder.RuntimeBinderException",
    "System.CheeseOverflowException",
    "System.RealityNotFoundException",
    "System.BananaReferenceException",
    "System.GoblinInteropException",
    "System.NonEuclideanGeometryException",
    "System.MoonUnavailableException",
    "System.FrogInitializationException",
    "System.PotatoSerializationException",
    "System.ForbiddenTuesdayException",
    "System.RecursiveGrandmotherException",
    "System.VoidAccessViolationException",
    "System.UnlicensedWizardException",
]

DOTNET_MESSAGES = [
    "Object reference not set to an instance of a potato.",
    "Sequence contains more than one moon.",
    "Collection was modified; reality enumeration may not execute.",
    "Value cannot be null. (Parameter 'cheese')",
    "The given key 'banana' was not present in the universe.",
    "Operation is not valid due to the current state of the frog.",
    "Unable to cast object of type 'System.Penguin' to type 'System.Bureaucrat'.",
    "Input string '𓆏' was not in a correct format.",
    "The operation timed out while waiting for Tuesday.",
    "Cannot access a disposed object. Object name: 'Moon'.",
    "Arithmetic operation resulted in a goblin overflow.",
    "An item with the same key has already been added. Key: Kartoffel",
    "The remote server returned an error: (418) Reality Is A Teapot.",
    "Could not load file or assembly 'Forbidden.Lasagna.dll'.",
    "Attempted to divide the ceremonial frog by zero.",
    "The runtime detected a non-Euclidean dependency cycle.",
    "Expected exactly one grandmother but found NaN.",
    "The cheese mutex has been abandoned.",
    "The universe entered an invalid CLR state.",
    "Cannot await object of type 'System.Mushroom'.",
]

DOTNET_NAMESPACES = [
    "Chaos.Core", "Chaos.Runtime", "Forbidden.Lasagna", "Goblin.Interop",
    "Moon.Services", "Banana.Infrastructure", "Potato.Serialization",
    "FrogWare.Core", "Reality.Engine", "Cheese.Orchestration",
    "NonEuclidean.Geometry", "Grandmother.Cloud", "Penguin.Bureaucracy",
    "Void.Internal",
]

DOTNET_CLASSES = [
    "RealityManager", "PotatoFactory", "MoonController", "GoblinService",
    "CheeseProvider", "BananaRepository", "FrogCompiler",
    "LasagnaMiddleware", "VoidAccessor", "TuesdayScheduler",
    "GrandmotherSerializer", "PenguinWorker", "OrbContext",
    "CabbageDispatcher",
]

DOTNET_METHODS = [
    "ExecuteAsync", "Invoke", "Run", "Initialize", "Serialize",
    "Deserialize", "ConsumeCheese", "ResolveMoon", "ValidateReality",
    "SummonGoblinAsync", "ComputeBanana", "RotateFrog", "ProcessPotato",
    "AwaitTuesday", "OpenForbiddenOrb", "CompileLasagna",
    "DoNotCallThis", "AbsolutelyNormalMethod",
]

DOTNET_PATHS = [
    r"C:\src\ChaosEngine",
    r"C:\Users\Administrator\source\repos\ForbiddenLasagna",
    r"D:\build\agent\_work\13\s",
    r"C:\Reality\Production",
    r"C:\inetpub\wwwroot\GoblinAPI",
    r"Z:\DO_NOT_MOUNT\moon",
]

DOTNET_HRESULTS = [
    "0x80004003", "0x80004005", "0x80131500", "0x80131509",
    "0x80131522", "0xDEADBEEF", "0xB16B00B5", "0xF00DBABE",
]

DOTNET_RUNTIME_FRAMES = [
    "   at System.RuntimeMethodHandle.InvokeMethod(Object target, Void** arguments, Signature sig, Boolean isConstructor)",
    "   at System.Reflection.MethodBaseInvoker.InvokeWithNoArgs(Object obj, BindingFlags invokeAttr)",
    "   at System.Threading.ExecutionContext.RunInternal(ExecutionContext executionContext, ContextCallback callback, Object state)",
    "   at System.Runtime.CompilerServices.TaskAwaiter.ThrowForNonSuccess(Task task)",
    "   at Microsoft.AspNetCore.Mvc.Infrastructure.ActionMethodExecutor.TaskOfIActionResultExecutor.Execute(...)",
    "   at Microsoft.AspNetCore.Mvc.Infrastructure.ControllerActionInvoker.InvokeNextActionFilterAsync()",
    "   at Microsoft.AspNetCore.Routing.EndpointMiddleware.Invoke(HttpContext httpContext)",
    "   at Microsoft.AspNetCore.Diagnostics.DeveloperExceptionPageMiddlewareImpl.Invoke(HttpContext context)",
]


# ============================================================
# GENERATOR HELPERS
# ============================================================

def word() -> str:
    return random.choice(random.choice(LANGUAGE_POOLS))


def language_soup(count: int = 4) -> str:
    return " ".join(word() for _ in range(count))


def emoji_burst(minimum: int = 1, maximum: int = 5) -> str:
    return "".join(random.choices(EMOJIS, k=random.randint(minimum, maximum)))


def symbol_burst(minimum: int = 1, maximum: int = 5) -> str:
    return "".join(random.choices(SYMBOLS, k=random.randint(minimum, maximum)))


def rune_burst(minimum: int = 3, maximum: int = 10) -> str:
    return "".join(random.choices(RUNES, k=random.randint(minimum, maximum)))


def zalgo(text: str, intensity: int = 2) -> str:
    output = []
    for char in text:
        output.append(char)
        if char.isspace():
            continue
        for _ in range(random.randint(0, intensity)):
            output.append(random.choice(ZALGO_UP))
        for _ in range(random.randint(0, intensity)):
            output.append(random.choice(ZALGO_MID))
        for _ in range(random.randint(0, intensity)):
            output.append(random.choice(ZALGO_DOWN))
    return "".join(output)


def weird_quote(text: str) -> str:
    pairs = [
        ("「", "」"), ("『", "』"), ("《", "》"), ("⟦", "⟧"),
        ("༺", "༻"), ("꧁", "꧂"), ("“", "”"), ("⫷", "⫸"),
    ]
    left, right = random.choice(pairs)
    return f"{left}{text}{right}"


def mutate_word(text: str, chaos: int) -> str:
    mutation_count = random.randint(0, max(1, chaos // 3))
    for _ in range(mutation_count):
        mutation = random.choice(["zalgo", "case", "emoji", "symbols", "suffix", "bracket"])
        if mutation == "zalgo":
            text = zalgo(text, max(1, chaos // 4))
        elif mutation == "case":
            text = "".join(
                (c.upper() if random.random() < 0.5 else c.lower()) if c.isalpha() else c
                for c in text
            )
        elif mutation == "emoji":
            text = random.choice(EMOJIS) + text + random.choice(EMOJIS)
        elif mutation == "symbols":
            text = random.choice(SYMBOLS) + text + random.choice(SYMBOLS)
        elif mutation == "suffix":
            text += random.choice([".exe", ".dll", ".jpeg", ".gov", "_FINAL_v37", "™", "⁷", "_NULL"])
        elif mutation == "bracket":
            text = weird_quote(text)
    return text


def generate_sentence(chaos: int = 7) -> str:
    chaos = max(1, min(10, chaos))
    chunks = []
    if random.random() < chaos / 11:
        chunks.append(f"{symbol_burst(2, 5)} {emoji_burst(1, 3)} ")

    clause_count = random.randint(1 + chaos // 3, 2 + chaos // 2)
    for i in range(clause_count):
        if i:
            chunks.append(f" {random.choice([',', ';', '—', '⋯', '※', '∴'])} {random.choice(CONNECTORS)} ")
        subject = mutate_word(random.choice([
            word(),
            random.choice(ENGLISH),
            random.choice(GLITCH_WORDS),
            f"{random.choice(WEIRD_ADJECTIVES)} {word()}",
        ]), chaos)
        obj = mutate_word(random.choice([
            word(),
            f"the {random.choice(WEIRD_ADJECTIVES)} {word()}",
            f"{random.choice(NUMERIC_NONSENSE)} of {word()}",
            random.choice(FAKE_PROTOCOLS),
            weird_quote(language_soup(random.randint(2, 5))),
        ]), max(1, chaos - 2))
        chunks.append(f"{subject} {random.choice(VERBS)} {obj}")

        if random.random() < chaos / 10:
            chunks.append(" " + random.choice([
                random.choice(KAOMOJI),
                emoji_burst(2, 6),
                symbol_burst(2, 7),
                rune_burst(),
                random.choice(GLITCH_WORDS),
            ]))

    if chaos >= 5 and random.random() < 0.65:
        chunks.append(f" and whispered {weird_quote(language_soup(random.randint(3, 8)))}")
    if chaos >= 7 and random.random() < 0.6:
        chunks.append(" " + random.choice(["𓂀𓆏𓂀", "꧁༺☠︎༻꧂", "ΣΩΣΩΣΩ", rune_burst(8, 18), emoji_burst(5, 12)]))
    return "".join(chunks) + random.choice([".", "!", "‽", "⁉", "!!!", "⸮", " ※", " ∎", " ꙮ"])


# ============================================================
# FAKE .NET STACK TRACE GENERATOR
# ============================================================

def dotnet_identifier() -> str:
    namespace = random.choice(DOTNET_NAMESPACES)
    cls = random.choice(DOTNET_CLASSES)
    method = random.choice(DOTNET_METHODS)
    generic = random.choice(["", "", "", "[T]", "[TContext]", "[TPotato]"])
    return f"{namespace}.{cls}{generic}.{method}"


def dotnet_arguments() -> str:
    return random.choice([
        "()",
        "(String value)",
        "(CancellationToken cancellationToken)",
        "(Object sender, EventArgs e)",
        "(Potato potato, Int32 moonCount)",
        "(String cheese, Boolean forbidden)",
        "(GoblinContext context)",
        "(IEnumerable`1 objects)",
        "(ReadOnlySpan`1 reality)",
        "(Task`1 banana)",
        "(𓆏 frog, String[] args)",
    ])


def dotnet_file() -> str:
    root = random.choice(DOTNET_PATHS)
    namespace = random.choice(DOTNET_NAMESPACES).replace(".", "\\")
    filename = random.choice(DOTNET_CLASSES) + ".cs"
    return rf"{root}\{namespace}\{filename}"


def dotnet_stack_frame() -> str:
    method = dotnet_identifier()
    args = dotnet_arguments()
    if random.random() < 0.25:
        return f"   at {method}{args}"
    return f"   at {method}{args} in {dotnet_file()}:line {random.randint(6, 9999)}"


def dotnet_async_frame() -> str:
    namespace = random.choice(DOTNET_NAMESPACES)
    cls = random.choice(DOTNET_CLASSES)
    method = random.choice(DOTNET_METHODS)
    state = random.randint(0, 42)
    return (
        f"   at {namespace}.{cls}.<{method}>d__{state}.MoveNext() "
        f"in {dotnet_file()}:line {random.randint(10, 4000)}"
    )


def dotnet_stack_trace(depth: int | None = None, chaos: int = 7) -> str:
    if depth is None:
        depth = random.randint(3, 6 + chaos)
    frames = []
    for _ in range(depth):
        frames.append(dotnet_async_frame() if random.random() < 0.35 else dotnet_stack_frame())
        if random.random() < 0.18:
            frames.append(random.choice(DOTNET_RUNTIME_FRAMES))
    return "\n".join(frames)


def dotnet_exception_data(chaos: int = 7, include_inner: bool = True) -> dict:
    exception_type = random.choice(DOTNET_EXCEPTIONS)
    message = random.choice(DOTNET_MESSAGES)
    if chaos >= 8 and random.random() < 0.4:
        message += f" {symbol_burst(1, 4)} {language_soup(random.randint(1, 4))}"

    inners = []
    if include_inner and chaos >= 5:
        for _ in range(random.randint(1, 1 + chaos // 4)):
            if random.random() < 0.72:
                inners.append({
                    "type": random.choice(DOTNET_EXCEPTIONS),
                    "message": random.choice(DOTNET_MESSAGES),
                    "stack": dotnet_stack_trace(random.randint(1, max(2, chaos // 2)), chaos),
                })

    return {
        "type": exception_type,
        "message": message,
        "stack": dotnet_stack_trace(chaos=chaos),
        "inner": inners,
        "hresult": random.choice(DOTNET_HRESULTS),
        "trace_id": f"00-{secrets.token_hex(16)}-{secrets.token_hex(8)}-00",
    }


def dotnet_exception_text(chaos: int = 7) -> str:
    data = dotnet_exception_data(chaos)
    lines = [f"Unhandled exception. {data['type']}: {data['message']}", data["stack"]]
    for inner in data["inner"]:
        lines.extend([
            f" ---> {inner['type']}: {inner['message']}",
            inner["stack"],
            "   --- End of inner exception stack trace ---",
        ])
    if chaos >= 6:
        lines.append(f"HRESULT: {data['hresult']}")
    if chaos >= 8:
        lines.extend([
            "",
            "=== CLR REALITY DIAGNOSTICS ===",
            f"Managed thread ID: {random.randint(1, 128)}",
            f"GC generation: {random.randint(0, 2)}",
            f"AppDomain: {random.choice(['DefaultDomain', 'VOID', 'CheeseDomain', '𓂀'])}",
            f"Current culture: {random.choice(['en-US', 'de-DE', 'ja-JP', '??-MOON'])}",
            f"Reality integrity: {random.choice(['FAILED', 'NaN%', '-1', '🧀'])}",
            f"Trace identifier: {data['trace_id']}",
        ])
    return "\n".join(lines)


# ============================================================
# ASP.NET-STYLE HTML ERROR PAGE
# ============================================================

def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fake_request_headers(handler: BaseHTTPRequestHandler) -> list[tuple[str, str]]:
    headers = [(k, v) for k, v in handler.headers.items()]
    headers.extend([
        ("X-Fake-CLR", random.choice(["8.0.8", "9.0.0-preview", "∞.0.𓆏"])),
        ("X-Reality-Integrity", random.choice(["FAILED", "NaN", "CHEESE"])),
        ("X-Goblin-Mode", random.choice(["enabled", "aggressive", "recursive"])),
    ])
    return headers


def render_dotnet_error_page(handler: BaseHTTPRequestHandler, chaos: int) -> str:
    data = dotnet_exception_data(chaos)
    parsed = urlparse(handler.path)
    headers = fake_request_headers(handler)

    inner_html = ""
    for inner in data["inner"]:
        inner_html += f"""
        <section class="panel inner">
          <h2>Inner Exception</h2>
          <div class="exception">{_esc(inner['type'])}: {_esc(inner['message'])}</div>
          <pre>{_esc(inner['stack'])}</pre>
        </section>
        """

    header_rows = "\n".join(
        f"<tr><td>{_esc(k)}</td><td>{_esc(v)}</td></tr>" for k, v in headers
    )

    query_rows = ""
    query = parse_qs(parsed.query, keep_blank_values=True)
    if query:
        query_rows = "\n".join(
            f"<tr><td>{_esc(k)}</td><td>{_esc(', '.join(v))}</td></tr>"
            for k, v in query.items()
        )
    else:
        query_rows = "<tr><td colspan='2'><em>No query string parameters.</em></td></tr>"

    nonsense = generate_sentence(chaos)
    timestamp = datetime.now(timezone.utc).isoformat()

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(data['type'])} — Fake Developer Exception Page</title>
<style>
:root {{
  color-scheme: light dark;
  --bg: #111318;
  --panel: #1b1f27;
  --text: #ecedf1;
  --muted: #aab0bd;
  --danger: #ff6b6b;
  --border: #343a46;
  --code: #0d0f13;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
}}
header {{
  padding: 28px 32px 18px;
  border-bottom: 1px solid var(--border);
}}
main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
h1 {{ margin: 0 0 8px; color: var(--danger); font-size: 1.55rem; overflow-wrap: anywhere; }}
h2 {{ margin-top: 0; font-size: 1.05rem; }}
.subtitle {{ color: var(--muted); }}
.badge {{
  display: inline-block;
  border: 1px solid var(--danger);
  color: var(--danger);
  border-radius: 999px;
  padding: 3px 8px;
  margin-left: 8px;
  font-size: .75rem;
  vertical-align: middle;
}}
.panel {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px;
  margin: 16px 0;
  overflow: hidden;
}}
.inner {{ border-left: 4px solid #b06cff; }}
.exception {{
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  color: #ffb4b4;
  overflow-wrap: anywhere;
}}
pre {{
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  padding: 14px;
  background: var(--code);
  border-radius: 8px;
  line-height: 1.45;
}}
table {{ width: 100%; border-collapse: collapse; }}
td {{
  padding: 7px 9px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
  overflow-wrap: anywhere;
}}
td:first-child {{
  width: 240px;
  color: var(--muted);
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
}}
footer {{ color: var(--muted); padding: 8px 0 28px; font-size: .85rem; }}
.warning {{
  padding: 10px 12px;
  border-radius: 8px;
  background: #2c2315;
  border: 1px solid #73531c;
}}
</style>
</head>
<body>
<header>
  <h1>{_esc(data['type'])}<span class="badge">FAKE / GENERATED</span></h1>
  <div class="subtitle">{_esc(data['message'])}</div>
</header>
<main>
  <div class="warning">
    This is a fictional ASP.NET-style developer error page generated by crazy_server.py.
    It is not a real application diagnostic.
  </div>

  <section class="panel">
    <h2>Stack</h2>
    <pre>{_esc(data['stack'])}</pre>
  </section>

  {inner_html}

  <section class="panel">
    <h2>Request</h2>
    <table>
      <tr><td>Method</td><td>{_esc(handler.command)}</td></tr>
      <tr><td>Path</td><td>{_esc(parsed.path)}</td></tr>
      <tr><td>Protocol</td><td>{_esc(handler.request_version)}</td></tr>
      <tr><td>TraceIdentifier</td><td>{_esc(data['trace_id'])}</td></tr>
      <tr><td>Timestamp (UTC)</td><td>{_esc(timestamp)}</td></tr>
      <tr><td>HRESULT</td><td>{_esc(data['hresult'])}</td></tr>
    </table>
  </section>

  <section class="panel">
    <h2>Query</h2>
    <table>{query_rows}</table>
  </section>

  <section class="panel">
    <h2>Headers</h2>
    <table>{header_rows}</table>
  </section>

  <section class="panel">
    <h2>Reality diagnostics</h2>
    <pre>{_esc(nonsense)}

GC generation: {random.randint(0, 2)}
ThreadPool goblins: {random.randint(1, 9001)}
Culture: {random.choice(["en-US", "fr-FR", "ja-JP", "??-MOON"])}
Reality integrity: {random.choice(["FAILED", "NaN%", "CHEESE", "𓆏"])}
Server: Kestrel-but-not-really/{random.randint(1, 99)}.{random.randint(0, 9)}
</pre>
  </section>

  <footer>
    Generated locally by crazy_server.py · not affiliated with Microsoft or ASP.NET Core.
  </footer>
</main>
</body>
</html>"""


# ============================================================
# HTTP SERVER
# ============================================================

class CrazyHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address, handler_cls, *, chaos: int, dotnet: bool, status: int, seed: int | None):
        super().__init__(server_address, handler_cls)
        self.chaos = chaos
        self.dotnet = dotnet
        self.status = status
        self.seed = seed
        self.request_count = 0
        self.request_lock = threading.Lock()


class CrazyHandler(BaseHTTPRequestHandler):
    server_version = "CrazyFakeServer/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        sys.stderr.write(f"[{stamp}] {self.client_address[0]} {fmt % args}\n")

    def _seed_for_request(self) -> None:
        if self.server.seed is None:
            random.seed(secrets.randbits(64))
            return
        with self.server.request_lock:
            self.server.request_count += 1
            request_num = self.server.request_count
        random.seed(f"{self.server.seed}:{request_num}:{self.path}:{self.command}")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Crazy-Server", "fake")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _text(self, status: int, text: str) -> None:
        self._send(status, text.encode("utf-8"), "text/plain; charset=utf-8")

    def _html(self, status: int, text: str) -> None:
        self._send(status, text.encode("utf-8"), "text/html; charset=utf-8")

    def _handle(self) -> None:
        self._seed_for_request()
        parsed = urlparse(self.path)
        path = parsed.path
        chaos = self.server.chaos
        status = self.server.status

        # Health stays boring on purpose.
        if path == "/health":
            self._json(200, {
                "ok": True,
                "fake": True,
                "mode": "dotnet" if self.server.dotnet else "plain",
                "chaos": chaos,
            })
            return

        if path == "/":
            if self.server.dotnet:
                self._html(status, render_dotnet_error_page(self, chaos))
            else:
                self._text(status, generate_sentence(chaos))
            return

        if path in ("/stack", "/exception"):
            if self.server.dotnet:
                self._html(status, render_dotnet_error_page(self, chaos))
            else:
                self._text(status, dotnet_exception_text(chaos))
            return

        if path == "/api/error":
            data = dotnet_exception_data(chaos)
            self._json(status, {
                "title": "An absurd fake server error occurred.",
                "status": status,
                "type": data["type"],
                "detail": data["message"],
                "traceId": data["trace_id"],
                "hresult": data["hresult"],
                "stackTrace": data["stack"],
                "nonsense": generate_sentence(chaos),
                "fake": True,
            })
            return

        if path == "/api/nonsense":
            query = parse_qs(parsed.query)
            try:
                count = min(100, max(1, int(query.get("count", ["1"])[0])))
            except ValueError:
                count = 1
            self._json(200, {
                "count": count,
                "chaos": chaos,
                "items": [generate_sentence(chaos) for _ in range(count)],
            })
            return

        if path == "/teapot":
            self._json(418, {
                "error": "Reality Is A Teapot",
                "message": generate_sentence(chaos),
                "traceId": f"00-{secrets.token_hex(16)}-{secrets.token_hex(8)}-00",
            })
            return

        self._json(404, {
            "status": 404,
            "error": "System.RealityNotFoundException",
            "message": f"The route {_esc(path)} was eaten by a multilingual goblin.",
            "nonsense": generate_sentence(chaos),
        })

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle
    do_PATCH = _handle
    do_DELETE = _handle
    do_HEAD = _handle


# ============================================================
# CLI
# ============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a fake HTTP server that emits absurd Unicode errors and fake .NET diagnostics."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Address to bind. Default: 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="TCP port. Default: 8000",
    )
    parser.add_argument(
        "-c", "--chaos",
        type=int,
        default=7,
        help="Chaos level 1-10. Default: 7",
    )
    parser.add_argument(
        "--dotnet",
        action="store_true",
        help="Render fake ASP.NET-style HTML developer exception pages.",
    )
    parser.add_argument(
        "--status",
        type=int,
        default=500,
        help="HTTP status used for generated error endpoints. Default: 500",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional deterministic seed. Requests remain varied but reproducible.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.chaos = max(1, min(10, args.chaos))

    if not (1 <= args.port <= 65535):
        print("error: --port must be between 1 and 65535", file=sys.stderr)
        return 2

    if not (100 <= args.status <= 599):
        print("error: --status must be a valid HTTP status code (100-599)", file=sys.stderr)
        return 2

    server = CrazyHTTPServer(
        (args.host, args.port),
        CrazyHandler,
        chaos=args.chaos,
        dotnet=args.dotnet,
        status=args.status,
        seed=args.seed,
    )

    shown_host = "localhost" if args.host in ("127.0.0.1", "::1") else args.host
    mode = "fake ASP.NET-style pages" if args.dotnet else "plain nonsense/errors"

    print(f"Crazy Fake Server running: http://{shown_host}:{args.port}")
    print(f"Mode: {mode} | chaos={args.chaos} | error-status={args.status}")
    print("Endpoints: /  /health  /stack  /exception  /api/error  /api/nonsense?count=5  /teapot")
    if args.host not in ("127.0.0.1", "::1", "localhost"):
        print("WARNING: You are binding beyond loopback. This server is for local/dev use and has no authentication.")
    print("Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
