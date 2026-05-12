import sys
import yaml
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.profile_classifier import classify_profile
from src.gap_analyzer import analyze_gap

DATA_DIR = Path(__file__).parent.parent / "data"
EVAL_PATH = DATA_DIR / "eval" / "test_cases.yaml"
RESULTS_PATH = DATA_DIR / "eval" / "results.json"

def load_test_cases() -> list:
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["test_cases"]

def evaluate_classification(
    test_case: dict,
    classifications: list
) -> dict:
    """Score the classification against expected output."""
    expected_families = test_case["expected"]["top_role_families"]
    expected_confidence = test_case["expected"].get("low_confidence", False)

    # Get top classified families (score > 0.6)
    actual_families = [
        c["family"] for c in classifications
        if c["score"] >= 0.6
    ]
    actual_low_confidence = len(actual_families) == 0

    # Score: did correct families appear?
    if expected_confidence:
        # Expected low confidence — pass if actual is also low confidence
        classification_pass = actual_low_confidence
    else:
        # Check overlap between expected and actual families
        overlap = set(expected_families) & set(actual_families)
        classification_pass = len(overlap) > 0

    return {
        "expected_families": expected_families,
        "actual_families": actual_families,
        "expected_low_confidence": expected_confidence,
        "actual_low_confidence": actual_low_confidence,
        "pass": classification_pass
    }

def skill_matches(expected: str, actual_list: list) -> bool:
    """Fuzzy match — check if expected skill appears in any actual skill."""
    exp_lower = expected.lower()
    exp_words = set(exp_lower.split())
    
    for actual in actual_list:
        actual_lower = actual.lower()
        # Direct substring match
        if exp_lower in actual_lower or actual_lower in exp_lower:
            return True
        # Word overlap match — if 50%+ of expected words appear in actual
        actual_words = set(actual_lower.split())
        overlap = exp_words & actual_words
        if len(overlap) / len(exp_words) >= 0.5:
            return True
    return False

def evaluate_gap_analysis(
    test_case: dict,
    gap_result: dict
) -> dict:
    """Score gap analysis against expected output."""
    expected = test_case["expected"]

    # Check already_have
    already_have_skills = [
        item["skill"].lower()
        for item in gap_result.get("already_have", [])
    ]
    expected_have = [
        s.lower() for s in expected.get(
            "should_appear_in_already_have", []
        )
    ]
    have_hits = sum(
        1 for exp in expected_have
        if skill_matches(exp, already_have_skills)
    )
    have_score = have_hits / len(expected_have) if expected_have else 1.0

    # Check need_to_learn
    need_skills = [
        item["skill"].lower()
        for item in gap_result.get("need_to_learn", [])
    ]
    expected_need = [
        s.lower() for s in expected.get(
            "should_appear_in_need_to_learn", []
        )
    ]
    need_hits = sum(
        1 for exp in expected_need
        if skill_matches(exp, need_skills)
    )
    need_score = need_hits / len(expected_need) if expected_need else 1.0

    # Check readiness
    expected_readiness = expected.get("expected_readiness", "")
    actual_readiness = gap_result.get("overall_readiness", "")
    readiness_pass = expected_readiness == actual_readiness

    # Overall gap score
    gap_score = (have_score + need_score) / 2

    return {
        "have_score": round(have_score, 2),
        "need_score": round(need_score, 2),
        "gap_score": round(gap_score, 2),
        "readiness_expected": expected_readiness,
        "readiness_actual": actual_readiness,
        "readiness_pass": readiness_pass,
        "pass": gap_score >= 0.6 and readiness_pass
    }

def run_eval(max_cases: int = None):
    """Run evaluation against all test cases."""
    test_cases = load_test_cases()
    if max_cases:
        test_cases = test_cases[:max_cases]

    print(f"Running eval on {len(test_cases)} test cases...\n")

    results = []
    classification_passes = 0
    gap_passes = 0
    total_cost = 0.0

    for tc in test_cases:
        tc_id = tc["id"]
        desc = tc["description"]
        profile = tc["profile"]
        domain_pref = tc["expected"].get("domain_preference", "both")

        print(f"── {tc_id}: {desc}")

        # Step 1: Classification
        try:
            classifications = classify_profile(profile)
            class_result = evaluate_classification(tc, classifications)

            status = "✅" if class_result["pass"] else "❌"
            print(f"   Classification {status}: "
                  f"expected {class_result['expected_families']} "
                  f"got {class_result['actual_families']}")

            if class_result["pass"]:
                classification_passes += 1

        except Exception as e:
            print(f"   Classification ERROR: {e}")
            class_result = {"pass": False, "error": str(e)}
            classifications = []

        # Step 2: Gap analysis
        # Use top classified family or first expected family
        qualifying = [
            c for c in classifications if c["score"] >= 0.6
        ]
        if qualifying:
            target_family = qualifying[0]["family"]
        elif tc["expected"]["top_role_families"]:
            target_family = tc["expected"]["top_role_families"][0]
        else:
            target_family = "ml_engineer"  # fallback

        try:
            gap_result = analyze_gap(
                skills_profile=profile,
                target_role_family=target_family,
                domain_preference=domain_pref
            )

            tokens = gap_result.get("_tokens", {})
            cost = tokens.get("cost_usd", 0)
            total_cost += cost

            if "error" not in gap_result:
                gap_eval = evaluate_gap_analysis(tc, gap_result)
                status = "✅" if gap_eval["pass"] else "❌"
                print(f"   Gap analysis {status}: "
                      f"have={gap_eval['have_score']:.0%} "
                      f"need={gap_eval['need_score']:.0%} "
                      f"readiness={gap_eval['readiness_actual']}"
                      f"({'✓' if gap_eval['readiness_pass'] else '✗'})")

                if gap_eval["pass"]:
                    gap_passes += 1
            else:
                print(f"   Gap analysis ERROR: {gap_result['error']}")
                gap_eval = {"pass": False, "error": gap_result["error"]}

        except Exception as e:
            print(f"   Gap analysis ERROR: {e}")
            gap_eval = {"pass": False, "error": str(e)}

        results.append({
            "id": tc_id,
            "description": desc,
            "classification": class_result,
            "gap_analysis": gap_eval,
            "gap_raw": {
                "need_to_learn": gap_result.get("need_to_learn", []) 
                    if "error" not in gap_result else [],
                "already_have": gap_result.get("already_have", [])
                    if "error" not in gap_result else []
            },
            "cost_usd": cost if "cost" in dir() else 0
        })

        print()

    # Summary
    n = len(test_cases)
    print("═" * 60)
    print(f"RESULTS SUMMARY")
    print(f"═" * 60)
    print(f"Classification accuracy: {classification_passes}/{n} "
          f"({classification_passes/n:.0%})")
    print(f"Gap analysis accuracy:   {gap_passes}/{n} "
          f"({gap_passes/n:.0%})")
    print(f"Total cost:              ${total_cost:.4f}")
    print(f"Cost per case:           ${total_cost/n:.4f}")

    # Save results
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_cases": n,
                "classification_passes": classification_passes,
                "classification_accuracy": classification_passes/n,
                "gap_passes": gap_passes,
                "gap_accuracy": gap_passes/n,
                "total_cost_usd": total_cost
            },
            "results": results
        }, f, indent=2)

    print(f"\nDetailed results saved to {RESULTS_PATH}")
    return classification_passes/n, gap_passes/n

if __name__ == "__main__":
    # Run first 3 cases only for quick test
    # Remove max_cases to run all 15
    run_eval()