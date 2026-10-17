import numpy as np
import pandas as pd

from alpha.uncertainty import (
    probability_summary,
    run_uq,
    sample_parameters,
    wilson_interval,
)


def test_sampling_reproducibility():
    a = sample_parameters("conservative", 5, 123)
    b = sample_parameters("conservative", 5, 123)
    for (ia, pa, da), (ib, pb, db) in zip(a, b):
        assert ia == ib
        assert pa == pb
        assert da.keys() == db.keys()


def test_probability_sum_and_partition():
    samples, results = run_uq("conservative", 3, 7, [0.0, 1.0])
    prob = probability_summary(results)
    assert np.allclose(prob["P_sum"], 1.0)
    assert np.all(prob["n_valid"] + prob["n_failed"] == prob["n_total"])
    allowed = {"extinction", "marginal", "non_marginal", "failed"}
    assert set(results["outcome"].unique()).issubset(allowed)


def test_wilson_interval_bounds():
    lo, hi = wilson_interval(0, 10)
    assert 0.0 <= lo <= hi <= 1.0
    lo, hi = wilson_interval(10, 10)
    assert 0.0 <= lo <= hi <= 1.0
    assert hi >= 0.9
