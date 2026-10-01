# Confirmed intent

User confirmed on 2026-10-01.

Tune anomaly_detection_v1, keyword_spotting_v1, streaming_wakeword_v1 and visual_wake_words_v1 using the IC V1/V2 experience. Preserve complete deployed arithmetic in AutoTVM. First obtain one successful FSIM configuration per deployed VTA operator occurrence, measure AutoTVM TSIM and real deployment TSIM, and require each difference to be at most 10%. Only then perform full FSIM search in batches of 100 distinct trials until at least 20 distinct successful configurations per occurrence or search-space exhaustion. Measure every successful configuration on AutoTVM TSIM and select the minimum-cycle configuration. Deploy the selected configurations, verify correctness with exactly one sample, measure real cycles and calculate per-operator useful-MAC utilization.

Consumer: the user's VTA benchmark analysis. Purpose: reproducible schedule selection with cycles representative of deployment. Constraints: unchanged model semantics and geometry, genuine simulator evidence and durable artifacts. Out of scope: retuning IC V1/V2, ten-sample validation, FPGA measurements.
