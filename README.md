# 🔥 Harmonized Wildfire Activity Calendar (MODIS + VIIRS)

A cross-calibrated satellite thermal anomaly dashboard developed for the **NASA Space Apps Challenge 2026**. This tool harmonizes 26 years of NASA FIRMS active fire detections (2000–2026) across Chile into a consistent, colorblind-accessible burning activity calendar.

## 🛰️ Scientific Approach & Calibration
* **The Challenge:** MODIS (1 km resolution, 2000–present) and VIIRS (375 m resolution, 2012–present) cannot be directly compared due to spatial resolution and sensitivity differences.
* **Methodology (`1_harmonize.py`):** Filtered high-confidence detections (`>=70%` MODIS; `nominal`/`high` VIIRS) across 875,848 raw NASA FIRMS records and aggregated them into a common $0.1^\circ \times 0.1^\circ$ space-time grid.
* **Cross-Calibration:** Trained a Random Forest regression model over 12,918 overlapping space-time bins (2012–2026), achieving an **out-of-sample $R^2 = 0.614$** (80/20 split), and retrained on 100% of overlap data to reconstruct pre-2012 MODIS records into the VIIRS 375 m scale.

## 💻 Web Application Features (`2_app.py`)
* **Interactive AOI Selection:** Regional presets for critical Chilean fire zones (Biobío & Ñuble, Valparaíso, La Araucanía) plus custom bounding-box coordinates.
* **Historical Anomaly Detector:** Compares annual hotspot counts and Fire Radiative Power (FRP) against the 26-year historical median.
* **Accessible Burning Calendar:** Monthly heatmap (2000–2026) built with the colorblind-safe `Cividis` palette.
* **Data Export:** One-click CSV download of harmonized time series for emergency managers and researchers.

## 📊 NASA Data Sources
* NASA FIRMS MODIS Collection 6.1 (`M-C61`)
* NASA FIRMS VIIRS S-NPP Collection 2 (`SV-C2`)
* NASA FIRMS VIIRS NOAA-20 Collection 2 (`J1V-C2`)