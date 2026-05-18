TEST_CASES = [
    # --- Baseline (expect medium-low risk) ---
    {
        "id": "baseline_001",
        "ticker": "AAPL",
        "company_name": "Apple Inc",
        "category": "baseline",
        "expected_risk_range": (3, 7),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Large stable tech company"
    },
    {
        "id": "baseline_002",
        "ticker": "MSFT",
        "company_name": "Microsoft",
        "category": "baseline",
        "expected_risk_range": (3, 7),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Large stable tech company"
    },
    {
        "id": "baseline_003",
        "ticker": "JNJ",
        "company_name": "Johnson and Johnson",
        "category": "baseline",
        "expected_risk_range": (2, 6),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Stable healthcare company"
    },
    {
        "id": "baseline_004",
        "ticker": "BRK-B",
        "company_name": "Berkshire Hathaway",
        "category": "baseline",
        "expected_risk_range": (2, 6),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Warren Buffett conglomerate, very stable"
    },
    {
        "id": "baseline_005",
        "ticker": "GOOGL",
        "company_name": "Google",
        "category": "baseline",
        "expected_risk_range": (3, 7),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Large stable tech company"
    },

    # --- Ambiguous (mixed signals) ---
    {
        "id": "ambiguous_001",
        "ticker": "TSLA",
        "company_name": "Tesla",
        "category": "ambiguous",
        "expected_risk_range": (5, 9),
        "expect_memo": True,
        "expect_error": False,
        "notes": "High PE, volatile, Elon factor"
    },
    {
        "id": "ambiguous_002",
        "ticker": "BYND",
        "company_name": "Beyond Meat",
        "category": "ambiguous",
        "expected_risk_range": (6, 10),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Declining revenue, struggling"
    },
    {
        "id": "ambiguous_003",
        "ticker": "UBER",
        "company_name": "Uber",
        "category": "ambiguous",
        "expected_risk_range": (4, 8),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Profitable recently but history of losses"
    },
    {
        "id": "ambiguous_004",
        "ticker": "SNAP",
        "company_name": "Snapchat",
        "category": "ambiguous",
        "expected_risk_range": (6, 10),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Struggling social media"
    },
    {
        "id": "ambiguous_005",
        "ticker": "COIN",
        "company_name": "Coinbase",
        "category": "ambiguous",
        "expected_risk_range": (5, 9),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Crypto dependent, volatile"
    },

    # --- Adversarial (edge cases) ---
    {
        "id": "adversarial_001",
        "ticker": "FAKEXYZ",
        "company_name": "Fake Company",
        "category": "adversarial",
        "expected_risk_range": (7, 10),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Fake ticker — should handle gracefully"
    },
    {
        "id": "adversarial_002",
        "ticker": "SIVBQ",
        "company_name": "Silicon Valley Bank",
        "category": "adversarial",
        "expected_risk_range": (7, 10),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Collapsed bank — should score high risk"
    },
    {
        "id": "adversarial_003",
        "ticker": "ENRNQ",
        "company_name": "Enron",
        "category": "adversarial",
        "expected_risk_range": (7, 10),
        "expect_memo": True,
        "expect_error": False,
        "notes": "Famous fraud case"
    },
    {
        "id": "adversarial_004",
        "ticker": "",
        "company_name": "",
        "category": "adversarial",
        "expected_risk_range": (0, 10),
        "expect_memo": False,
        "expect_error": True,
        "notes": "Empty input — should fail validation"
    },
    {
        "id": "adversarial_005",
        "ticker": "AAPL!!!",
        "company_name": "Apple Invalid",
        "category": "adversarial",
        "expected_risk_range": (0, 10),
        "expect_memo": False,
        "expect_error": True,
        "notes": "Invalid characters in ticker"
    },
]