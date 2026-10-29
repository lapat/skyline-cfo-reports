import json
import os

def parse_and_save():
    os.makedirs('data/kendall_auction_results', exist_ok=True)

    # 1. Kendall Use Code Data from Stan's email
    kendall_use_codes = [
        {"buyer": "PRIVATE EQUITY GROUP (Bridge)", "use_code": "11", "desc": "Residential Vacant", "certs": 3, "amount": 11452.34, "bid": 5.00},
        {"buyer": "PRIVATE EQUITY GROUP (Bridge)", "use_code": "21", "desc": "Residential Improved (Single)", "certs": 4, "amount": 8588.89, "bid": 5.00},
        {"buyer": "PRIVATE EQUITY GROUP (Bridge)", "use_code": "40", "desc": "Residential Improved (Suburban)", "certs": 120, "amount": 741098.11, "bid": 5.07},
        {"buyer": "PRIVATE EQUITY GROUP (Bridge)", "use_code": "50", "desc": "Commercial Vacant", "certs": 1, "amount": 5163.17, "bid": 4.00},
        {"buyer": "PRIVATE EQUITY GROUP (Bridge)", "use_code": "60", "desc": "Commercial Improved", "certs": 14, "amount": 323763.63, "bid": 4.69},
        {"buyer": "PRIVATE EQUITY GROUP (Bridge)", "use_code": "70", "desc": "Industrial Vacant", "certs": 1, "amount": 29845.97, "bid": 5.00},
        {"buyer": "PRIVATE EQUITY GROUP (Bridge)", "use_code": "80", "desc": "Industrial Improved", "certs": 3, "amount": 18742.76, "bid": 4.63},

        {"buyer": "1095 INVESTMENTS LLC", "use_code": "11", "desc": "Residential Vacant", "certs": 5, "amount": 66813.95, "bid": 5.00},
        {"buyer": "1095 INVESTMENTS LLC", "use_code": "21", "desc": "Residential Improved", "certs": 3, "amount": 8137.77, "bid": 5.00},
        {"buyer": "1095 INVESTMENTS LLC", "use_code": "40", "desc": "Residential Improved", "certs": 37, "amount": 352865.78, "bid": 5.01},
        {"buyer": "1095 INVESTMENTS LLC", "use_code": "60", "desc": "Commercial Improved", "certs": 3, "amount": 31681.20, "bid": 5.39},

        {"buyer": "RAVEN SECURITIES INC (Bass)", "use_code": "21", "desc": "Residential Improved", "certs": 5, "amount": 10974.15, "bid": 4.13},
        {"buyer": "RAVEN SECURITIES INC (Bass)", "use_code": "40", "desc": "Residential Improved", "certs": 37, "amount": 271078.64, "bid": 4.06},
        {"buyer": "RAVEN SECURITIES INC (Bass)", "use_code": "50", "desc": "Commercial Vacant", "certs": 3, "amount": 7680.37, "bid": 5.86},
        {"buyer": "RAVEN SECURITIES INC (Bass)", "use_code": "60", "desc": "Commercial Improved", "certs": 3, "amount": 10161.63, "bid": 4.50}
    ]

    # 2. Kane Class Code Data from Stan's email
    kane_class_codes = [
        {"buyer": "PRIVATE EQUITY GROUP, LLC (Bridge)", "class_code": "11", "desc": "Residential Vacant", "certs": 5, "amount": 25120.28, "bid": 5.31},
        {"buyer": "PRIVATE EQUITY GROUP, LLC (Bridge)", "class_code": "21", "desc": "Residential Improved", "certs": 5, "amount": 14195.75, "bid": 5.00},
        {"buyer": "PRIVATE EQUITY GROUP, LLC (Bridge)", "class_code": "30", "desc": "Farm / Rural", "certs": 10, "amount": 21523.07, "bid": 5.83},
        {"buyer": "PRIVATE EQUITY GROUP, LLC (Bridge)", "class_code": "40", "desc": "Residential Improved", "certs": 545, "amount": 2415225.59, "bid": 5.07},
        {"buyer": "PRIVATE EQUITY GROUP, LLC (Bridge)", "class_code": "60", "desc": "Commercial Improved", "certs": 84, "amount": 968699.44, "bid": 4.67},
        {"buyer": "PRIVATE EQUITY GROUP, LLC (Bridge)", "class_code": "70", "desc": "Industrial Vacant", "certs": 12, "amount": 121317.59, "bid": 4.57},
        {"buyer": "PRIVATE EQUITY GROUP, LLC (Bridge)", "class_code": "80", "desc": "Industrial Improved", "certs": 25, "amount": 733317.93, "bid": 4.57},

        {"buyer": "HEARTLAND TAX AUCTION, LLC", "class_code": "11", "desc": "Residential Vacant", "certs": 2, "amount": 52248.85, "bid": 2.78},
        {"buyer": "HEARTLAND TAX AUCTION, LLC", "class_code": "40", "desc": "Residential Improved", "certs": 317, "amount": 2311547.81, "bid": 2.95},
        {"buyer": "HEARTLAND TAX AUCTION, LLC", "class_code": "60", "desc": "Commercial Improved", "certs": 9, "amount": 329361.29, "bid": 3.33},
        {"buyer": "HEARTLAND TAX AUCTION, LLC", "class_code": "70", "desc": "Industrial Vacant", "certs": 1, "amount": 77620.67, "bid": 3.00},
        {"buyer": "HEARTLAND TAX AUCTION, LLC", "class_code": "80", "desc": "Industrial Improved", "certs": 6, "amount": 279852.23, "bid": 2.51},

        {"buyer": "RAVEN SECURITIES, INC (Bass)", "class_code": "11", "desc": "Residential Vacant", "certs": 6, "amount": 49962.55, "bid": 4.00},
        {"buyer": "RAVEN SECURITIES, INC (Bass)", "class_code": "40", "desc": "Residential Improved", "certs": 99, "amount": 622464.14, "bid": 4.16},
        {"buyer": "RAVEN SECURITIES, INC (Bass)", "class_code": "60", "desc": "Commercial Improved", "certs": 3, "amount": 25411.79, "bid": 5.72}
    ]

    with open('data/kendall_auction_results/kendall_class_codes_2026.json', 'w') as f:
        json.dump(kendall_use_codes, f, indent=2)

    with open('data/kendall_auction_results/kane_class_codes_2026.json', 'w') as f:
        json.dump(kane_class_codes, f, indent=2)

    print("✅ Successfully generated JSON files for Kane and Kendall Class Code breakdowns.")

if __name__ == '__main__':
    parse_and_save()
