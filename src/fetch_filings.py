import json
import requests


def fetch_company_facts(cik, company_name):
    """Fetches key financial facts from SEC EDGAR API for a given CIK."""
    headers = {"User-Agent": "KalyaniKhandait kalyanik@udel.edu"}

    formatted_cik = str(cik).zfill(10)
    url = (
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{formatted_cik}.json"
    )

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        us_gaap = data.get("facts", {}).get("us-gaap", {})

        # Check all possible SEC XBRL tags for Revenue / Sales
        revenue_keys = [
            "Revenues",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "SalesRevenueNet",
            "TotalRevenuesAndOtherIncome",
        ]

        units = []
        for key in revenue_keys:
            if key in us_gaap:
                units = us_gaap[key].get("units", {}).get("USD", [])
                if units:
                    break

        recent_revenues = []
        seen_years = set()

        for item in units:
            # Filter for 10-K annual reports from 2020 onward
            if (
                item.get("form") == "10-K"
                and item.get("fy", 0) >= 2020
                and item.get("fp") == "FY"
            ):
                fy = item.get("fy")
                if fy not in seen_years:
                    seen_years.add(fy)
                    recent_revenues.append(
                        {
                            "company": company_name,
                            "cik": formatted_cik,
                            "fiscal_year": fy,
                            "revenue_usd": item.get("val"),
                            "filed_date": item.get("filed"),
                        }
                    )

        return recent_revenues
    else:
        print(f"Error fetching data for {company_name}: {response.status_code}")
        return []


if __name__ == "__main__":
    companies = [
        {"name": "Apple", "cik": "0000320193"},
        {"name": "Microsoft", "cik": "0000789019"},
        {"name": "Amazon", "cik": "0001018724"},
        {"name": "Alphabet (Google)", "cik": "0001652044"},
    ]

    all_records = []
    for comp in companies:
        records = fetch_company_facts(comp["cik"], comp["name"])
        print(f"Extracted {len(records)} records for {comp['name']}.")
        all_records.extend(records)

    with open("sec_financial_summary.json", "w") as f:
        json.dump(all_records, f, indent=2)

    print(f"\nTotal Records Saved: {len(all_records)}")