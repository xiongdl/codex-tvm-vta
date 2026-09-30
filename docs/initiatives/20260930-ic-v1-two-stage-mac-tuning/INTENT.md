# Confirmed intent

User confirmed the complete intent on 2026-09-30, with these corrections incorporated.

- Optimize every IC V1 workload through FSIM AutoTVM followed by TSIM measurement of every distinct successful FSIM configuration.
- Search FSIM in increments of 100 trials until at least 20 distinct successful schedules exist or the entire configuration space is exhausted. No fixed 200-trial limit.
- FSIM measurement timeout: 60 seconds. TSIM measurement timeout: 120 seconds.
- Tuning computation must match real model deployment, including complete fusion semantics. Resolve encountered local RPC errors and permission problems.
- Tuning Python and optimal results belong in image_classification_v1/tune/. Intermediate artifacts belong in image_classification_v1/build/.
- Modify the repository's existing scripts/mac_utilization.py to consume real deployment results and report whole-model MAC utilization independently of model identity.
- Compare deployment cycles against TSIM AutoTVM cycles for each operator; relative difference must be at most 10%. Report actual results to the user.
- Scope: actual tuning and deployment validation for IC V1; generic reporting for other models. Do not tune other models or change model assets, quantization, or hardware geometry.

Consumer: the user evaluating VTA MAC efficiency. Success requires runtime evidence, not only implementation or unit tests.
