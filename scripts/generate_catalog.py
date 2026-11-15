#!/usr/bin/env python3
"""Build category JSON files + index.json for tennis-life-catalog."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def slug(*parts: str) -> str:
    s = "-".join(parts).lower()
    for a, b in [
        ("á", "a"),
        ("à", "a"),
        ("â", "a"),
        ("ã", "a"),
        ("é", "e"),
        ("ê", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ô", "o"),
        ("õ", "o"),
        ("ú", "u"),
        ("ç", "c"),
        (" ", "-"),
        ("/", "-"),
        (".", ""),
        (",", ""),
        ("(", ""),
        (")", ""),
    ]:
        s = s.replace(a, b)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def envelope(items: list) -> dict:
    return {"schemaVersion": 1, "items": items}


def racket(brand, model, details, weight, head, pattern, balance, ra, length=68.5):
    return {
        "id": slug(brand, model),
        "brand": brand,
        "model": model,
        "details": details,
        "specs": {
            "weightG": weight,
            "headSizeSqIn": head,
            "lengthCm": length,
            "pattern": pattern,
            "balance": balance,
            "stiffnessRa": ra,
        },
    }


def gear(brand, model, details=None, **extra):
    item = {"id": slug(brand, model), "brand": brand, "model": model}
    if details:
        item["details"] = details
    item.update(extra)
    return item


def string_item(brand, name, gauge, typ, mains, crosses):
    return {
        "id": slug(brand, name),
        "brand": brand,
        "name": name,
        "spec": {
            "gauge": gauge,
            "type": typ,
            "mainsLbs": mains,
            "crossesLbs": crosses,
        },
    }


RACKETS = [
    racket("Babolat", "Pure Drive", "Potência e spin, a clássica azul", 300, 100, "16x19", "32 cm", 71),
    racket("Babolat", "Pure Drive Lite", "Versão leve da Pure Drive", 270, 100, "16x19", "33 cm", 70),
    racket("Babolat", "Pure Drive 98", "Pure Drive com cabeça menor", 305, 98, "16x19", "32 cm", 68),
    racket("Babolat", "Pure Drive 110", "Cabeça grande, fácil de usar", 255, 110, "16x19", "34 cm", 70),
    racket("Babolat", "Pure Aero", "Feita pro topspin", 300, 100, "16x19", "32 cm", 67),
    racket("Babolat", "Pure Aero 98", "A do Alcaraz", 305, 98, "16x20", "32 cm", 66),
    racket("Babolat", "Pure Aero Rafa", "Edição Rafa, ainda mais spin", 300, 100, "16x19", "32 cm", 67),
    racket("Babolat", "Pure Strike 98 16x19", "Controle com pegada agressiva", 305, 98, "16x19", "32 cm", 66),
    racket("Babolat", "Pure Strike 100", "Controle mais tolerante", 300, 100, "16x19", "32 cm", 67),
    racket("Babolat", "Boost Drive", "Leve, pra quem tá começando", 260, 105, "16x19", "34 cm", 72),
    racket("Wilson", "Blade 98 16x19 v9", "Controle e sensação", 305, 98, "16x19", "32 cm", 62),
    racket("Wilson", "Blade 98 18x20 v9", "Controle máximo, padrão fechado", 305, 98, "18x20", "32 cm", "62"),
    racket("Wilson", "Blade 100 v9", "Blade mais tolerante", 300, 100, "16x19", "32 cm", 63),
    racket("Wilson", "Blade 98L v9", "Blade leve", 285, 98, "16x19", "33 cm", 62),
    racket("Wilson", "Pro Staff 97 v14", "Clássica, estável e precisa", 315, 97, "16x19", "31 cm", 66),
    racket("Wilson", "Pro Staff 97L v14", "Pro Staff mais leve", 290, 97, "16x19", "32 cm", 66),
    racket("Wilson", "Clash 100 v2", "Flexível e confortável", 295, 100, "16x19", "32,5 cm", 55),
    racket("Wilson", "Clash 98 v2", "Clash com mais precisão", 310, 98, "16x20", "32 cm", 56),
    racket("Wilson", "Ultra 100 v4", "Potência fácil", 300, 100, "16x19", "32 cm", 72),
    racket("Wilson", "Shift 99 v1", "Spin com flexão vertical", 300, 99, "16x20", "32 cm", 66),
    racket("Head", "Speed MP", "Equilíbrio entre controle e potência", 300, 100, "16x19", "32 cm", 64),
    racket("Head", "Speed Pro", "Pesada e precisa, padrão fechado", 310, 100, "18x20", "31,5 cm", 64),
    racket("Head", "Speed Team", "Speed mais leve", 285, 100, "16x19", "33 cm", 64),
    racket("Head", "Radical MP", "All-court versátil", 300, 98, "16x19", "32 cm", 66),
    racket("Head", "Extreme MP", "Spin e potência", 300, 100, "16x19", "32 cm", 67),
    racket("Head", "Gravity MP", "Cabeça grande e muito controle", 295, 104, "16x20", "32,5 cm", 61),
    racket("Head", "Prestige MP", "Toque clássico", 320, 99, "18x19", "31 cm", 63),
    racket("Head", "Boom MP", "Potência com conforto", 295, 100, "16x19", "32,5 cm", 68),
    racket("Yonex", "EZONE 98", "Conforto e potência controlada", 305, 98, "16x19", "31,5 cm", 64),
    racket("Yonex", "EZONE 100", "Potência com conforto", 300, 100, "16x19", "32 cm", 69),
    racket("Yonex", "EZONE 98L", "EZONE leve", 285, 98, "16x19", "32,5 cm", 64),
    racket("Yonex", "VCORE 98", "Spin e sensação", 305, 98, "16x19", "31,5 cm", 63),
    racket("Yonex", "VCORE 100", "Spin tolerante", 300, 100, "16x19", "32 cm", 65),
    racket("Yonex", "Percept 97", "Controle e estabilidade", 310, 97, "16x19", "31 cm", 62),
    racket("Yonex", "Percept 100", "Percept mais tolerante", 300, 100, "16x19", "32 cm", 62),
    racket("Tecnifibre", "TF40 305 16M", "Controle com toque macio", 305, 98, "16x19", "32 cm", 65),
    racket("Tecnifibre", "TFight 300 Isoflex", "Potência controlada", 300, 98, "16x19", "32,5 cm", 68),
    racket("Tecnifibre", "TFight 305 Isoflex", "TFight um pouco mais pesada", 305, 98, "18x19", "32 cm", 68),
    racket("Dunlop", "CX 200", "Controle e sensação", 305, 98, "16x19", "32 cm", 66),
    racket("Dunlop", "SX 300", "Spin e potência", 300, 100, "16x19", "32 cm", 69),
    racket("Dunlop", "FX 500", "Potência fácil", 300, 100, "16x19", "32 cm", 70),
    racket("Prince", "Phantom 100X", "Bem flexível, muito conforto", 305, 100, "18x20", "32 cm", 60),
    racket("Prince", "Textreme Tour 100P", "Controle moderno", 310, 100, "18x20", "32 cm", 64),
    racket("Volkl", "V-Cell 8 300", "Conforto e spin", 300, 100, "16x18", "32 cm", 68),
    racket("Volkl", "V-Cell 10 300", "Controle com conforto", 300, 98, "16x19", "32 cm", 65),
]

# Fix the accidental string stiffness
for r in RACKETS:
    if isinstance(r["specs"]["stiffnessRa"], str):
        r["specs"]["stiffnessRa"] = float(r["specs"]["stiffnessRa"])

SHOES = [
    gear("Asics", "Gel-Resolution 9", "Estabilidade, todas as quadras", court="todas"),
    gear("Asics", "Gel-Resolution 9 Clay", "Estabilidade, saibro", court="saibro"),
    gear("Asics", "Solution Speed FF 3", "Leve e rápido", court="todas"),
    gear("Asics", "Court FF 3", "Conforto e ajuste", court="todas"),
    gear("Asics", "Gel-Challenger 14", "Custo-benefício, todas as quadras", court="todas"),
    gear("Asics", "Gel-Game 9", "Entrada de linha estável", court="todas"),
    gear("Nike", "Air Zoom Vapor 11", "Leve, todas as quadras", court="todas"),
    gear("Nike", "Air Zoom Vapor Pro 2", "Leve e responsivo", court="todas"),
    gear("Nike", "GP Challenge Pro", "Amortecimento e estabilidade", court="todas"),
    gear("Nike", "Court Lite 4", "Custo-benefício", court="todas"),
    gear("Adidas", "Barricade", "Durabilidade e estabilidade", court="todas"),
    gear("Adidas", "Adizero Ubersonic 4", "Leve e veloz", court="todas"),
    gear("Adidas", "SoleMatch Control 2", "Estabilidade lateral", court="todas"),
    gear("Adidas", "CourtJam Control 3", "Conforto diário", court="todas"),
    gear("Babolat", "Jet Mach 3", "Leve, pra jogo rápido", court="todas"),
    gear("Babolat", "Propulse Fury 3", "Estabilidade e durabilidade", court="todas"),
    gear("Babolat", "Sensa", "Feminino, conforto", court="todas"),
    gear("Wilson", "Rush Pro 4.0", "Estabilidade", court="todas"),
    gear("Wilson", "Kaos Swift 1.5", "Leve", court="todas"),
    gear("Head", "Sprint Pro 3.5", "Leve e confortável", court="todas"),
    gear("Head", "Revolt Pro 4.5", "Estabilidade", court="todas"),
    gear("Yonex", "Power Cushion Eclipsion 5", "Amortecimento e estabilidade", court="todas"),
    gear("Yonex", "Power Cushion AD-Accel", "Leve", court="todas"),
    gear("K-Swiss", "Hypercourt Supreme 2", "Estabilidade e conforto", court="todas"),
    gear("New Balance", "Fresh Foam X CT-Rally", "Amortecimento", court="todas"),
    gear("New Balance", "FuelCell Lav V2", "Leve e responsivo", court="todas"),
    gear("Mizuno", "Wave Exceed Tour 6", "Estabilidade e conforto", court="todas"),
    gear("Olympikus", "Ace", "Custo-benefício", court="todas"),
    gear("Fila", "Axilus 2 Energized", "Estabilidade", court="todas"),
    gear("Lotto", "Mirage 100 SPD", "Leve", court="todas"),
]

BALLS = [
    gear("Wilson", "US Open", "Pressurizada, tubo com 3", pressurized=True, tubeCount=3),
    gear("Wilson", "Roland Garros Clay", "Pressurizada, feita pro saibro", pressurized=True, tubeCount=4),
    gear("Wilson", "Championship", "Pressurizada, dia a dia", pressurized=True, tubeCount=3),
    gear("Wilson", "Triniti", "Pressurizada, mais durável", pressurized=True, tubeCount=3),
    gear("Head", "Tour", "Pressurizada, tubo com 4", pressurized=True, tubeCount=4),
    gear("Head", "ATP", "Pressurizada, todas as quadras", pressurized=True, tubeCount=4),
    gear("Head", "Championship", "Pressurizada, custo-benefício", pressurized=True, tubeCount=3),
    gear("Babolat", "Gold Championship", "Pressurizada, tubo com 3", pressurized=True, tubeCount=3),
    gear("Babolat", "Team Clay", "Pressurizada, saibro", pressurized=True, tubeCount=4),
    gear("Dunlop", "ATP Championship", "Pressurizada, tubo com 3", pressurized=True, tubeCount=3),
    gear("Dunlop", "Fort All Court", "Pressurizada, durável", pressurized=True, tubeCount=4),
    gear("Penn", "Championship", "Pressurizada, dia a dia", pressurized=True, tubeCount=3),
    gear("Slazenger", "Wimbledon", "Pressurizada, a oficial da grama", pressurized=True, tubeCount=4),
    gear("Tecnifibre", "X-One", "Pressurizada, tubo com 4", pressurized=True, tubeCount=4),
    gear("Yonex", "Tour", "Pressurizada", pressurized=True, tubeCount=4),
]

BAGS = [
    gear("Babolat", "Pure Drive RH12", "Raqueteira para 12 raquetes", racketCapacity=12),
    gear("Babolat", "Pure Aero Backpack", "Mochila para 2 raquetes", racketCapacity=2),
    gear("Babolat", "Pure Drive RH6", "Raqueteira para 6 raquetes", racketCapacity=6),
    gear("Wilson", "Super Tour 9 Pack", "Raqueteira para 9 raquetes", racketCapacity=9),
    gear("Wilson", "Tour Backpack", "Mochila para 2 raquetes", racketCapacity=2),
    gear("Wilson", "Super Tour 15 Pack", "Raqueteira grande", racketCapacity=15),
    gear("Head", "Tour Racquet Bag L", "Raqueteira grande", racketCapacity=12),
    gear("Head", "Tour Backpack 28L", "Mochila para 2 raquetes", racketCapacity=2),
    gear("Yonex", "Pro Racquet Bag 9", "Raqueteira para 9 raquetes", racketCapacity=9),
    gear("Yonex", "Pro Backpack S", "Mochila compacta", racketCapacity=2),
    gear("Tecnifibre", "Tour Endurance 15R", "Raqueteira para 15 raquetes", racketCapacity=15),
    gear("Tecnifibre", "Tour Endurance Backpack", "Mochila para 3 raquetes", racketCapacity=3),
]

ACCESSORIES = [
    gear("Wilson", "Pro Overgrip", "Overgrip macio, pacote com 3"),
    gear("Wilson", "Comfort Pro Overgrip", "Overgrip macio e absorvente"),
    gear("Tourna", "Grip Original", "Overgrip seco, pra mão que sua"),
    gear("Tourna", "Mega Tac", "Overgrip bem pegajoso"),
    gear("Babolat", "VS Original", "Overgrip fino e seco"),
    gear("Babolat", "Pro Tour", "Overgrip clássico"),
    gear("Yonex", "Super Grap", "Overgrip macio e durável"),
    gear("Head", "Prime Tour", "Overgrip seco"),
    gear("Head", "Hydrosorb Pro", "Replacement grip confortável"),
    gear("Babolat", "Custom Damp", "Antivibrador"),
    gear("Wilson", "Pro Feel", "Antivibrador"),
    gear("Tourna", "Sampras Vibration Dampener", "Antivibrador clássico"),
    gear("Nike", "Munhequeira Swoosh", "Par de munhequeiras"),
    gear("Adidas", "Munhequeira Tennis L", "Par de munhequeiras"),
    gear("Wilson", "Tower Ball Basket", "Cesto de bolinhas"),
]

STRINGS = [
    string_item("Luxilon", "ALU Power", "1.25 mm", "Poliéster", 52, 50),
    string_item("Luxilon", "ALU Power Soft", "1.25 mm", "Poliéster macio", 52, 50),
    string_item("Luxilon", "4G", "1.25 mm", "Poliéster", 50, 48),
    string_item("Luxilon", "Element", "1.25 mm", "Poliéster macio", 50, 48),
    string_item("Luxilon", "Adrenaline", "1.25 mm", "Poliéster", 52, 50),
    string_item("Babolat", "RPM Blast", "1.25 mm", "Poliéster", 52, 50),
    string_item("Babolat", "RPM Rough", "1.25 mm", "Poliéster texturizado", 52, 50),
    string_item("Babolat", "RPM Team", "1.25 mm", "Poliéster", 52, 50),
    string_item("Babolat", "Xcel", "1.30 mm", "Multifilamento", 55, 53),
    string_item("Babolat", "VS Touch", "1.30 mm", "Tripa natural", 57, 55),
    string_item("Solinco", "Hyper-G", "1.25 mm", "Poliéster", 50, 48),
    string_item("Solinco", "Tour Bite", "1.25 mm", "Poliéster texturizado", 50, 48),
    string_item("Solinco", "Confidential", "1.25 mm", "Poliéster", 50, 48),
    string_item("Solinco", "Hyper-G Soft", "1.25 mm", "Poliéster macio", 50, 48),
    string_item("Wilson", "NXT", "1.30 mm", "Multifilamento", 55, 53),
    string_item("Wilson", "Revolve", "1.25 mm", "Poliéster", 52, 50),
    string_item("Wilson", "Natural Gut", "1.30 mm", "Tripa natural", 57, 55),
    string_item("Head", "Lynx Tour", "1.25 mm", "Poliéster", 52, 50),
    string_item("Head", "Hawk Touch", "1.25 mm", "Poliéster", 52, 50),
    string_item("Head", "Velocity MLT", "1.30 mm", "Multifilamento", 55, 53),
    string_item("Tecnifibre", "X-One Biphase", "1.30 mm", "Multifilamento", 55, 53),
    string_item("Tecnifibre", "Razor Code", "1.25 mm", "Poliéster", 52, 50),
    string_item("Tecnifibre", "Black Code", "1.24 mm", "Poliéster", 52, 50),
    string_item("Yonex", "Poly Tour Pro", "1.25 mm", "Poliéster", 52, 50),
    string_item("Yonex", "Poly Tour Spin", "1.25 mm", "Poliéster texturizado", 52, 50),
    string_item("Kirschbaum", "Max Power", "1.25 mm", "Poliéster", 52, 50),
    string_item("Signum Pro", "Firestorm", "1.25 mm", "Poliéster", 52, 50),
    string_item("Volkl", "Cyclone", "1.25 mm", "Poliéster", 52, 50),
    string_item("Isospeed", "Cream", "1.28 mm", "Multifilamento", 54, 52),
]

APPAREL = {
    "schemaVersion": 1,
    "brands": [
        "Nike",
        "Adidas",
        "Lacoste",
        "Fila",
        "Asics",
        "Head",
        "Wilson",
        "Babolat",
        "Yonex",
        "Uniqlo",
        "On",
        "Sergio Tacchini",
        "Ellesse",
        "New Balance",
        "Under Armour",
        "Lotto",
        "Castore",
        "Lululemon",
    ],
    "pieces": [
        "Camiseta",
        "Polo",
        "Regata",
        "Shorts",
        "Saia",
        "Vestido",
        "Jaqueta",
        "Boné",
        "Viseira",
        "Meia",
        "Calça",
        "Top",
    ],
}


def write_json(name: str, payload: dict) -> tuple[str, int]:
    path = DATA / name
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    count = len(payload.get("items", payload.get("brands", [])))
    return digest, count


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, items in [
        ("rackets.json", RACKETS),
        ("shoes.json", SHOES),
        ("balls.json", BALLS),
        ("bags.json", BAGS),
        ("accessories.json", ACCESSORIES),
        ("strings.json", STRINGS),
    ]:
        digest, count = write_json(name, envelope(items))
        files[name.replace(".json", "")] = {
            "path": f"data/{name}",
            "sha256": digest,
            "count": count,
        }

    digest, count = write_json("apparel.json", APPAREL)
    files["apparel"] = {"path": "data/apparel.json", "sha256": digest, "count": count}

    index = {
        "schemaVersion": 1,
        "version": 1,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": files,
    }
    (DATA / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v["count"] for k, v in files.items()}, indent=2))


if __name__ == "__main__":
    main()
