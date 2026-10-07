# EN 10204 — Material Certificate Reference

## What Is EN 10204?

EN 10204:2004 is the European standard for **"Metallic products – Types of inspection documents"**. It defines what certification a manufacturer must provide when supplying metallic products (bars, pipes, plates, forgings, castings, etc.). It supersedes the older DIN 50 049 standard and is universally required on oil & gas, chemical, and power generation projects globally.

---

## Certificate Types

| Type | Name | Test Results | Who Signs | Typical Use |
|---|---|---|---|---|
| **2.1** | Declaration of Compliance | None | Manufacturer | Non-critical structural parts, supports, gaskets |
| **2.2** | Test Report | Non-specific (batch/typical) | Manufacturer | Commercial structural steel |
| **3.1** | Inspection Certificate | Specific per heat | Manufacturer QA (independent of production) | Oil & gas, power, chemical plant — **most common** |
| **3.2** | Inspection Certificate | Specific per heat | Manufacturer QA **+** independent 3rd party | Subsea, nuclear, HP/HT, aerospace |

> **3.1 is the default expectation** on any purchase order that says "MTC required" in oil & gas and industrial projects.

### 3.1 vs 3.2 — Key Differences

| Aspect | 3.1 | 3.2 |
|---|---|---|
| Third-party witness | No | Yes (SGS, BV, Lloyd's, TÜV, DNV, etc.) |
| Cost impact | Moderate | Highest (+inspection fees) |
| Lead time | +1–2 weeks | +2–4 weeks |
| Required by | ASME B31.3, NACE MR0175 | DNV-OS-F101, NORSOK, ASME Sec. III |

---

## EN 10204 3.1 — Required Data Fields

### 1. Document Header

| Field | Description | Example |
|---|---|---|
| Certificate type | Must state "EN 10204 3.1" or "DIN EN 10204/01.05 3.1" | `BSEN 10204:2004 3.1` |
| Certificate number | Unique cert ID issued by manufacturer/distributor | `EUR-472273`, `22/1454` |
| Issue date | Date of certificate | `03-Sep-24` |
| Page numbering | "X of Y" — defines how many pages are part of this cert | `Page: 1/2` |
| Issuer name & address | Manufacturer or authorised distributor | `VDM Metals GmbH, Werdohl, Germany` |

### 2. Order & Customer Details

| Field | Description | Example |
|---|---|---|
| Customer name & address | Purchaser receiving the material | `Aarbakke AS, Jaervegen 142, Norway` |
| Purchase order number | Customer PO reference | `1002-PO-013388` |
| Sales/internal order number | Manufacturer's own order reference | `SO-EUR-720712-1` |
| Customer order/ref number | Customer-side reference | `105320-1` |

### 3. Product Description

| Field | Description | Example |
|---|---|---|
| Product form | Bar, pipe, plate, forging, casting, ring, etc. | `Bar, round, hot rolled, annealed, machined` |
| Material grade / UNS | Trade name, UNS number, EN designation | `Alloy 625 / UNS N06625`, `ASTM A182 F51` |
| Material specification | Full standard reference | `ASTM B446-19`, `ASTM A995 & MDS D56 rev 5` |
| Dimensions | OD × wall thickness × length, or OD × height etc. | `101.6 mm Ø × 1000 mm long` |
| Number of pieces | Quantity | `1` |
| Weight | Per piece or total | `714 kg` |
| Heat / Cast number | Unique melt identifier — **core traceability field** | `329277`, `EZ17` |
| Lot / Batch number | Groups items from same heat processed together | `105548658` |
| Melt practice | How the steel was made | `VIM/ESR`, `AOD`, `Induction furnace` |

### 4. Chemical Analysis (Cast / Ladle Analysis)

Reported as **weight %** for each element. Must show:
- Actual measured values for the specific heat
- Specification min/max limits for comparison

**Common elements by material family:**

| Element | Symbol | Carbon Steel | Stainless / Duplex | Ni-alloys (625, 825) |
|---|---|---|---|---|
| Carbon | C | ✅ | ✅ | ✅ |
| Manganese | Mn | ✅ | ✅ | ✅ |
| Silicon | Si | ✅ | ✅ | ✅ |
| Phosphorus | P | ✅ | ✅ | ✅ |
| Sulfur | S | ✅ | ✅ | ✅ |
| Chromium | Cr | sometimes | ✅ | ✅ |
| Nickel | Ni | — | ✅ | ✅ (balance) |
| Molybdenum | Mo | — | ✅ | ✅ |
| Nitrogen | N | — | ✅ duplex | — |
| Niobium + Tantalum | Nb+Ta | — | — | ✅ 625 |
| Cobalt | Co | — | — | ✅ |
| Iron | Fe | balance | balance | ✅ |

> Some certs include both **ladle analysis** (from melt) and **check/product analysis** (from finished product). Both are valid; ladle is more common.

**Example — Alloy 625 heat 329277:**

| C | Si | Mn | P | S | Cr | Mo | Ni | Al | Ti | Nb+Ta | Co | Fe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.022 | 0.18 | 0.08 | 0.006 | 0.001 | 22.27 | 9.12 | 59.80 | 0.23 | 0.34 | 3.40 | 0.02 | 4.44 |

### 5. Mechanical Properties

#### Tensile Test

| Field | Unit | Description |
|---|---|---|
| Test standard | — | e.g. `ASTM E8/E8M-22`, `ASTM A370` |
| Test temperature | °C | Usually room temp (20–21°C) |
| Yield strength (0.2% proof) | MPa | `Rp0.2` — must meet spec minimum |
| Tensile strength (UTS) | MPa | `Rm` — must meet spec range |
| Elongation | % | `A%` — ductility, must meet spec minimum |
| Reduction of area | % | `Z%` — toughness indicator |
| Test piece location | — | `1/4t`, `1/2t`, `surface` |
| Test direction | — | `Longitudinal`, `Transversal` |

#### Impact Test (Charpy V-notch)

| Field | Unit | Notes |
|---|---|---|
| Test standard | — | `ASTM E23`, `ISO 148` |
| Test temperature | °C | e.g. `-46°C`, `-60°C` |
| Absorbed energy | Joules | 3 individual values + average reported |
| Lateral expansion | mm | Optional |
| Shear fracture | % | Optional |

#### Hardness

| Field | Notes |
|---|---|
| Method | HBW (Brinell), HRC (Rockwell), HV (Vickers) |
| Location | Surface, 1/4t, 1/2t |
| Values | Individual readings + average |
| NACE limit | Max 22 HRC / 250 HBW for sour service |

### 6. Heat Treatment

| Field | Example |
|---|---|
| Treatment type | `Anneal`, `Solution Anneal`, `Normalize + Temper`, `Quench + Temper` |
| Temperature | `920°C`, `1060°C`, `1120°C` |
| Soak time | `0h 30m`, `min 1/2 h/inch` |
| Cooling method | `Water Quench`, `Air Cool`, `Furnace Cool` |
| Transfer time | For water quench — time from furnace to quench |
| Quench bath temp | Start and end water temperature (e.g. `start 29°C, end 29°C, max 30°C`) |

### 7. Additional Tests (Supplementary — not always present)

| Test | Standard | What it checks |
|---|---|---|
| Grain size | `ASTM E112` | Austenite grain size number |
| Corrosion test | `ASTM G28-A`, `ASTM G48-A` | Intergranular / pitting corrosion resistance |
| Ferrite content | `ASTM E562` or ferritoscope | Dual-phase balance in duplex steels |
| PREN | Calculated | Pitting Resistance Equivalent Number for duplex |
| Macroetch | `ASTM A604` | Internal soundness of forgings |
| Ultrasonic (UT) | `ASTM A388`, `API 6A` | Internal defects — pass/fail |
| Liquid Penetrant (PT/LPT) | `ASTM E165`, `ASME V` | Surface cracks — pass/fail |
| Magnetic Particle (MT) | `ASTM E709` | Surface/near-surface defects — ferritic only |
| Dimensional / Visual | MSS-SP-55, project spec | Geometry conformance |

### 8. Conformance Statement & Signatures

| Field | Notes |
|---|---|
| Conformance statement | Formal text certifying material meets all requirements |
| Authorised signatory | Name + title of QA representative independent of production |
| Inspection agency | For 3.2: third-party body name, inspector name, stamp |
| Date of release | Date cert was signed/issued |

---

## Traceability Chain

```
Steel melt → Heat number assigned
    ↓
Billet / ingot produced → Heat number stamped on product
    ↓
Finished product (bar, pipe, forging) → Heat number maintained
    ↓
MTC issued → Heat number links cert to physical product
    ↓
Purchase order + packing list → Heat number on shipping docs
    ↓
Installation → Heat number recorded in as-built documentation
```

> **Rule**: If a piece is cut or machined and the heat number marking is removed, it must be transferred before removing the original. Failure = non-conformance.

---

## Document Structure in Practice

Most EN 10204 3.1 cert packages consist of:

| Document | Pages | Contains |
|---|---|---|
| **Primary cert** (manufacturer) | 1–3 | All mandatory fields above — chemistry, mechanical, heat treatment, conformance |
| Hardness test report | 1–2 | Individual hardness readings, equipment calibration |
| UT / NDT report | 1–2 | Scan results, probe data, inspector qualification |
| Corrosion test report | 1 | Corrosion rate, weight loss, pitting assessment |
| Metallographic report | 1 | Microstructure images + grain size assessment |
| NDE personnel roster | 1 | Inspector qualifications and PCN/ASNT levels |
| Scan plan | 1 | UT coverage diagram |

> **Only the primary cert (pages 1–3) contains EN 10204 required data. Everything else is a supplementary enclosure.**

---

## Observations from Sample Documents

| Cert | Type | Issuer | Material | Multi-heat? | Language | Pages (cert only) |
|---|---|---|---|---|---|---|
| EUR-472273 | 3.1 | Howco (distributor) + VDM Metals | Alloy 625 / UNS N06625 | No (1 heat: 329277) | English | 3 of 11 |
| MELESI MA-00351 | 3.1 | A. Melesi (forging manufacturer) | ASTM A182 F51/F60 (Duplex) | Yes (3 heats) | IT/EN/FR | 1 of ~8 |
| FMT-22-1454 | 3.1 | Aianox (casting manufacturer) | ASTM A995 6A / J93380 (Super Duplex) | Yes (4 heats) | ES/EN | 2 of ~5 |

### Key Parsing Challenges

| Challenge | Description |
|---|---|
| Multi-heat certs | Melesi and Aianox report chemistry and mechanical properties for multiple heats in one table — parser must handle rows per heat |
| Multi-language | Italian, Spanish, French field labels alongside English — field names vary |
| Distributor wrap | EUR-472273 has a Howco cover cert summarising VDM's primary cert — same data appears twice (different precision) |
| Table fragmentation | Long tables often split across columns or rows merge unexpectedly in OCR output |
| Boilerplate hallucination | Repeated small-print footers (company name, management board) are prone to OCR hallucination — not data fields |
| Page markers | Format varies: `1/1`, `Page: 1/2`, `Pag 1 of 2`, `Sheet 1/1` — all equivalent |

---

## Fields Needed for Structured Extraction (EN 10204 3.1)

Minimum structured output per cert:

```json
{
  "cert_number": "",
  "cert_type": "3.1",
  "issue_date": "",
  "issuer": "",
  "customer": "",
  "purchase_order": "",
  "product": {
    "form": "",
    "grade": "",
    "uns": "",
    "specification": [],
    "dimensions": "",
    "quantity": 0,
    "heat_numbers": []
  },
  "melt_practice": "",
  "chemical_analysis": [
    { "heat": "", "C": 0, "Si": 0, "Mn": 0, "P": 0, "S": 0, "Cr": 0, "Ni": 0, "Mo": 0, "Fe": 0 }
  ],
  "mechanical_properties": [
    {
      "heat": "",
      "test": "tensile",
      "yield_mpa": 0,
      "uts_mpa": 0,
      "elongation_pct": 0,
      "reduction_area_pct": 0
    }
  ],
  "impact_test": [
    { "heat": "", "temp_c": 0, "energy_j": [] }
  ],
  "hardness": [
    { "heat": "", "method": "HBW", "values": [] }
  ],
  "heat_treatment": {
    "type": "",
    "temp_c": 0,
    "soak": "",
    "cooling": ""
  },
  "additional_tests": [],
  "conforming": true,
  "signatory": ""
}
```
