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
