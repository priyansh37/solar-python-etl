import pandas as pd

# Read your real solar parquet file
df = pd.read_parquet(r'C:\Data\datawarehouse\EFE98859-67C0-4AA1-98DF-AAD07A4A477A_2025-12-22.parquet')

# Basic exploration
# print("Shape:", df.shape)
# print("\nColumns:", df.columns.tolist())
# print("\nData types:\n", df.dtypes)
# print("\nFirst 5 rows:\n", df.head())
# print("\nBasic stats:\n", df.describe())

# Convert data types
df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

# How many device types?
print("\nDevice Types:")
print(df['Type'].value_counts())

# How many unique parameters?
print("\nUnique Parameters:", df['ParameterName'].nunique())

# Filter only inverter data
inverter_df = df[df['Type'] == 'Inverter']
print("\nInverter rows:", len(inverter_df))

# Get active power only
active_power = inverter_df[inverter_df['ParameterName'] == 'Active_Power']
print("\nActive Power readings:", len(active_power))
print("\nActive Power stats:")
print(active_power['Value'].describe())

# ============================================
# DAILY ENERGY SUMMARY
# ============================================

# Filter inverter data only
inverter_df = df[df['Type'] == 'Inverter'].copy()

# Convert timestamp and value
inverter_df['TimeStamp'] = pd.to_datetime(inverter_df['TimeStamp'])
inverter_df['Value'] = pd.to_numeric(inverter_df['Value'], errors='coerce')

# Filter Today_Energy parameter
energy_df = inverter_df[inverter_df['ParameterName'] == 'Today_Energy']

# Group by device and get max (cumulative counter)
daily_energy = energy_df.groupby('DeviceName')['Value'].max().reset_index()
daily_energy.columns = ['inverter_name', 'energy_kwh']
daily_energy = daily_energy.sort_values('energy_kwh', ascending=False)

print("\nDaily Energy per Inverter (kWh):")
print(daily_energy.to_string(index=False))
print(f"\nTotal Plant Energy: {daily_energy['energy_kwh'].sum():.2f} kWh")

# Active power over time
power_df = inverter_df[inverter_df['ParameterName'] == 'Active_Power'].copy()
power_df = power_df.sort_values('TimeStamp')

# Resample to hourly average
power_df = power_df.set_index('TimeStamp')
hourly_power = power_df['Value'].resample('h').mean().reset_index()
hourly_power.columns = ['hour', 'avg_power_kw']
hourly_power = hourly_power[hourly_power['avg_power_kw'] > 0]

print("\nHourly Average Power (kW):")
print(hourly_power.to_string(index=False))

# ============================================
# INVERTER PERFORMANCE COMPARISON
# ============================================

# Get all inverters and their active power
perf_df = inverter_df[
    inverter_df['ParameterName'] == 'Active_Power'
].copy()

# Group by inverter and time
perf_df = perf_df.set_index('TimeStamp')

# Average power per inverter
avg_per_inverter = perf_df.groupby('DeviceName')['Value'].mean().reset_index()
avg_per_inverter.columns = ['inverter', 'avg_power_kw']
avg_per_inverter = avg_per_inverter.sort_values('avg_power_kw', ascending=False)

print("\nAverage Power per Inverter (kW):")
print(avg_per_inverter.to_string(index=False))

# Find underperforming inverters
fleet_avg = avg_per_inverter['avg_power_kw'].mean()
print(f"\nFleet Average Power: {fleet_avg:.2f} kW")

underperforming = avg_per_inverter[
    avg_per_inverter['avg_power_kw'] < fleet_avg * 0.8
]

if len(underperforming) > 0:
    print("\nUnderperforming Inverters (below 80% of fleet average):")
    print(underperforming.to_string(index=False))
else:
    print("\nAll inverters performing within normal range")

# ============================================
# SAVE RESULTS
# ============================================

# Save daily energy summary
daily_energy.to_csv('daily_energy_summary.csv', index=False)
print("\nSaved: daily_energy_summary.csv")

# Save hourly power
hourly_power.to_csv('hourly_power_profile.csv', index=False)
print("Saved: hourly_power_profile.csv")

# Save inverter performance
avg_per_inverter.to_csv('inverter_performance.csv', index=False)
print("Saved: inverter_performance.csv")