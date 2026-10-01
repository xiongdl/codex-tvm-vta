# Confirmed intent: IC V2 operator tuning

Confirmed by the user on 2026-10-01 (Asia/Shanghai).

- Outcome: migrate IC V1's complete operator tuning workflow to IC V2 and actually finish tuning every VTA operator.
- Consumer: the repository owner deploying MLPerf Tiny image_classification_v2 on TSIM.
- Motivation: obtain replayable selected schedules whose isolated tuning measurements agree with actual deployment.
- Success: perform FSIM screening, TSIM AutoTVM selection, export self-contained best configurations, deploy IC V2 with those configurations, and validate each VTA occurrence.
- Hard constraint: abs(deployment_cycles - autotvm_best_cycles) / autotvm_best_cycles < 0.10, independently for every occurrence, using identical complete fusion scope and single-call TSIM counting. Exactly 10% fails.
- If a comparison fails, diagnose and correct tuning or deployment rather than accepting a slower substitute merely to pass the comparison.
- Out of scope: tuning other models and FPGA hardware performance validation.

User confirmation: “确认”. The formula and per-occurrence comparison were separately confirmed with “是”.
