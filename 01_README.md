# Closing the Hidden Waiting List
## NHS Ophthalmology Follow-Up Backlog & Sight-Loss Risk Dashboard

![Executive Overview](Executive%20Overview.png)

## The Problem
Ophthalmology is the busiest outpatient specialty in the NHS with over 8.8 million 
appointments per year. It runs 3:1 follow-up to new appointments — far above the 
NHS average — because conditions like glaucoma and AMD require ongoing monitoring 
to prevent permanent sight loss.

Permanent sight loss is **9× more likely** in follow-up patients than new ones. Yet 
the NHS 18-week RTT target prioritises new patients, creating a structural backlog 
in follow-ups that is invisible to standard reporting.

Most trusts clear backlogs by date order. This dashboard clears them by **clinical 
risk**.

## The Dashboard
A 4-page Power BI dashboard built on synthetic NHS ophthalmology data:

| Page | Description |
|---|---|
| Executive Overview | KPI cards, pathway status breakdown, overdue by subspecialty |
| Sight-Loss Risk & Safety Worklist | Risk heatmap + prioritised clinical worklist |
| Subspecialty Deep-Dive | Interactive drill-down by condition and ageing band |
| DNA & Capacity | Did Not Attend analysis and appointment volume trends |

## Key Findings (Synthetic Data)
- **6,000** patients on the follow-up pathway
- **1,788 (29.8%)** overdue with no appointment booked
- **421 high-risk (R1) patients** overdue — potential sight loss risk
- **9.1% DNA rate** representing wasted clinic capacity
- Glaucoma and Medical Retina carry the highest R1 overdue burden

## Tools Used
- **Power BI Desktop** — report building, DAX measures, data modelling
- **Power Query** — data cleaning and transformation
- **DAX** — custom measures including risk filtering and ageing bands
- **Python** — synthetic dataset generation (`generate_eye_data.py`)

## Data
All data is **synthetic**. No real patient data is used anywhere in this project. 
Distributions are modelled on published NHS ophthalmology characteristics:
- ~9% DNA rate
- 3:1 follow-up to new ratio
- Risk-stratified pathways (R1 High / R2 Medium / R3 Low)
- 5 clinic sites, 5 subspecialties, 15 conditions

## Files
| File | Description |
|---|---|
| `Eye_Clinic_Dashboard.pbix` | Power BI dashboard file |
| `eye_clinic_followups.csv` | Patient pathway data (6,000 rows) |
| `eye_clinic_appointments.csv` | Appointment history (~24,000 rows) |
| `generate_eye_data.py` | Python script used to generate synthetic data |

## Domain Context
Built on experience from NHS EPR implementations including Moorfields Eye Hospital 
(MEDITECH Expanse). The clinical logic — risk tiers, follow-up intervals, subspecialty 
pathways — reflects real Hospital Eye Service operational challenges.

## Author
**Mahamed Ali** — Business Systems Analyst & EPR Specialist transitioning into BI/Data Analytics 
