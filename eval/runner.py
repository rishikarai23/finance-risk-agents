import asyncio
import json
from datetime import datetime
from agents.orchestrator import run as orchestrator_run
from eval.test_cases import TEST_CASES
from eval.grader import grade


async def run_single_test(test_case: dict) -> dict:
    """Runs one test case and grades it."""
    print(f"  Running {test_case['id']} — {test_case['ticker']}...")

    try:
        context = await orchestrator_run(
            ticker=test_case["ticker"],
            company_name=test_case["company_name"],
        )
        result = grade(context, test_case)
        result["error"] = None

    except Exception as e:
        result = {
            "id": test_case["id"],
            "ticker": test_case["ticker"],
            "category": test_case["category"],
            "passed": test_case["expect_error"],
            "score": 4 if test_case["expect_error"] else 0,
            "max_score": 4,
            "grade": "4/4" if test_case["expect_error"] else "0/4",
            "error": str(e),
            "checks": {}
        }

    return result


async def run_eval(categories: list = None) -> dict:
   
    test_cases = TEST_CASES
    if categories:
        test_cases = [t for t in TEST_CASES if t["category"] in categories]

    print(f"Running {len(test_cases)} test cases...")

    results = []
    for test_case in test_cases:
        result = await run_single_test(test_case)
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  {status} {result['id']} — {result['grade']}")

    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    pass_rate = round(passed / total * 100, 1)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": pass_rate,
        "by_category": {},
        "results": results
    }

    # Grade by category
    for category in ["baseline", "ambiguous", "adversarial"]:
        cat_results = [r for r in results if r["category"] == category]
        if cat_results:
            cat_passed = sum(1 for r in cat_results if r["passed"])
            summary["by_category"][category] = {
                "passed": cat_passed,
                "total": len(cat_results),
                "pass_rate": round(cat_passed / len(cat_results) * 100, 1)
            }

    print(f"Total: {passed}/{total} passed ({pass_rate}%)")
    for cat, stats in summary["by_category"].items():
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({stats['pass_rate']}%)")

    with open("eval/results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to eval/results.json")

    return summary


if __name__ == "__main__":
    asyncio.run(run_eval())

