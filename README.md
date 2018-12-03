# rhw-ham
This repository has additional information to help HAM's listening to Reaktor Hello World satellite.

Project web page: https://reaktorspace.com/reaktor-hello-world/


# Telemetry decoding

An example GNU Radio Companion file is provided that can decode the FSK packets transmitted by Reaktor Hello World. It requires the [CC11XX decoder block](https://github.com/andrepuschmann/gr-cc11xx). The sample file used by default is a real recording from orbit with a single EPS telemetry packet. The format is explained in the [Reaktor Hello World page](https://reaktorspace.com/reaktor-hello-world/#get-in-touch). The decoder print to standard out the bytes starting after the sync word, i.e., the first byte is the radio packet length.

The file telemetry_unit_conversions.py contains the conversions from adc readings to meaningful units.

There's a full conversion script `rhw_telemetry/hex_decoder.py`, usage e.g. with the included telemetry packet from `rhw_telemetry_samples/rhw_fsk_eps_beacon_from_orbit_96k.raw`:

```
$ python3
>>> import hex_decoder
>>> hex_decoder.eps_to_json('71 01 07 00 C3 00 00 62 81 F8 00 5C AC 60 03 00 77 7A 35 00 8F 00 00 00 5E 00 00 00 0A 00 02 06 02 02 02 02 02 02 02 06 02 02 06 DE 72 01 00 C6 00 00 00 00 FE FF 03 00 77 00 BB 00 27 00 E0 05 07 05 FF 07 A5 0D 2E 00 05 00 97 01 01 00 F6 00 00 00 7A 08 B3 0C 03 00 00 00 7E 0A 18 0B B5 07 9D 08 C3 06 C3 06 00 04 00 3F 20 23 04 26 FD 7A AB FF B4 AC')
{
 "timestamp": 1543567489,
 "can_statistics": {
  "rx_frame_count": 221356,
  "tx_frame_count": 3504759,
  "error_count": 143
 },
 "eps_statistics": {
  "boot_count": 94,
  "periodic_boot_count": 10,
  "boot_reasons": [
   2,
   6,
   2,
   2,
   2,
   2,
   2,
   2,
   2,
   6,
   2,
   2
  ],
  "last_boot_reason": 6,
  "total_uptime_s": 94942,
  "uptime_s": 198,
  "memory_violation_reset_has_occured": false,
  "internal_temp": -2
 },
 "adc_statistics": {
  "spxp_curr": 3,
  "spxn_curr": 134,
  "spyp_curr": 211,
  "spyn_curr": 44,
  "sp_x_v": 5595,
  "sp_y_v": 4785,
  "bat_curr": -90,
  "bat_v": 8333,
  "uhf_curr_3v3": 32,
  "uhf_curr_5v": 3,
  "payload_curr": 288,
  "adcs_curr": -233,
  "gps_curr": 45,
  "obc_curr": -136,
  "sns_3v3": 3333,
  "sns_5v": 4993,
  "sns_12v_1": 13,
  "sns_12v_2": 0,
  "temp_sns1": 11,
  "temp_sns2": 8
 },
 "mppt_statistics": {
  "panels": [
   {
    "current_mppt_value": 1973
   },
   {
    "current_mppt_value": 2205
   }
  ]
 },
 "power_statistics": {
  "target_power_levels": {
   "raw": 1731,
   "structured": {
    "payload": 1,
    "gps": 1,
    "obc": 0,
    "adcs": 0,
    "battery_heater1": 0,
    "battery_heater2": 0,
    "charging": 1,
    "uhf_a": 1,
    "uhf_b": 0,
    "toggle_3v3": 1,
    "toggle_5v": 1,
    "antenna_deployment1": 0,
    "antenna_deployment2": 0
   }
  },
  "actual_power_levels": {
   "raw": 1731,
   "structured": {
    "payload": 1,
    "gps": 1,
    "obc": 0,
    "adcs": 0,
    "battery_heater1": 0,
    "battery_heater2": 0,
    "charging": 1,
    "uhf_a": 1,
    "uhf_b": 0,
    "toggle_3v3": 1,
    "toggle_5v": 1,
    "antenna_deployment1": 0,
    "antenna_deployment2": 0
   }
  },
  "state": 0,
  "reserved": 0
 },
 "subsystem_hearbeat_statistics": {
  "uhf_failures": 4
 },
 "antenna_statistics": {
  "deployment_sensed": 15,
  "deployment_rounds": 3
 }
}
```
