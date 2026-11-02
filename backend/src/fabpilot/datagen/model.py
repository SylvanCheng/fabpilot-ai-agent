"""Static fab model: products, route template, equipment fleet, parameter specs.

All names are generic and invented. Nothing here comes from a real fab.
"""

from dataclasses import dataclass

# equipment_type -> (module, fleet size)
EQUIPMENT_FLEET: dict[str, tuple[str, int]] = {
    "WET": ("CLEAN", 2),
    "FURNACE": ("DIFF", 3),
    "SCANNER": ("LITHO", 3),
    "ETCH": ("ETCH", 4),
    "CMP": ("CMP", 2),
    "IMPLANTER": ("IMPLANT", 2),
    "CVD": ("THIN_FILM", 3),
    "PVD": ("THIN_FILM", 2),
    "THK": ("METRO", 2),
    "CDSEM": ("METRO", 2),
    "INSPECTION": ("METRO", 2),
}


@dataclass(frozen=True)
class StepTemplate:
    name: str
    equipment_type: str


@dataclass(frozen=True)
class ParamTemplate:
    """A parameter measured at `measure_step`, physically driven by `source_step`."""

    name: str
    measure_step: str
    source_step: str
    unit: str
    target: float
    lsl: float
    usl: float
    sigma: float  # within-process noise
    tool_sigma: float  # tool-to-tool offset spread


ROUTE_TEMPLATE: list[StepTemplate] = [
    StepTemplate("WAFER START CLEAN", "WET"),
    StepTemplate("PAD OXIDATION", "FURNACE"),
    StepTemplate("PAD OX THK MEAS", "THK"),
    StepTemplate("STI LITHO", "SCANNER"),
    StepTemplate("STI ETCH", "ETCH"),
    StepTemplate("STI CMP", "CMP"),
    StepTemplate("STI STEP HEIGHT MEAS", "THK"),
    StepTemplate("WELL IMPLANT", "IMPLANTER"),
    StepTemplate("WELL ANNEAL", "FURNACE"),
    StepTemplate("GATE OXIDATION", "FURNACE"),
    StepTemplate("POLY DEPO", "CVD"),
    StepTemplate("POLY LITHO", "SCANNER"),
    StepTemplate("POLY ETCH", "ETCH"),
    StepTemplate("POLY CD MEAS", "CDSEM"),
    StepTemplate("POLY DEFECT INSP", "INSPECTION"),
    StepTemplate("SD IMPLANT", "IMPLANTER"),
    StepTemplate("SALICIDE", "PVD"),
    StepTemplate("ILD DEPO", "CVD"),
    StepTemplate("ILD CMP", "CMP"),
    StepTemplate("ILD THK MEAS", "THK"),
    StepTemplate("CONTACT ETCH", "ETCH"),
    StepTemplate("M1 DEPO", "PVD"),
    StepTemplate("M1 ETCH", "ETCH"),
    StepTemplate("FINAL DEFECT INSP", "INSPECTION"),
    StepTemplate("PASSIVATION", "CVD"),
]

PARAMS: list[ParamTemplate] = [
    ParamTemplate(
        "PAD_OX_THK", "PAD OX THK MEAS", "PAD OXIDATION", "nm", 10.0, 9.0, 11.0, 0.15, 0.1
    ),
    ParamTemplate(
        "STI_STEP_HEIGHT", "STI STEP HEIGHT MEAS", "STI CMP", "nm", 20.0, 10.0, 30.0, 2.0, 1.5
    ),
    ParamTemplate("POLY_CD", "POLY CD MEAS", "POLY ETCH", "nm", 55.0, 50.0, 60.0, 0.8, 0.6),
    ParamTemplate("ILD_THK", "ILD THK MEAS", "ILD CMP", "nm", 500.0, 470.0, 530.0, 6.0, 4.0),
]

INSPECTION_STEPS = {"POLY DEFECT INSP", "FINAL DEFECT INSP"}


@dataclass(frozen=True)
class ProductTemplate:
    product_id: str
    name: str
    node: str
    gross_die: int
    route_code: str


PRODUCTS: list[ProductTemplate] = [
    ProductTemplate("PRD-A", "Demo Logic A", "55nm", 620, "A"),
    ProductTemplate("PRD-B", "Demo Power B", "110nm", 1180, "B"),
]

# WM-811K failure-pattern labels, reused so synthetic yield can later be joined with the
# public wafer-map classifier.
MAP_PATTERNS = [
    "Center",
    "Donut",
    "Edge-Loc",
    "Edge-Ring",
    "Loc",
    "Near-full",
    "Random",
    "Scratch",
]
