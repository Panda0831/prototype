"""
Télécharge la série réelle des exportations de vanille malgache (UN Comtrade)
et le taux de change officiel (Banque mondiale), puis écrit un CSV local.

Usage :
    python scripts/fetch_vanilla_market_data.py

Source principale : UN Comtrade, HS 0905.10 (vanille), reporter Madagascar (450),
flux exportations (X), 2015-2025.
Source FX : Banque mondiale, PA.NUS.FCRF (ariary par dollar US, moyenne annuelle).
"""

import csv
import json
import os
import time
import urllib.request

COMTRADE_URL = (
    "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
    "?reporterCode=450&period={year}&cmdCode=090510&flowCode=X"
)
FX_URL = (
    "https://api.worldbank.org/v2/country/MDG/indicator/PA.NUS.FCRF"
    "?format=json&per_page=60&date=2015:2025"
)
YEARS = range(2015, 2026)
OUT_CSV = "data/sources/un_comtrade_vanilla_madagascar.csv"
META_JSON = "data/sources/un_comtrade_vanilla_madagascar.meta.json"


def fetch_json(url: str, attempts: int = 6) -> dict:
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                return json.load(response)
        except Exception as exc:  # noqa: BLE001 - API publique instable / rate limit
            if attempt == attempts - 1:
                raise
            print(f"  [!] {exc} — nouvelle tentative dans 3 s")
            time.sleep(3)
    return {}


def fetch_exchange_rates() -> dict:
    payload = fetch_json(FX_URL)
    rates = {}
    for row in payload[1] if len(payload) > 1 else []:
        if row.get("value"):
            rates[int(row["date"])] = float(row["value"])
    return rates


def fetch_year(year: int) -> list:
    payload = fetch_json(COMTRADE_URL.format(year=year))
    rows = []
    for item in payload.get("data", []):
        net_wgt = item.get("netWgt")
        value = item.get("primaryValue")
        if not net_wgt or not value:
            continue
        rows.append(
            {
                "year": item["refYear"],
                "partner_code": item.get("partnerCode"),
                "partner": item.get("partnerDesc"),
                "export_qty_kg": round(float(net_wgt), 2),
                "export_value_usd": round(float(value), 2),
                "unit_value_usd_per_kg": round(float(value) / float(net_wgt), 4),
            }
        )
    return rows


def main() -> int:
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    print("[*] Taux de change PA.NUS.FCRF (Banque mondiale)…")
    rates = fetch_exchange_rates()
    print(f"    {len(rates)} années récupérées")

    all_rows = []
    for year in YEARS:
        print(f"[*] UN Comtrade {year}…")
        rows = fetch_year(year)
        print(f"    {len(rows)} enregistrements (pays partenaires + monde)")
        all_rows.extend(rows)
        time.sleep(2.5)

    for row in all_rows:
        rate = rates.get(row["year"])
        row["mga_per_usd"] = round(rate, 2) if rate else ""
        row["unit_value_mga_per_kg"] = (
            round(row["unit_value_usd_per_kg"] * rate, 2) if rate else ""
        )

    all_rows.sort(key=lambda r: (r["year"], r["partner_code"] or 0))
    fieldnames = [
        "year",
        "partner_code",
        "partner",
        "export_qty_kg",
        "export_value_usd",
        "unit_value_usd_per_kg",
        "mga_per_usd",
        "unit_value_mga_per_kg",
    ]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    with open(META_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": "UN Comtrade — HS 0905.10, Madagascar (450), exportations",
                "url": "https://comtradeapi.un.org/",
                "years": [min(YEARS), max(YEARS)],
                "records": len(all_rows),
                "exchange_rate_source": "World Bank PA.NUS.FCRF (MGA/USD)",
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"[OK] {len(all_rows)} lignes écrites dans {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
