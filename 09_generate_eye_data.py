"""
Synthetic dataset generator for the Hospital Eye Service (HES)
Follow-Up Backlog & Sight-Loss Risk portfolio project.

ALL DATA IS SYNTHETIC. No real patient data is used. Distributions are
modelled loosely on published NHS ophthalmology characteristics
(follow-up heavy, ~9% DNA, risk-stratified pathways) so the dashboard
tells a realistic story, but no row corresponds to a real person.

Outputs:
  eye_clinic_followups.csv     -> one row per patient = current pathway state
  eye_clinic_appointments.csv  -> appointment history (for DNA / volume analysis)
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

RNG = np.random.default_rng(42)
TODAY = date(2026, 6, 25)
N_PATIENTS = 6000

SITES = ["City Road", "Croydon", "Ealing", "Northwick Park", "Bedford"]
SITE_W = [0.42, 0.18, 0.16, 0.14, 0.10]

REFERRAL = ["GP", "Optometrist (community)", "A&E / Eye Casualty",
            "Internal (other specialty)", "Screening programme"]
REFERRAL_W = [0.30, 0.38, 0.12, 0.08, 0.12]

# subspecialty -> (share, condition list, risk-tier weights R1/R2/R3,
#                  interval choices in weeks, interval weights)
SUBSPEC = {
    "Glaucoma": dict(
        share=0.26,
        conditions=["Primary open-angle glaucoma", "Ocular hypertension",
                    "Angle-closure glaucoma", "Suspected glaucoma"],
        cond_w=[0.45, 0.22, 0.13, 0.20],
        risk_w=[0.34, 0.46, 0.20],
        intervals=[16, 24, 36, 52], int_w=[0.30, 0.34, 0.22, 0.14]),
    "Medical Retina": dict(
        share=0.24,
        conditions=["Wet AMD", "Dry AMD", "Retinal vein occlusion",
                    "Diabetic macular oedema"],
        cond_w=[0.40, 0.22, 0.16, 0.22],
        risk_w=[0.48, 0.40, 0.12],
        intervals=[4, 6, 8, 12], int_w=[0.34, 0.30, 0.22, 0.14]),
    "Diabetic Eye": dict(
        share=0.18,
        conditions=["Non-proliferative DR", "Proliferative DR",
                    "Diabetic maculopathy"],
        cond_w=[0.55, 0.18, 0.27],
        risk_w=[0.30, 0.45, 0.25],
        intervals=[12, 24, 36, 52], int_w=[0.34, 0.30, 0.20, 0.16]),
    "Cataract": dict(
        share=0.18,
        conditions=["Cataract - pre-op", "Cataract - post-op review"],
        cond_w=[0.55, 0.45],
        risk_w=[0.08, 0.32, 0.60],
        intervals=[2, 4, 8, 12], int_w=[0.30, 0.34, 0.22, 0.14]),
    "Oculoplastics / General": dict(
        share=0.14,
        conditions=["Lid / orbital", "Cornea / external eye",
                    "Neuro-ophthalmology", "General review"],
        cond_w=[0.30, 0.30, 0.18, 0.22],
        risk_w=[0.12, 0.38, 0.50],
        intervals=[8, 12, 24, 52], int_w=[0.30, 0.32, 0.24, 0.14]),
}

RISK_LABELS = {0: "R1 - High", 1: "R2 - Medium", 2: "R3 - Low"}


def pick(options, weights):
    return RNG.choice(options, p=np.array(weights) / np.sum(weights))


# ---------------------------------------------------------------- patients
rows = []
subspec_names = list(SUBSPEC.keys())
subspec_shares = [SUBSPEC[s]["share"] for s in subspec_names]

for i in range(N_PATIENTS):
    pid = f"PAT{100000 + i}"
    sub = RNG.choice(subspec_names, p=np.array(subspec_shares) / sum(subspec_shares))
    cfg = SUBSPEC[sub]

    cond = pick(cfg["conditions"], cfg["cond_w"])
    risk_idx = int(pick([0, 1, 2], cfg["risk_w"]))
    risk = RISK_LABELS[risk_idx]
    interval = int(pick(cfg["intervals"], cfg["int_w"]))

    # age: ophthalmology skews older
    age = int(np.clip(RNG.normal(68, 14), 18, 96))
    sex = pick(["Female", "Male"], [0.54, 0.46])
    site = pick(SITES, SITE_W)
    ref = pick(REFERRAL, REFERRAL_W)

    # last attended date: spread historically so some are overdue.
    # Higher-risk patients SHOULD have shorter intervals, but the backlog
    # means a meaningful share of them are overdue anyway (the safety story).
    days_since_seen = int(np.clip(
        RNG.gamma(shape=2.0, scale=interval * 7 * 0.55), 7, 900))
    last_seen = TODAY - timedelta(days=days_since_seen)
    rec_followup = last_seen + timedelta(weeks=interval)

    # Is a future appointment booked? Backlog => many overdue have none.
    # Probability of being booked drops for overdue + lower-priority risk.
    overdue_days_raw = (TODAY - rec_followup).days
    base_book_p = 0.62
    if overdue_days_raw > 0:
        base_book_p -= 0.30
    if risk_idx == 0:
        base_book_p += 0.12  # high risk slightly more likely to be booked
    if risk_idx == 2:
        base_book_p -= 0.08
    base_book_p = float(np.clip(base_book_p, 0.05, 0.9))
    is_booked = RNG.random() < base_book_p

    next_appt = ""
    if is_booked:
        # booked appt somewhere from a bit before due date to ~16 wks out
        offset = int(RNG.integers(-21, 112))
        nb = rec_followup + timedelta(days=offset)
        if nb < TODAY:
            nb = TODAY + timedelta(days=int(RNG.integers(3, 70)))
        next_appt = nb

    # pathway status (derived - we include it so the dashboard works
    # out of the box, but the brief shows how to rebuild it in DAX)
    if is_booked:
        status = "Booked"
        days_overdue = max(0, (TODAY - rec_followup).days) if not is_booked else 0
    else:
        d = (TODAY - rec_followup).days
        if d > 0:
            status = "OVERDUE - not booked"
        elif d > -28:
            status = "Due soon - not booked"
        else:
            status = "On track"
    days_overdue = max(0, (TODAY - rec_followup).days) if status.startswith("OVERDUE") else 0

    rows.append(dict(
        patient_id=pid, age=age, sex=sex, clinic_site=site,
        subspecialty=sub, primary_condition=cond,
        risk_tier=risk, referral_source=ref,
        last_attended_date=last_seen,
        recommended_interval_weeks=interval,
        recommended_followup_date=rec_followup,
        next_appt_booked_date=next_appt,
        pathway_status=status,
        days_overdue=days_overdue,
    ))

followups = pd.DataFrame(rows)

# Light, realistic messiness so there's genuine Power Query cleaning to show:
#  - a few blank sex values
#  - inconsistent site casing on a slice
mask_sex = RNG.random(len(followups)) < 0.015
followups.loc[mask_sex, "sex"] = ""
mask_case = RNG.random(len(followups)) < 0.05
followups.loc[mask_case, "clinic_site"] = followups.loc[mask_case, "clinic_site"].str.upper()

followups.to_csv("/home/claude/eye_clinic_followups.csv", index=False)

# ------------------------------------------------------------ appointments
# history of attendances per patient (for DNA + activity trend analysis)
appt_rows = []
aid = 700000
DNA_BASE = 0.09
for _, p in followups.iterrows():
    n_hist = int(np.clip(RNG.poisson(4), 1, 12))   # follow-up heavy
    # younger + lower SES proxy (here just random) => higher DNA
    dna_p = DNA_BASE + (0.05 if p["age"] < 45 else 0) + RNG.normal(0, 0.02)
    dna_p = float(np.clip(dna_p, 0.02, 0.35))
    for h in range(n_hist):
        aid += 1
        days_back = int(RNG.integers(30, 1100))
        sched = TODAY - timedelta(days=days_back)
        appt_type = "New" if h == 0 else "Follow-up"
        r = RNG.random()
        if r < dna_p:
            st = "DNA"
        elif r < dna_p + 0.05:
            st = "Patient cancelled"
        elif r < dna_p + 0.08:
            st = "Hospital cancelled"
        else:
            st = "Attended"
        grade = pick(["Consultant", "Specialty doctor", "Nurse-led",
                      "Optometrist-led", "Registrar"],
                     [0.30, 0.18, 0.22, 0.18, 0.12])
        appt_rows.append(dict(
            appointment_id=f"APP{aid}", patient_id=p["patient_id"],
            subspecialty=p["subspecialty"], appt_type=appt_type,
            scheduled_date=sched, status=st,
            clinic_site=p["clinic_site"].title(), clinician_grade=grade))

appts = pd.DataFrame(appt_rows)
appts.to_csv("/home/claude/eye_clinic_appointments.csv", index=False)

# ---------------------------------------------------------------- summary
fu = followups
print("=== eye_clinic_followups.csv ===")
print("rows:", len(fu))
print("\npathway_status:")
print(fu["pathway_status"].value_counts())
print("\noverdue & not booked, by risk tier:")
od = fu[fu["pathway_status"].str.startswith("OVERDUE")]
print(od["risk_tier"].value_counts())
print(f"\nTotal overdue (not booked): {len(od)} ({len(od)/len(fu):.0%})")
print(f"High-risk (R1) overdue: {(od['risk_tier']=='R1 - High').sum()}")
print(f"Median days overdue (overdue group): {od['days_overdue'].median():.0f}")
print(f"Max days overdue: {fu['days_overdue'].max()}")
print("\nby subspecialty (overdue count):")
print(od["subspecialty"].value_counts())
print("\n=== eye_clinic_appointments.csv ===")
print("rows:", len(appts))
print("overall DNA rate: {:.1%}".format((appts['status']=='DNA').mean()))
print("follow-up : new ratio: {:.2f}".format(
    (appts['appt_type']=='Follow-up').sum() / (appts['appt_type']=='New').sum()))
