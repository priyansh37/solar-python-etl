import pandas as pd
import os
from datetime import datetime

# ============================================
# EXTRACT — Read all Parquet files
# ============================================

PARQUET_FOLDER = r'C:\Data\datawarehouse'
OUTPUT_FOLDER = r'C:\Priyansh_WorkSpace\Reference Project\Learn-Play\python-solar\output'

# Create output folder if not exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("=" * 50)
print("SOLAR ETL PIPELINE")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

# Read all parquet files
all_files = [f for f in os.listdir(PARQUET_FOLDER) if f.endswith('.parquet')]
print(f"\nFound {len(all_files)} parquet files")

dfs = []
for file in all_files:
    path = os.path.join(PARQUET_FOLDER, file)
    parts = file.replace('.parquet', '').rsplit('_', 3)
    plant_id = parts[0]
    file_date = f"{parts[1]}-{parts[2]}-{parts[3]}" if len(parts) == 4 else 'unknown'
    
    df = pd.read_parquet(path)
    df['plant_id'] = plant_id
    df['file_date'] = file_date
    dfs.append(df)
    print(f"  Extracted: {file} — {len(df):,} rows")

# Combine all files
raw_df = pd.concat(dfs, ignore_index=True)
print(f"\nTotal raw rows: {len(raw_df):,}")

# ============================================
# TRANSFORM — Clean and process data
# ============================================

print("\nTransforming data...")

# Convert data types
raw_df['TimeStamp'] = pd.to_datetime(raw_df['TimeStamp'])
raw_df['Value'] = pd.to_numeric(raw_df['Value'], errors='coerce')
raw_df['date'] = raw_df['TimeStamp'].dt.date

# Keep only useful columns
clean_df = raw_df[[
    'plant_id', 'date', 'TimeStamp',
    'DeviceName', 'ParameterName', 'Value', 'Unit', 'Type'
]].copy()

# Rename columns
clean_df.columns = [
    'plant_id', 'date', 'timestamp',
    'device_name', 'parameter_name', 'value', 'unit', 'device_type'
]

# Remove rows with null values
clean_df = clean_df.dropna(subset=['value'])
print(f"Rows after cleaning: {len(clean_df):,}")

# ============================================
# TRANSFORM — Calculate Daily KPIs
# ============================================

print("\nCalculating KPIs...")

# Filter inverter data
inverter_df = clean_df[clean_df['device_type'] == 'Inverter'].copy()

# Daily energy per plant
energy_df = inverter_df[
    inverter_df['parameter_name'].isin(['Today_Energy', 'E-Daily'])
]

daily_energy = energy_df.groupby(
    ['plant_id', 'date']
)['value'].max().reset_index()
daily_energy.columns = ['plant_id', 'date', 'total_energy_kwh']

# Daily average power per plant
power_df = inverter_df[
    inverter_df['parameter_name'].isin(['Active_Power', 'Active power'])
]

power_df = power_df[
    (power_df['value'] >= 0) & 
    (power_df['value'] <= 10000)
]

daily_power = power_df.groupby(
    ['plant_id', 'date']
)['value'].agg(['mean', 'max']).reset_index()

daily_power.columns = ['plant_id', 'date', 'avg_power_kw', 'peak_power_kw']

# Weather data
weather_df = clean_df[clean_df['device_type'] == 'WMS'].copy()

daily_irradiance = weather_df[
    weather_df['parameter_name'] == 'GHI'
].groupby(['plant_id', 'date'])['value'].mean().reset_index()
daily_irradiance.columns = ['plant_id', 'date', 'avg_irradiance']

# Merge all KPIs
kpi_df = daily_energy.merge(daily_power, on=['plant_id', 'date'], how='left')
kpi_df = kpi_df.merge(daily_irradiance, on=['plant_id', 'date'], how='left')

# Calculate CUF (assuming 1MW capacity)
kpi_df['cuf_percent'] = (kpi_df['total_energy_kwh'] / (1000 * 24) * 100).round(2)

# Performance category
kpi_df['performance_category'] = pd.cut(
    kpi_df['cuf_percent'],
    bins=[0, 30, 50, 70, 100],
    labels=['Poor', 'Below Average', 'Average', 'Good']
)

print(f"KPI rows calculated: {len(kpi_df)}")

# ============================================
# LOAD — Save results
# ============================================

print("\nLoading results...")

# Save clean data
clean_output = os.path.join(OUTPUT_FOLDER, 'clean_solar_data.parquet')
clean_df.to_parquet(clean_output, index=False)
print(f"Saved: clean_solar_data.parquet")

# Save KPI summary
kpi_output = os.path.join(OUTPUT_FOLDER, 'daily_kpi_summary.csv')
kpi_df.to_csv(kpi_output, index=False)
print(f"Saved: daily_kpi_summary.csv")

# Print summary
print("\n" + "=" * 50)
print("KPI SUMMARY")
print("=" * 50)
print(kpi_df.to_string(index=False))

print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("ETL Pipeline finished successfully")