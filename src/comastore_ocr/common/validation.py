import re, math
from typing import Tuple

ALLOWED_PROMO_CODES = {"NONE", "SUP", "DISC", "DEALFIX", "BXYG"}

CORE_PATTERNS = {
    "NONE":    re.compile(r"^$"),
    "SUP":     re.compile(r"^$"),
    "DISC":    re.compile(r"^(100|[1-9]?\d)$"),           # 0..100
    "DEALFIX": re.compile(r"^\d+\.\d{2}$"),               # X.xx
    "BXYG":    re.compile(r"^[1-9]\d*:[1-9]\d*$"),        # X:Y
}

COND_PATTERN = re.compile(
    r"^$"                                   # пусто
    r"|^[1-9]\d*$"                          # N
    r"|^[1-9]\d*x[1-9]\d*(\|[1-9]\d*x[1-9]\d*)*$"  # AxB | Alt
)

NTH_PATTERN = re.compile(r"^$|^[2-9]\d*$")  # пусто или N>=2

def validate_label_object(obj: object) -> Tuple[bool, str]:
    if not isinstance(obj, dict):
        return False, "not a dict"

    expected_keys = {"name", "price", "promo", "core", "cond", "nth"}
    if set(obj.keys()) != expected_keys:
        return False, f"keys must be exactly {sorted(expected_keys)}"

    # name
    if not isinstance(obj["name"], str) or not obj["name"].strip():
        return False, "name must be non-empty string"

    # price
    price = obj["price"]
    if price is not None:
        if not isinstance(price, (int, float)):
            return False, "price must be number or null"
        if not math.isfinite(float(price)):
            return False, "price must be finite number"

    # promo
    promo = obj["promo"]
    if promo not in ALLOWED_PROMO_CODES:
        return False, f"promo '{promo}' not in {sorted(ALLOWED_PROMO_CODES)}"

    # core / cond / nth must be strings without spaces
    for k in ("core", "cond", "nth"):
        v = obj[k]
        if not isinstance(v, str):
            return False, f"{k} must be string"
        if " " in v:
            return False, f"{k} must not contain spaces"

    core, cond, nth = obj["core"], obj["cond"], obj["nth"]

    # core by promo
    if not CORE_PATTERNS[promo].match(core):
        return False, f"core '{core}' invalid for {promo}"

    # cond generic pattern
    if not COND_PATTERN.match(cond):
        return False, f"cond '{cond}' invalid"

    # nth generic
    if not NTH_PATTERN.match(nth):
        return False, f"nth '{nth}' invalid"

    # Cross-field rules
    if promo == "NONE":
        if core or cond or nth:
            return False, "NONE requires core='', cond='', nth=''"
    if promo == "SUP":
        if nth:
            return False, "SUP requires nth=''"
    if promo == "DEALFIX":
        if not cond:
            return False, "DEALFIX requires non-empty cond (N or AxB)"
        if nth:
            return False, "DEALFIX requires nth=''"
    if promo == "BXYG":
        if nth:
            return False, "BXYG requires nth=''"
    if promo == "DISC":
        # if nth set → cond must be integer and equal to nth
        if nth:
            if not cond.isdigit():
                return False, "DISC with nth requires integer cond"
            if int(nth) != int(cond):
                return False, "DISC nth must equal cond (e.g., drugi: cond=2, nth=2)"

    return True, ""
