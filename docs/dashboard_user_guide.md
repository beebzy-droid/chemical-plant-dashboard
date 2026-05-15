# Dashboard User Guide
## Chemical Plant Performance Monitoring Dashboard
**Version:** 1.0  
**Last Updated:** May 2026  
**Tool:** Tableau Public

---

## 🎯 Purpose
This dashboard monitors the real-time performance of the Phenol
Synthesis Plant (Unit-01, Unit-02, Unit-03). It helps plant 
managers and operators:
- Track KPIs against targets instantly
- Identify which unit or shift is underperforming
- Spot trends in defects, downtime, and yield
- Make data-driven decisions on the plant floor

---

## 📊 Dashboard Pages

### Page 1 — OEE Trend
**What it shows:** Monthly OEE trend for all 3 units
**How to read it:**
- Each colored line = one plant unit
- Red dashed line = 85% OEE target
- Lines below the red line = underperforming months
- Dips in June/July = seasonal fault spikes

**Questions it answers:**
- Is OEE improving or declining over time?
- Which unit consistently performs best?
- Which months had the worst OEE?

---

### Page 2 — OEE Components
**What it shows:** Availability, Performance, Quality bars per unit
**How to read it:**
- 3 bar groups per unit (Availability, Performance, Quality)
- Taller bar = better performance
- Short Performance bars = speed is the problem

**Questions it answers:**
- Which OEE component is dragging performance down?
- Is the problem availability, speed, or quality?

---

### Page 3 — Downtime Analysis
**What it shows:** Average downtime per unit broken down by shift
**How to read it:**
- Each stacked bar = one unit
- Colors = Morning / Afternoon / Night shift
- Taller bar = more downtime

**Questions it answers:**
- Which unit has the most downtime?
- Which shift contributes most to downtime?

---

### Page 4 — Yield Analysis
**What it shows:** Monthly yield % trend for all 3 units
**How to read it:**
- Each line = one unit
- Red line = 90% yield target
- Lines below red = below target months

**Questions it answers:**
- Is yield improving over time?
- Which months had the lowest yield?

---

### Page 5 — Defect Analysis
**What it shows:** Monthly defect % trend for all 3 units
**How to read it:**
- Each line = one unit
- Red line = 2% defect target
- Lines above red = too many defects

**Questions it answers:**
- Is defect rate improving or worsening?
- Which unit has the highest defect rate?
- Which months had defect spikes?

---

### Page 6 — MTBF & MTTR
**What it shows:** Mean Time Between Failures per unit/shift
**How to read it:**
- Taller bar = longer time between failures = more reliable
- Colors = Morning / Afternoon / Night shift

**Questions it answers:**
- How reliable is each unit?
- Which shift has the best equipment reliability?

---

## 🎯 KPI Targets Quick Reference

| KPI | Target | Current | Status |
|---|---|---|---|
| OEE | ≥ 85% | 71.4% | ⚠️ Below |
| Yield | ≥ 90% | 89.7% | ⚠️ Borderline |
| Defect % | ≤ 2% | 2.47% | ⚠️ Above |
| Availability | ≥ 90% | 97.5% | ✅ Good |
| Performance | ≥ 95% | 75.0% | ⚠️ Below |
| Quality | ≥ 99% | 97.5% | ⚠️ Slight |
| MTBF | Maximize | 330 min | ✅ Good |
| MTTR | Minimize | 3.6 min | ✅ Good |

---

## 🔍 How to Use Filters
- **Unit filter:** Click a unit name in the legend to highlight it
- **Date filter:** Use the date range selector to zoom into a period
- **Shift filter:** Click a shift color in the legend to isolate it

---

## ⚠️ How to Read Alarm Colors
| Color | Meaning |
|---|---|
| 🟢 Green | On target |
| 🟡 Amber | Approaching limit |
| 🔴 Red | Below/above target |

---

## 📞 Support
For data issues contact the Data Engineering team.  
For dashboard access issues contact the IT team.