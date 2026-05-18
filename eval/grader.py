from core.context import FinancialContext

def grade(context: FinancialContext,test_cases:dict)->dict:
    results = {
        "id": test_cases["id"],
        "ticker" : test_cases["ticker"],
        "company_name" : test_cases["company_name"],
        "category": test_cases["category"], 
        "passed" : True,
        "score" : 0,
        "max_score" : 4,
        "grade": "0/4",
        "checks" : {}
    }
    expected_min , expected_max = test_cases["expected_risk_range"]
    overall_risk = context.overall_risk or 0
    risk_in_range = expected_min <= overall_risk <= expected_max

    results['checks']['risk_in_range'] = {
        "passed" : risk_in_range,
        "expected range" : f"{expected_min} - {expected_max}",
        "actual risk" : overall_risk
    }

    if risk_in_range:
        results['score'] += 1

    memo_produced = bool(context.final_memo)
    memo_check = memo_produced == test_cases["expect_memo"]
    results['checks']['memo_produced'] = {
        "passed": memo_check,
        "excepted" : test_cases["expect_memo"],
        "actual" : memo_produced
    }
    if memo_check:
        results['score'] += 1

    if not test_cases["expect_error"]:
        contradictions_found = len(context.contradictions) > 0
        results['checks']['contradictions_found'] = {
            "passed" : contradictions_found,
            "expected" : test_cases["expect_error"],
            "actual" : len(context.contradictions)
        }
        if contradictions_found:
            results['score'] += 1
    else :
        results['checks']['expect_error'] = {
            "passed" : True,
            "expected" : "skipped for error cases",
            "actual" : "skipped"
        }
        results['score'] += 1

    audit_log = len(context.audit_log) > 0
    results['checks']['audit_log_presence'] = {
        "passed" : audit_log,
        "expected" : True,
        "actual" : len(context.audit_log)
    }
    if audit_log:
        results['score'] += 1

    results["passed"] = results['score'] >= 3
    results['grade'] = f"{results["score"]}/{results['max_score']}"
    return results
   
    



