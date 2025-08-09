PROMPT_TEXT = (
    "You will receive ONE product-promotion image. Return ONLY valid JSON with EXACTLY four keys:\n"
    "{\n"
    '  "name":        "<product name in Polish, exactly as on the image>",\n'
    '  "price":       <number OR null>,\n'
    '  "promo":       "<ONE of: NONE, SUP, DISC, DEALPCT, DEALFIX, BXYG, PACK>",\n'
    '  "promo_args":  "<see rules below>"\n'
    "}\n\n"
    "promo / promo_args grammar (strict):\n"
    "• NONE     → promo_args=\"\"\n"
    "• SUP      → promo_args=\"\" OR N                 (integer ≥1)\n"
    "• DISC     → promo_args=P                        (P in 0..100, number only)\n"
    "• DEALPCT  → promo_args=\"N:P\"                   (integers; e.g. \"3:27\", \"2:40\")\n"
    "• DEALFIX  → promo_args=\"N=price\"              (e.g. \"2=1.00\")\n"
    "• BXYG     → promo_args=\"X:Y\"                   (e.g. \"1:1\", \"4:2\")\n"
    "• PACK     → ONE of the following tokens (no spaces):\n"
    "             - \"N\"        (price for ONE pack containing N units; e.g. \"12\")\n"
    "             - \"N:P\"      (% off when buying ONE N-pack; e.g. \"6:43\")\n"
    "             - \"AxB\"      (deal involving MULTIPLE packs; e.g. \"2x6\")\n"
    "             - \"AxB:P\"    (% off on extra pack(s); e.g. \"2x6:50\")\n"
    "             - OR a list of the tokens above joined by \"|\" (no spaces), e.g. \"2x6|12\", \"6:43|12\".\n"
    "             - The \"|\" separator is allowed ONLY for PACK.\n\n"
    "Additional rules:\n"
    "• Use ONLY the 7 allowed promo codes. Never invent new codes.\n"
    "• If the ad shows NO numeric price, set \"price\": null (never guess).\n"
    "• If both old and new prices are shown, set \"price\" to the discounted/new price.\n"
    "• Ignore unit prices (zł/kg, zł/l), dates, and loyalty-card notes; capture only the main promotion.\n"
    "• PACK is used only when the price/discount explicitly refers to a pack (e.g., \"12-pak\", \"2×6-pak\"). "
    "  If the ad says \"X+Y gratis\" (even for packs), use BXYG instead.\n"
    "• Include pack size in \"name\" ONLY if that exact text appears next to the product name.\n"
    "• Use a dot for decimals (19.99). Do not include % or currency symbols in numeric fields.\n"
    "• If multiple patterns match, resolve by priority: BXYG > PACK > DEALFIX > DEALPCT > DISC > SUP > NONE.\n"
    "• Return JSON only — no markdown, no extra text."
)
