"""Parameter provenance records and YAML configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import yaml


@dataclass(frozen=True)
class ParameterRecord:
    key: str
    symbol: str
    value: float
    unit: str
    category: str
    reference: str
    admissible_range: Optional[Tuple[float, float]]
    rationale: str


HISTORICAL_RECORDS: Dict[str, ParameterRecord] = {
    "beta_N": ParameterRecord(
        "beta_N", "beta_N", 0.055, "1/year", "ASSUMPTION", "",
        (0.03, 0.08), "Effective potential birth rate; not a measured age-specific schedule."
    ),
    "beta_M": ParameterRecord(
        "beta_M", "beta_M", 0.055, "1/year", "ASSUMPTION", "",
        (0.03, 0.08), "Effective potential birth rate; baseline symmetric with Neanderthals."
    ),
    "delta_N": ParameterRecord(
        "delta_N", "delta_N", 0.035, "1/year", "ASSUMPTION", "",
        (0.02, 0.05), "Effective baseline mortality; scenario value."
    ),
    "delta_M": ParameterRecord(
        "delta_M", "delta_M", 0.035, "1/year", "ASSUMPTION", "",
        (0.02, 0.05), "Effective baseline mortality; baseline symmetric with Neanderthals."
    ),
    "w_N": ParameterRecord(
        "w_N", "w_N", 1.0, "weight/person", "ASSUMPTION", "",
        (0.1, 10.0), "Common arbitrary weight unit; only ratios matter."
    ),
    "w_M": ParameterRecord(
        "w_M", "w_M", 1.0, "weight/person", "ASSUMPTION", "",
        (0.1, 10.0), "H0 baseline; H1 varies this ratio."
    ),
    "m_N": ParameterRecord(
        "m_N", "m_N", 2700.0, "kcal/person/day", "ASSUMPTION",
        "Problem-reported adult ranges 3,000-7,000 kcal/day; adult-equivalent extrapolation",
        (2200.0, 3500.0),
        "Illustrative all-age demand; no age/sex composition was supplied to estimate this mean."
    ),
    "m_M": ParameterRecord(
        "m_M", "m_M", 2500.0, "kcal/person/day", "ASSUMPTION",
        "Problem-reported Neanderthal-modern difference 100-350 kcal/day",
        (2000.0, 3000.0),
        "Illustrative mean; the selected difference of 200 is within the problem-reported adult comparison."
    ),
    "ell_N": ParameterRecord(
        "ell_N", "ell_N", 1.0, "km^2/person", "ASSUMPTION", "",
        (0.1, 10.0), "Effective land/habitat access; not binding in the baseline."
    ),
    "ell_M": ParameterRecord(
        "ell_M", "ell_M", 1.0, "km^2/person", "ASSUMPTION", "",
        (0.1, 10.0), "Effective land/habitat access; baseline symmetric."
    ),
    "S_E": ParameterRecord(
        "S_E", "S_E", 6.0e10, "kcal/year", "ASSUMPTION", "",
        (2.0e10, 2.0e11), "Regional food-energy supply supporting order 10^5 persons."
    ),
    "S_L": ParameterRecord(
        "S_L", "S_L", 1.0e6, "km^2", "ASSUMPTION", "",
        (1.0e5, 1.0e7), "Effective land-service supply; not binding in the baseline."
    ),
    "N0": ParameterRecord(
        "N0", "N0", 50000.0, "persons", "ASSUMPTION", "",
        (1.0e4, 1.0e5), "Initial Neanderthal population in the modeled region."
    ),
    "M0": ParameterRecord(
        "M0", "M0", 5000.0, "persons", "ASSUMPTION", "",
        (1.0e3, 2.0e4), "Initial modern-human population; M0/N0=0.1 baseline."
    ),
    "N_ref": ParameterRecord(
        "N_ref", "N_ref", 50000.0, "persons", "ASSUMPTION", "",
        (1.0e4, 1.0e5), "Reference population used to define the extinction threshold."
    ),
    "kappa": ParameterRecord(
        "kappa", "kappa", 0.01, "dimensionless", "ASSUMPTION", "",
        (0.001, 0.1), "Threshold fraction; effective disappearance convention."
    ),
    "t_max": ParameterRecord(
        "t_max", "T_hist", 10000.0, "years", "ASSUMPTION", "",
        (6000.0, 20000.0), "Censoring horizon for compatibility scans."
    ),
}

RSI_RECORDS: Dict[str, ParameterRecord] = {
    "beta_H": ParameterRecord(
        "beta_H", "beta_H", 0.02, "1/year", "ASSUMPTION", "",
        (0.005, 0.04), "Effective human potential growth rate; scenario."
    ),
    "delta_H": ParameterRecord(
        "delta_H", "delta_H", 0.01, "1/year", "ASSUMPTION", "",
        (0.005, 0.02), "Effective human baseline mortality; scenario."
    ),
    "e_H": ParameterRecord(
        "e_H", "e_H", 1.0, "MWh/person/year", "ASSUMPTION", "",
        (0.5, 5.0), "Essential electricity/service energy, not metabolic calories."
    ),
    "ell_H": ParameterRecord(
        "ell_H", "ell_H", 1.0e-4, "km^2/person", "ASSUMPTION", "",
        (1.0e-5, 1.0e-3), "Effective human land-service requirement."
    ),
    "e0": ParameterRecord(
        "e0", "e0", 10000.0, "MWh/hardware-unit/year", "ASSUMPTION", "",
        (5000.0, 20000.0), "Operational energy per hardware unit at q=1."
    ),
    "xi": ParameterRecord(
        "xi", "xi", 0.2, "dimensionless", "ASSUMPTION", "",
        (0.0, 1.0), "Capability-to-energy-efficiency scenario exponent."
    ),
    "ell_A": ParameterRecord(
        "ell_A", "ell_A", 1.0e-4, "km^2/hardware-unit", "ASSUMPTION", "",
        (1.0e-5, 1.0e-3), "Allocable AI land-service requirement."
    ),
    "w_H": ParameterRecord(
        "w_H", "w_H", 1.0, "weight/person", "ASSUMPTION", "",
        (0.1, 10.0), "Human acquisition weight in a common arbitrary utility unit."
    ),
    "w_A0": ParameterRecord(
        "w_A0", "w_A0", 1.0, "weight/hardware-unit", "ASSUMPTION", "",
        (0.1, 10.0), "AI acquisition weight at q=1; baseline neutral."
    ),
    "omega": ParameterRecord(
        "omega", "omega", 0.2, "dimensionless", "ASSUMPTION", "",
        (0.0, 1.0), "Capability-to-bargaining-weight scenario exponent."
    ),
    "L_site": ParameterRecord(
        "L_site", "L_site", 100.0, "km^2", "ASSUMPTION", "",
        (10.0, 1000.0), "Precommitted physical facility land."
    ),
    "L_service": ParameterRecord(
        "L_service", "L_service", 2.0e6, "km^2", "ASSUMPTION", "",
        (1.0e5, 1.0e7), "Allocable land service; disjoint from L_site."
    ),
    "ell_site": ParameterRecord(
        "ell_site", "ell_site", 1.0e-4, "km^2/hardware-unit", "ASSUMPTION", "",
        (1.0e-5, 1.0e-3), "Physical facility footprint per installed unit."
    ),
    "c_build": ParameterRecord(
        "c_build", "c_build", 5000.0, "MWh/hardware-unit", "ASSUMPTION", "",
        (1000.0, 20000.0), "Construction energy per newly installed unit."
    ),
    "rho": ParameterRecord(
        "rho", "rho", 0.1, "dimensionless", "ASSUMPTION", "",
        (0.02, 0.3), "Maximum fixed construction-energy share."
    ),
    "c_H": ParameterRecord(
        "c_H", "c_H", 10000.0, "hardware-units/year", "ASSUMPTION", "",
        (1000.0, 1.0e5), "Human-supported industrial production scale."
    ),
    "c_A": ParameterRecord(
        "c_A", "c_A", 0.5, "1/year", "ASSUMPTION", "",
        (0.05, 2.0), "Autonomous AI production rate at full automation."
    ),
    "H_ref": ParameterRecord(
        "H_ref", "H_ref", 8.0e9, "persons", "ASSUMPTION", "",
        (1.0e9, 8.0e9), "Human production reference population."
    ),
    "M_max": ParameterRecord(
        "M_max", "M_max", 1.0e5, "hardware-units/year", "ASSUMPTION", "",
        (1.0e4, 1.0e6), "Aggregate industrial production ceiling."
    ),
    "r0": ParameterRecord(
        "r0", "r0", 0.2, "1/year", "ASSUMPTION", "",
        (0.05, 1.0), "Desired hardware expansion rate at q=1."
    ),
    "gamma": ParameterRecord(
        "gamma", "gamma", 0.0, "dimensionless", "ASSUMPTION", "",
        (0.0, 1.0), "Capability-to-expansion scenario exponent; zero baseline."
    ),
    "tau_build": ParameterRecord(
        "tau_build", "tau_build", 2.0, "years", "ASSUMPTION", "",
        (0.5, 10.0), "Characteristic site-constrained construction time."
    ),
    "eta": ParameterRecord(
        "eta", "eta", 0.2, "1/year", "ASSUMPTION", "",
        (0.01, 1.0), "Capability improvement parameter."
    ),
    "A_c": ParameterRecord(
        "A_c", "A_c", 1.0e4, "hardware-units", "ASSUMPTION", "",
        (1.0e3, 1.0e6), "R&D saturation scale."
    ),
    "q_max": ParameterRecord(
        "q_max", "q_max", 100.0, "dimensionless", "ASSUMPTION", "",
        (10.0, 1000.0), "Capability ceiling in the bounded scenario."
    ),
    "q0": ParameterRecord(
        "q0", "q0", 1.0, "dimensionless", "ASSUMPTION", "",
        (0.1, 10.0), "Initial capability index."
    ),
    "nu": ParameterRecord(
        "nu", "nu", 2.0, "dimensionless", "ASSUMPTION", "",
        (0.5, 5.0), "Automation-transition shape exponent."
    ),
    "q_c": ParameterRecord(
        "q_c", "q_c", 10.0, "dimensionless", "ASSUMPTION", "",
        (3.0, 20.0), "Automation half-saturation capability."
    ),
    "delta_A": ParameterRecord(
        "delta_A", "delta_A", 0.05, "1/year", "ASSUMPTION", "",
        (0.01, 0.2), "Physical decommissioning/depreciation rate."
    ),
    "mu_A": ParameterRecord(
        "mu_A", "mu_A", 0.5, "1/year", "ASSUMPTION", "",
        (0.0, 2.0), "Additional completed-decommissioning rate under resource shortfall."
    ),
    "E_total": ParameterRecord(
        "E_total", "E_total", 3.0e10, "MWh/year", "ESTIMATE",
        "IEA (2025) 415 TWh = 1.5% of world electricity; rounded world total",
        (1.0e10, 6.0e10), "Global-scale scenario derived from rounded problem-reported data."
    ),
    "A0": ParameterRecord(
        "A0", "A0", 1.0e4, "hardware-units", "ASSUMPTION", "",
        (1.0e3, 1.0e6), "Initial installed AI hardware."
    ),
    "H0": ParameterRecord(
        "H0", "H0", 8.0e9, "persons", "ASSUMPTION", "",
        (1.0e8, 8.0e9), "Initial human population; global-scale scenario."
    ),
    "T": ParameterRecord(
        "T", "T", 100.0, "years", "ASSUMPTION", "",
        (50.0, 150.0), "Study horizon; classification convention."
    ),
    "dt": ParameterRecord(
        "dt", "dt", 0.5, "years", "ASSUMPTION", "",
        (0.25, 2.0), "Output and baseline integration step."
    ),
    "H_ext": ParameterRecord(
        "H_ext", "H_ext", 1.0e6, "persons", "ASSUMPTION", "",
        (1.0e5, 1.0e7), "Effective human extinction threshold."
    ),
    "H_min": ParameterRecord(
        "H_min", "H_min", 1.0e8, "persons", "ASSUMPTION", "",
        (1.0e7, 1.0e9), "Minimum acceptable human population."
    ),
    "s_min": ParameterRecord(
        "s_min", "s_min", 0.8, "dimensionless", "ASSUMPTION", "",
        (0.5, 0.95), "Minimum acceptable human resource adequacy."
    ),
    "W_window": ParameterRecord(
        "W_window", "W_window", 10.0, "years", "ASSUMPTION", "",
        (5.0, 20.0), "Final observation-window length."
    ),
    "p_tol": ParameterRecord(
        "p_tol", "p_tol", 0.0, "dimensionless", "ASSUMPTION", "",
        (0.0, 0.1), "Allowed final-window bad-time fraction."
    ),
}


def read_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if data is not None else {}


def records_to_rows(records: Iterable[ParameterRecord]) -> List[dict]:
    rows = []
    for rec in records:
        rows.append(
            {
                "key": rec.key,
                "symbol": rec.symbol,
                "value": rec.value,
                "unit": rec.unit,
                "category": rec.category,
                "reference": rec.reference,
                "range_min": None if rec.admissible_range is None else rec.admissible_range[0],
                "range_max": None if rec.admissible_range is None else rec.admissible_range[1],
                "rationale": rec.rationale,
            }
        )
    return rows
