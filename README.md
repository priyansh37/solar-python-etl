# Solar IoT Python ETL Pipeline

## Overview
Python ETL pipeline processing real solar IoT data from MW-scale plants across India.
Extracts raw Parquet files, transforms and cleans sensor data, calculates daily KPIs.

## What it does
- Extracts 19 Parquet files (4.2M rows) from 2 solar plants
- Cleans raw IoT sensor data (inverters, weather stations, meters)
- Calculates daily KPIs: CUF, average power, peak power, irradiance
- Flags underperforming inverters automatically
- Outputs clean Parquet and KPI CSV files

## KPIs Calculated
- CUF (Capacity Utilization Factor)
- Daily energy per inverter
- Average and peak power per plant
- Performance category (Poor/Below Average/Average/Good)

## Tech Stack
- Python 3.11
- Pandas — data transformation
- PyArrow — Parquet file handling
- Google Cloud BigQuery — cloud data warehouse

## Data
Real production solar IoT data from MW-scale plants in India.
Sensor types: Inverters, Weather Stations (WMS), MFM Meters, SMB

## Related Project
dbt Analytics Pipeline: https://github.com/priyansh37/solar-analytics-dbt