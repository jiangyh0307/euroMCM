"""Correct exploration labels on stored plots without changing or re-simulating data."""
import pandas as pd
from run_uq import FIG, TAB, _style, figure6, figure_sensitivity, figure_structural


def main():
    _style()
    figure6(pd.read_csv(TAB / "uq_probabilities.csv"),
            FIG / "fig6_uq_probabilities.png", FIG / "fig6_uq_probabilities.pdf", 100)
    figure_sensitivity(pd.read_csv(TAB / "uq_sensitivity.csv"),
                       FIG / "figS_uq_sensitivity.png", FIG / "figS_uq_sensitivity.pdf")
    figure_structural(pd.read_csv(TAB / "structural_robustness_summary.csv"),
                      FIG / "figS_structural_robustness.png",
                      FIG / "figS_structural_robustness.pdf",
                      title="Earlier broad exploratory aggressive library",
                      note="Stored exploratory data; finite-grid safety is not a global or full numerical certificate.")


if __name__ == "__main__":
    main()
