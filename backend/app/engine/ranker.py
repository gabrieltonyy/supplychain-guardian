import numpy as np

from app.schemas.mitigation import SimulatedScenario


CRITERIA_WEIGHTS = {
    "cost_delta": 0.30,
    "lead_time_delta": 0.25,
    "residual_risk": 0.25,
    "onboarding_weeks": 0.10,
    "confidence": 0.10,
}

BENEFIT_CRITERIA = {"confidence"}
COST_CRITERIA = {
    "cost_delta",
    "lead_time_delta",
    "residual_risk",
    "onboarding_weeks",
}


def rank_scenarios(
    scenarios: list[SimulatedScenario],
    weights: dict[str, float] | None = None,
) -> list[tuple[SimulatedScenario, float]]:
    """
    Rank supplier switch scenarios using TOPSIS.

    Higher TOPSIS score means better option.
    """

    if not scenarios:
        return []

    active_weights = weights or CRITERIA_WEIGHTS

    criteria = list(active_weights.keys())

    weight_values = np.array(
        [active_weights[criterion] for criterion in criteria],
        dtype=float,
    )

    matrix = np.array(
        [
            [
                scenario.cost_delta_pct,
                scenario.lead_time_delta_days,
                scenario.residual_risk_score,
                scenario.onboarding_weeks,
                scenario.confidence,
            ]
            for scenario in scenarios
        ],
        dtype=float,
    )

    norms = np.linalg.norm(matrix, axis=0)
    norms[norms == 0] = 1

    normalized_matrix = matrix / norms

    weighted_matrix = normalized_matrix * weight_values

    benefit_mask = np.array(
        [criterion in BENEFIT_CRITERIA for criterion in criteria],
        dtype=bool,
    )

    ideal_best = np.where(
        benefit_mask,
        weighted_matrix.max(axis=0),
        weighted_matrix.min(axis=0),
    )

    ideal_worst = np.where(
        benefit_mask,
        weighted_matrix.min(axis=0),
        weighted_matrix.max(axis=0),
    )

    distance_to_best = np.sqrt(
        ((weighted_matrix - ideal_best) ** 2).sum(axis=1)
    )

    distance_to_worst = np.sqrt(
        ((weighted_matrix - ideal_worst) ** 2).sum(axis=1)
    )

    topsis_scores = distance_to_worst / (
        distance_to_best + distance_to_worst + 1e-9
    )

    ranked = sorted(
        zip(scenarios, topsis_scores.tolist()),
        key=lambda item: item[1],
        reverse=True,
    )

    return ranked