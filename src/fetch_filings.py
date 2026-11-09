import json
import requests


def fetch_company_facts(cik="0000320193"):
    """Fetches key financial facts from SEC EDGAR API for a given CIK (Central Index Key).

    Apple CIK: 0000320193
    """
    # SEC EDGAR requires a specific User-Agent format: Sample Company Name AdminContact@<sample company domain>.com
    headers = {"User-Agent": "KalyaniKhandait kalyanik@udel.edu"}

    # Zero-pad CIK to 10 digits
    formatted_cik = str(cik).zfill(10)
    url = (
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{formatted_cik}.json"
    )

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        entity_name = data.get("entityName")

        # Extract Revenue metric under US-GAAP standards
        us_gaap = data.get("facts", {}).get("us-gaap", {})
        revenue_data = us_gaap.get("Revenues", {}) or us_gaap.get(
            "RevenueFromContractWithCustomerExcludingAssessedTax", {}
        )

        units = revenue_data.get("units", {}).get("USD", [])

        # Filter recent 10-K annual revenue records
        recent_revenues = [
            {
                "company": entity_name,
                "fiscal_year": item.get("fy"),
                "period": item.get("form"),
                "revenue_usd": item.get("val"),
                "filed_date": item.get("filed"),
            }
            for item in units
            if item.get("form") == "10-K" and item.get("fy") >= 2020
        ]

        return recent_revenues
    else:
        print(f"Error fetching data: {response.status_code}")
        return []


if __name__ == "__main__":
    records = fetch_company_facts("0000320193")
    print(f"Extracted {len(records)} annual financial records.")
    print(json.dumps(records[-3:], indent=2))  # Display last 3 years

    with open("sec_financial_summary.json", "w") as f:
        json.dump(records, f, indent=2)