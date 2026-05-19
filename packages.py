# packages.py
# This file stores soft drink package types in one place.
# Each entry is: "menu number": ("label", ounces_per_item, items_per_pack)

package_sizes = {
    # -------------------------
    # Single Cans
    # -------------------------
    "1": ("7.5 oz mini can (single)", 7.5, 1),
    "2": ("8 oz can (single)", 8, 1),
    "3": ("12 oz can (single)", 12, 1),
    "4": ("16 oz can (single)", 16, 1),
    "5": ("24 oz can (single)", 24, 1),

    # -------------------------
    # Single Bottles
    # -------------------------
    "6": ("12 oz bottle (single)", 12, 1),
    "7": ("16 oz bottle (single)", 16, 1),
    "8": ("16.9 oz bottle (single)", 16.9, 1),
    "9": ("20 oz bottle (single)", 20, 1),
    "10": ("1 liter bottle (single)", 33.8, 1),
    "11": ("1.25 liter bottle (single)", 42.3, 1),
    "12": ("1.5 liter bottle (single)", 50.7, 1),
    "13": ("2 liter bottle (single)", 67.6, 1),
    "14": ("3 liter bottle (single)", 101.4, 1),  # rare but real

    # -------------------------
    # Multipack Cans
    # -------------------------
    "20": ("6-pack 12 oz cans", 12, 6),
    "21": ("8-pack 12 oz cans", 12, 8),
    "22": ("10-pack 7.5 oz mini cans", 7.5, 10),
    "23": ("12-pack 12 oz cans", 12, 12),
    "24": ("15-pack 12 oz cans", 12, 15),
    "25": ("18-pack 12 oz cans", 12, 18),
    "26": ("20-pack 12 oz cans", 12, 20),
    "27": ("24-pack 12 oz cans", 12, 24),
    "28": ("30-pack 12 oz cans", 12, 30),

    # -------------------------
    # Multipack Bottles (16.9 oz)
    # -------------------------
    "30": ("6-pack 16.9 oz bottles", 16.9, 6),
    "31": ("8-pack 16.9 oz bottles", 16.9, 8),
    "32": ("12-pack 16.9 oz bottles", 16.9, 12),
    "33": ("24-pack 16.9 oz bottles", 16.9, 24),

    # -------------------------
    # Multipack Bottles (20 oz)
    # -------------------------
    "34": ("6-pack 20 oz bottles", 20, 6),
    "35": ("8-pack 20 oz bottles", 20, 8),   # less common but real
    "36": ("12-pack 20 oz bottles", 20, 12), # club stores

    # -------------------------
    # Specialty / Rare Packs
    # -------------------------
    "40": ("4-pack glass bottles (12 oz)", 12, 4),
    "41": ("6-pack glass bottles (12 oz)", 12, 6),
    "42": ("12-pack glass bottles (12 oz)", 12, 12)
}
