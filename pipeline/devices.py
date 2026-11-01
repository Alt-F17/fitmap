"""Device catalog: the phones in scope, with search aliases.

Run directly to write data/devices.json.
"""
import json
import pathlib

# (id, brand, family, display name, year, extra aliases)
_RAW = [
    # ---- Apple: iPhone 15 -> 18 ----
    ("ip15", "Apple", "iPhone", "iPhone 15", 2023, ["iphone15", "i15"]),
    ("ip15plus", "Apple", "iPhone", "iPhone 15 Plus", 2023, ["15 plus", "15+"]),
    ("ip15pro", "Apple", "iPhone", "iPhone 15 Pro", 2023, ["15 pro", "15p"]),
    ("ip15promax", "Apple", "iPhone", "iPhone 15 Pro Max", 2023, ["15 pro max", "15pm", "15 promax"]),
    ("ip16", "Apple", "iPhone", "iPhone 16", 2024, ["iphone16", "i16"]),
    ("ip16plus", "Apple", "iPhone", "iPhone 16 Plus", 2024, ["16 plus", "16+"]),
    ("ip16pro", "Apple", "iPhone", "iPhone 16 Pro", 2024, ["16 pro", "16p"]),
    ("ip16promax", "Apple", "iPhone", "iPhone 16 Pro Max", 2024, ["16 pro max", "16pm", "16 promax"]),
    ("ip16e", "Apple", "iPhone", "iPhone 16e", 2025, ["16e", "iphone 16 e"]),
    ("ip17", "Apple", "iPhone", "iPhone 17", 2025, ["iphone17", "i17"]),
    ("ipair", "Apple", "iPhone", "iPhone Air", 2025, ["iphone air", "17 air"]),
    ("ip17pro", "Apple", "iPhone", "iPhone 17 Pro", 2025, ["17 pro", "17p"]),
    ("ip17promax", "Apple", "iPhone", "iPhone 17 Pro Max", 2025, ["17 pro max", "17pm", "17 promax"]),
    ("ip17e", "Apple", "iPhone", "iPhone 17e", 2026, ["17e", "iphone 17 e"]),
    ("ip18pro", "Apple", "iPhone", "iPhone 18 Pro", 2026, ["18 pro", "18p"]),
    ("ip18promax", "Apple", "iPhone", "iPhone 18 Pro Max", 2026, ["18 pro max", "18pm", "18 promax"]),
    # ---- Google Pixel 8 -> 11 (folds excluded) ----
    ("px8", "Google", "Pixel", "Pixel 8", 2023, ["pixel 8", "pixel8", "p8"]),
    ("px8pro", "Google", "Pixel", "Pixel 8 Pro", 2023, ["pixel 8 pro", "8 pro", "p8p", "p8 pro"]),
    ("px8a", "Google", "Pixel", "Pixel 8a", 2024, ["pixel 8a", "8a"]),
    ("px9", "Google", "Pixel", "Pixel 9", 2024, ["pixel 9", "pixel9", "p9"]),
    ("px9pro", "Google", "Pixel", "Pixel 9 Pro", 2024, ["pixel 9 pro", "9 pro", "p9p", "p9 pro"]),
    ("px9proxl", "Google", "Pixel", "Pixel 9 Pro XL", 2024, ["pixel 9 pro xl", "9 pro xl", "p9pxl", "p9 pro xl"]),
    ("px9a", "Google", "Pixel", "Pixel 9a", 2025, ["pixel 9a", "9a"]),
    ("px10", "Google", "Pixel", "Pixel 10", 2025, ["pixel 10", "pixel10", "p10"]),
    ("px10pro", "Google", "Pixel", "Pixel 10 Pro", 2025, ["pixel 10 pro", "10 pro", "p10p", "p10 pro"]),
    ("px10proxl", "Google", "Pixel", "Pixel 10 Pro XL", 2025, ["pixel 10 pro xl", "10 pro xl", "p10pxl", "p10 pro xl"]),
    ("px10a", "Google", "Pixel", "Pixel 10a", 2026, ["pixel 10a", "10a"]),
    ("px11", "Google", "Pixel", "Pixel 11", 2026, ["pixel 11", "pixel11", "p11"]),
    ("px11pro", "Google", "Pixel", "Pixel 11 Pro", 2026, ["pixel 11 pro", "11 pro", "p11p", "p11 pro"]),
    ("px11proxl", "Google", "Pixel", "Pixel 11 Pro XL", 2026, ["pixel 11 pro xl", "11 pro xl", "p11pxl", "p11 pro xl"]),
    # ---- Samsung Galaxy S22 -> S26 ----
    ("s22", "Samsung", "Galaxy S", "Galaxy S22", 2022, ["s22"]),
    ("s22p", "Samsung", "Galaxy S", "Galaxy S22+", 2022, ["s22+", "s22 plus"]),
    ("s22u", "Samsung", "Galaxy S", "Galaxy S22 Ultra", 2022, ["s22 ultra", "s22u"]),
    ("s23", "Samsung", "Galaxy S", "Galaxy S23", 2023, ["s23"]),
    ("s23p", "Samsung", "Galaxy S", "Galaxy S23+", 2023, ["s23+", "s23 plus"]),
    ("s23u", "Samsung", "Galaxy S", "Galaxy S23 Ultra", 2023, ["s23 ultra", "s23u"]),
    ("s23fe", "Samsung", "Galaxy S", "Galaxy S23 FE", 2023, ["s23 fe", "s23fe"]),
    ("s24", "Samsung", "Galaxy S", "Galaxy S24", 2024, ["s24"]),
    ("s24p", "Samsung", "Galaxy S", "Galaxy S24+", 2024, ["s24+", "s24 plus"]),
    ("s24u", "Samsung", "Galaxy S", "Galaxy S24 Ultra", 2024, ["s24 ultra", "s24u"]),
    ("s24fe", "Samsung", "Galaxy S", "Galaxy S24 FE", 2024, ["s24 fe", "s24fe"]),
    ("s25", "Samsung", "Galaxy S", "Galaxy S25", 2025, ["s25"]),
    ("s25p", "Samsung", "Galaxy S", "Galaxy S25+", 2025, ["s25+", "s25 plus"]),
    ("s25u", "Samsung", "Galaxy S", "Galaxy S25 Ultra", 2025, ["s25 ultra", "s25u"]),
    ("s25edge", "Samsung", "Galaxy S", "Galaxy S25 Edge", 2025, ["s25 edge"]),
    ("s25fe", "Samsung", "Galaxy S", "Galaxy S25 FE", 2025, ["s25 fe", "s25fe"]),
    ("s26", "Samsung", "Galaxy S", "Galaxy S26", 2026, ["s26"]),
    ("s26p", "Samsung", "Galaxy S", "Galaxy S26+", 2026, ["s26+", "s26 plus"]),
    ("s26u", "Samsung", "Galaxy S", "Galaxy S26 Ultra", 2026, ["s26 ultra", "s26u"]),
    # ---- Samsung Galaxy A 2022 -> 2026 ----
    ("a13", "Samsung", "Galaxy A", "Galaxy A13", 2022, ["a13"]),
    ("a23", "Samsung", "Galaxy A", "Galaxy A23", 2022, ["a23"]),
    ("a33", "Samsung", "Galaxy A", "Galaxy A33", 2022, ["a33"]),
    ("a53", "Samsung", "Galaxy A", "Galaxy A53", 2022, ["a53"]),
    ("a14", "Samsung", "Galaxy A", "Galaxy A14", 2023, ["a14"]),
    ("a24", "Samsung", "Galaxy A", "Galaxy A24", 2023, ["a24"]),
    ("a34", "Samsung", "Galaxy A", "Galaxy A34", 2023, ["a34"]),
    ("a54", "Samsung", "Galaxy A", "Galaxy A54", 2023, ["a54"]),
    ("a15", "Samsung", "Galaxy A", "Galaxy A15", 2024, ["a15"]),
    ("a25", "Samsung", "Galaxy A", "Galaxy A25", 2024, ["a25"]),
    ("a35", "Samsung", "Galaxy A", "Galaxy A35", 2024, ["a35"]),
    ("a55", "Samsung", "Galaxy A", "Galaxy A55", 2024, ["a55"]),
    ("a16", "Samsung", "Galaxy A", "Galaxy A16", 2025, ["a16"]),
    ("a26", "Samsung", "Galaxy A", "Galaxy A26", 2025, ["a26"]),
    ("a36", "Samsung", "Galaxy A", "Galaxy A36", 2025, ["a36"]),
    ("a56", "Samsung", "Galaxy A", "Galaxy A56", 2025, ["a56"]),
    ("a17", "Samsung", "Galaxy A", "Galaxy A17", 2026, ["a17"]),
    ("a27", "Samsung", "Galaxy A", "Galaxy A27", 2026, ["a27"]),
    ("a37", "Samsung", "Galaxy A", "Galaxy A37", 2026, ["a37"]),
    ("a57", "Samsung", "Galaxy A", "Galaxy A57", 2026, ["a57"]),
    # ---- Motorola moto g 2023 -> 2026 ----
    ("mgplay23", "Motorola", "moto g", "moto g play (2023)", 2023, ["g play 2023"]),
    ("mg5g23", "Motorola", "moto g", "moto g 5G (2023)", 2023, ["g 5g 2023", "moto g 2023"]),
    ("mgpower23", "Motorola", "moto g", "moto g power 5G (2023)", 2023, ["g power 2023"]),
    ("mgstylus23", "Motorola", "moto g", "moto g stylus (2023)", 2023, ["g stylus 2023", "stylus 2023"]),
    ("mgstylus5g23", "Motorola", "moto g", "moto g stylus 5G (2023)", 2023, ["g stylus 5g 2023", "stylus 5g 2023"]),
    ("mgplay24", "Motorola", "moto g", "moto g play (2024)", 2024, ["g play 2024"]),
    ("mg5g24", "Motorola", "moto g", "moto g 5G (2024)", 2024, ["g 5g 2024", "moto g 2024"]),
    ("mgpower24", "Motorola", "moto g", "moto g power 5G (2024)", 2024, ["g power 2024"]),
    ("mgstylus24", "Motorola", "moto g", "moto g stylus 5G (2024)", 2024, ["g stylus 2024", "stylus 2024"]),
    ("mg25", "Motorola", "moto g", "moto g (2025)", 2025, ["moto g 2025", "g 2025"]),
    ("mgpower25", "Motorola", "moto g", "moto g power (2025)", 2025, ["g power 2025", "power 2025"]),
    ("mgstylus25", "Motorola", "moto g", "moto g stylus (2025)", 2025, ["g stylus 2025", "stylus 2025"]),
    ("mgplay26", "Motorola", "moto g", "moto g play (2026)", 2026, ["g play 2026"]),
    ("mg26", "Motorola", "moto g", "moto g (2026)", 2026, ["moto g 2026", "g 2026"]),
    ("mgpower26", "Motorola", "moto g", "moto g power (2026)", 2026, ["g power 2026", "power 2026"]),
    ("mgstylus26", "Motorola", "moto g", "moto g stylus (2026)", 2026, ["g stylus 2026", "stylus 2026"]),
    # ---- Motorola edge ----
    ("edge23", "Motorola", "edge", "motorola edge (2023)", 2023, ["edge 2023"]),
    ("edgeplus23", "Motorola", "edge", "motorola edge+ (2023)", 2023, ["edge+ 2023", "edge plus 2023", "edge 40 pro"]),
    ("edge24", "Motorola", "edge", "motorola edge (2024)", 2024, ["edge 2024"]),
    ("edge25", "Motorola", "edge", "motorola edge (2025)", 2025, ["edge 2025"]),
    ("edge26", "Motorola", "edge", "motorola edge (2026)", 2026, ["edge 2026"]),
    # ---- TCL 40 -> 70 ----
    ("tcl40xl", "TCL", "TCL", "TCL 40 XL", 2023, ["40 xl", "40xl"]),
    ("tcl40xe", "TCL", "TCL", "TCL 40 XE 5G", 2023, ["40 xe", "40xe"]),
    ("tcl40se", "TCL", "TCL", "TCL 40 SE", 2023, ["40 se", "40se"]),
    ("tcl40nxt", "TCL", "TCL", "TCL 40 NXTPAPER (5G)", 2023, ["40 nxtpaper"]),
    ("tcl40r", "TCL", "TCL", "TCL 40 R 5G", 2023, ["40 r 5g", "40r"]),
    ("tcl50xl", "TCL", "TCL", "TCL 50 XL 5G", 2024, ["50 xl", "50xl"]),
    ("tcl50xe", "TCL", "TCL", "TCL 50 XE 5G", 2024, ["50 xe", "50xe"]),
    ("tcl50xlnxt", "TCL", "TCL", "TCL 50 XL NXTPAPER 5G", 2024, ["50 xl nxtpaper"]),
    ("tcl50nxt", "TCL", "TCL", "TCL 50 NXTPAPER 5G", 2024, ["50 nxtpaper"]),
    ("tcl50pro", "TCL", "TCL", "TCL 50 Pro NXTPAPER 5G", 2024, ["50 pro nxtpaper", "50 pro"]),
    ("tcl50se", "TCL", "TCL", "TCL 50 SE", 2024, ["50 se", "50se"]),
    ("tcl50le", "TCL", "TCL", "TCL 50 LE", 2024, ["50 le"]),
    ("tcl60xe", "TCL", "TCL", "TCL 60 XE NXTPAPER 5G", 2025, ["60 xe", "60xe"]),
    ("tcl60se", "TCL", "TCL", "TCL 60 SE NXTPAPER", 2025, ["60 se"]),
    ("tcl60nxt", "TCL", "TCL", "TCL 60 NXTPAPER", 2025, ["60 nxtpaper"]),
    ("tcl60r", "TCL", "TCL", "TCL 60R 5G", 2025, ["60r", "60 r 5g"]),
    ("tcl60ultra", "TCL", "TCL", "TCL NXTPAPER 60 Ultra", 2025, ["60 ultra", "nxtpaper 60 ultra"]),
    ("tcl70pro", "TCL", "TCL", "TCL NXTPAPER 70 Pro", 2026, ["70 pro", "nxtpaper 70 pro", "nxtpaper 70"]),
]

# Subreddits harvested per family (archive needs a subreddit for full-text search).
SUBREDDITS = {
    "iPhone": ["iphone", "iPhone15Pro", "iPhone16Pro", "iPhone17Pro", "iphone18pro", "17ProMax",
               "iPhone16", "iPhone17", "iphone16e", "iPhoneAir", "iPhone15"],
    "Pixel": ["GooglePixel", "pixel_phones", "Pixel8Pro", "Pixel9Pro", "Pixel10", "Pixel10Pro",
              "Pixel11", "PixelA"],
    "Galaxy S": ["samsunggalaxy", "samsung", "GalaxyS22", "galaxys23", "GalaxyS24", "GalaxyS25",
                 "GalaxyS26", "S22Ultra", "S23Ultra", "S24Ultra", "S25Ultra", "S26Ultra", "S25FE",
                 "S24FE", "GalaxyS23FE", "S25Edge"],
    "Galaxy A": ["GalaxyA", "GalaxyA57", "GalaxyA56", "GalaxyA55", "GalaxyA54", "GalaxyA35",
                 "GalaxyA36", "GalaxyA16", "GalaxyA15", "GalaxyA25", "GalaxyA53", "GalaxyA34"],
    "moto g": ["MotoG", "motorola", "Moto_G"],
    "edge": ["motorola", "MotorolaEdge"],
    "TCL": ["nxtpaper", "TCL", "PWM_Sensitive"],
    "_shared": ["telus", "videotron", "bell", "Rogers", "PhoneCases", "dbrand", "Spigen"],
}


def build():
    devices = []
    for did, brand, family, name, year, aliases in _RAW:
        al = sorted({a.lower() for a in aliases} | {name.lower()})
        devices.append({"id": did, "brand": brand, "family": family, "name": name,
                        "year": year, "aliases": al})
    return devices


if __name__ == "__main__":
    out = pathlib.Path(__file__).resolve().parent.parent / "data" / "devices.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(build(), indent=1, ensure_ascii=False))
    print(f"{len(_RAW)} devices -> {out}")
