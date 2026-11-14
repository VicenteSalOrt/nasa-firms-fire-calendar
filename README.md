# 🔥 Harmonized Wildfire Activity Calendar (MODIS + VIIRS)

A cross-calibrated satellite thermal anomaly dashboard developed for the **NASA Space Apps Challenge 2026**. This tool harmonizes 26 years of NASA FIRMS active fire detections (2000–2026) across Chile into a consistent, colorblind-accessible burning activity calendar.

## 🛰️ Scientific Approach & Instrument Calibration
* **The Challenge:** MODIS (1 km nadir resolution, stretching up to ~9.6 km² at swath edges) and VIIRS (375 m resolution) cannot be directly compared due to spatial resolution, swath distortion, and orbital schedule differences.
* **Sensor Continuity (`1_harmonize.py`):** Filtered high-confidence detections (`>=70%` MODIS; `nominal`/`high` VIIRS) across 875,848 raw NASA FIRMS records. Prevented orbital double-counting by chaining VIIRS S-NPP (2012–Nov 2, 2026) with VIIRS NOAA-20 (post-Nov 2, 2026) on a standard $0.25^\circ \times 0.25^\circ$ grid.
* **Cross-Calibration:** Trained a Gradient Boosting regression model incorporating MODIS optical pixel area (`scan × track`), Fire Radiative Power (FRP), and day/night detection ratios over 8,497 overlapping space-time bins, achieving an **out-of-sample $R^2 = 0.887$** (80/20 split, bias-corrected via Duan's smearing factor).

## 💻 Web Application Features (`2_app.py`)
* **Interactive AOI Selection:** Regional presets for critical Chilean fire zones (Biobío & Ñuble, Valparaíso, La Araucanía) plus custom bounding-box coordinates.
* **Historical Anomaly Detector:** Compares annual hotspot counts and Fire Radiative Power (FRP) against the 26-year historical median.
* **Accessible Burning Calendar:** Monthly heatmap (2000–2026) built with the colorblind-safe `Cividis` palette.
* **Data Export:** One-click CSV download of the 37,095 harmonized cells for emergency managers and researchers.

## 📊 NASA Data Sources
* NASA FIRMS MODIS Collection 6.1 (`M-C61`)
* NASA FIRMS VIIRS S-NPP Collection 2 (`SV-C2`)
* NASA FIRMS VIIRS NOAA-20 Collection 2 (`J1V-C2`)