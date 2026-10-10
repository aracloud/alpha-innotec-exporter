import os

# Alpha Innotec LW251 / Luxtronik German-language telemetry mapping
serverHost = os.getenv("SERVER_HOST", "0.0.0.0")
serverPort = int(os.getenv("SERVER_PORT", "8888"))
heatPumpHost = os.getenv("HEATPUMP_HOST", "")
heatPumpPort = os.getenv("HEATPUMP_PORT", "8214")


# Metric names match the original exporter's naming where applicable.
# The revised main.py supports Ein/Aus, signed numbers and HH:MM values.
def metric(name, variable, help_text, kind="gauge"):
    return {"name": name, "variable": variable, "help": help_text, "type": kind}

metrics = {
    "Temperaturen": [
        metric("Vorlauf", "heat_pump_flow_temperature", "Flow temperature in degrees Celsius."),
        metric("Rücklauf", "heat_pump_return_temperature", "Return temperature in degrees Celsius."),
        metric("Rückl.-Soll", "heat_pump_target_return_temperature", "Target return temperature in degrees Celsius."),
        metric("Rückl.-Extern", "heat_pump_external_return_temperature", "External return temperature in degrees Celsius."),
        metric("Heissgas", "heat_pump_hot_gas_temperature", "Hot gas temperature in degrees Celsius."),
        metric("Außentemperatur", "heat_pump_ambient_temperature", "Outside temperature in degrees Celsius."),
        metric("Mitteltemperatur", "heat_pump_average_temperature", "Average temperature in degrees Celsius."),
        metric("Warmwasser-Ist", "heat_pump_actual_service_water_temperature", "Actual domestic hot water temperature in degrees Celsius."),
        metric("Warmwasser-Soll", "heat_pump_target_service_water_temperature", "Target domestic hot water temperature in degrees Celsius."),
        metric("Wärmequelle-Ein", "heat_pump_input_heat_source_temperature", "Heat source inlet temperature in degrees Celsius."),
        metric("Wärmequelle-Aus", "heat_pump_output_heat_source_temperature", "Heat source outlet temperature in degrees Celsius."),
        metric("Mischkreis1-Vorlauf", "heat_pump_mixing_circuit_1_flow_temperature", "Mixing circuit 1 flow temperature in degrees Celsius."),
        metric("Mischkreis1 VL-Soll", "heat_pump_mixing_circuit_1_target_flow_temperature", "Mixing circuit 1 target flow temperature in degrees Celsius."),
        metric("Solarkollektor", "heat_pump_solar_collector_temperature", "Solar collector temperature in degrees Celsius."),
        metric("Solarspeicher", "heat_pump_solar_storage_temperature", "Solar storage temperature in degrees Celsius."),
        metric("Externe Energ.Quelle", "heat_pump_external_energy_source_temperature", "External energy source temperature in degrees Celsius."),
        metric("Vorlauf max.", "heat_pump_max_flow_temperature", "Maximum flow temperature in degrees Celsius."),
    ],
    "Ausgänge": [
        metric("AV-Abtauventil", "heat_pump_defrost_valve_status", "Defrost valve state (0=off, 1=on)."),
        metric("BUP", "heat_pump_domestic_hot_water_pump_status", "DHW circulation pump state (0=off, 1=on)."),
        metric("FUP 1", "heat_pump_floor_heat_pump_1_status", "Floor heating pump 1 state (0=off, 1=on)."),
        metric("HUP", "heat_pump_heat_system_pump_status", "Heating circulation pump state (0=off, 1=on)."),
        metric("Mischer 1 Auf", "heat_pump_mixer_1_open_status", "Mixer 1 opening state (0=off, 1=on)."),
        metric("Mischer 1 Zu", "heat_pump_mixer_1_close_status", "Mixer 1 closing state (0=off, 1=on)."),
        metric("Ventilation", "heat_pump_ventilation_status", "Ventilation state (0=off, 1=on)."),
        metric("Ventil.-BOSUP", "heat_pump_ventilation_bosup_status", "Ventilation BOSUP state (0=off, 1=on)."),
        metric("Verdichter", "heat_pump_compressor_status", "Compressor 1 state (0=off, 1=on)."),
        metric("Verdichter 2", "heat_pump_compressor_2_status", "Compressor 2 state (0=off, 1=on)."),
        metric("ZIP", "heat_pump_zip_status", "ZIP output state (0=off, 1=on)."),
        metric("ZUP", "heat_pump_supply_pump_status", "Supply pump state (0=off, 1=on)."),
        metric("ZWE 1", "heat_pump_2nd_heat_generator_1_status", "Auxiliary heat generator 1 state (0=off, 1=on)."),
        metric("ZWE 2 - SST", "heat_pump_2nd_heat_generator_2_status", "Auxiliary heat generator 2 state (0=off, 1=on)."),
        metric("ZWE 3", "heat_pump_2nd_heat_generator_3_status", "Auxiliary heat generator 3 state (0=off, 1=on)."),
        metric("SLP", "heat_pump_slp_status", "SLP output state (0=off, 1=on)."),
        metric("FUP 2", "heat_pump_floor_heat_pump_2_status", "Floor heating pump 2 state (0=off, 1=on)."),
        metric("FUP 3", "heat_pump_floor_heat_pump_3_status", "Floor heating pump 3 state (0=off, 1=on)."),
        metric("AO1", "heat_pump_analog_output_1_volts", "Analog output 1 in volts."),
        metric("AO2", "heat_pump_analog_output_2_volts", "Analog output 2 in volts."),
    ],
    "Betriebsstunden": [
        metric("Betriebstund. VD1", "heat_pump_compressor_1_operating_hours", "Compressor 1 cumulative operating hours."),
        metric("Impulse Verdichter 1", "heat_pump_compressor_1_starts_total", "Compressor 1 cumulative start count.", "counter"),
        metric("Laufzeit Ø VD1", "heat_pump_compressor_1_average_runtime_minutes", "Compressor 1 average runtime in minutes."),
        metric("Betriebstund. VD2", "heat_pump_compressor_2_operating_hours", "Compressor 2 cumulative operating hours."),
        metric("Impulse Verdichter 2", "heat_pump_compressor_2_starts_total", "Compressor 2 cumulative start count.", "counter"),
        metric("Laufzeit Ø VD2", "heat_pump_compressor_2_average_runtime_minutes", "Compressor 2 average runtime in minutes."),
        metric("Betriebstunden ZWE1", "heat_pump_auxiliary_heater_1_operating_hours", "Auxiliary heater 1 cumulative operating hours."),
        metric("Betriebstunden WP", "heat_pump_total_operating_hours", "Heat pump cumulative operating hours."),
        metric("Betriebstunden Heiz.", "heat_pump_heating_operating_hours", "Heating cumulative operating hours."),
        metric("Betriebstunden WW", "heat_pump_hot_water_operating_hours", "Domestic hot water cumulative operating hours."),
    ],
}
