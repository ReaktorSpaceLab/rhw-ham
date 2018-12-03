import logging
import sys
from ntcle100_temp_sensor import resistance_to_celsius
ADC_REFERENCE_5V = 4885
SOLAR_PANEL_CURRENT_CALIB_MULTIPLIER = 0.95
ADC_REFERENCE_3V3 = 3145
TEMP_CALIB_R1_OHM = 99800
BAT_CURRENT_SENSING_REFERENCE = ADC_REFERENCE_5V / 2
BAT_CURRENT_CALIB_MULTIPLIER = 0.95
BAT_CURRENT_OFFSET_MILLIAMPER = -95
SOLAR_PANEL_OP_AMP_GAIN = 3.13
SOLAR_PANEL_VOLTAGE_OFFSET_MV = -20
RESISTOR_DIVIDER_BAT_COMPENSATION = 2
RESISTOR_DIVIDER_3V3_COMPENSATION = 2
RESISTOR_DIVIDER_5V_COMPENSATION = 2
RESISTOR_DIVIDER_12V_COMPENSATION = 5.7
COM_3V3_CURRENT_CALIB_MULTIPLIER = 0.93
PAYLOAD_CALIB_MULTIPLIER = 1.070
PAYLOAD_CALIB_OFFSET = -146.50
GPS_CALIB_MULTIPLIER = 0.550
GPS_CALIB_OFFSET = -90.278
OBC_CALIB_MULTIPLIER = 0.576
OBC_CALIB_OFFSET = -136.87
ADCS_CALIB_MULTIPLIER = 0.435
ADCS_CALIB_OFFSET = -234.14
ADC_MAX_VALUE = 4095


def adc_5v_to_milli_volt(adc):
    return (adc * ADC_REFERENCE_5V) / ADC_MAX_VALUE


def adc_3v3_to_milli_volt(adc):
    return (adc * ADC_REFERENCE_3V3) / ADC_MAX_VALUE


def adc_to_bat_current_milli_amper(adc):
    return BAT_CURRENT_CALIB_MULTIPLIER * ((adc_5v_to_milli_volt(adc) - BAT_CURRENT_SENSING_REFERENCE) + BAT_CURRENT_OFFSET_MILLIAMPER)


def adc_to_solar_panel_voltage_milli_volt(adc):
    return SOLAR_PANEL_OP_AMP_GAIN * adc_5v_to_milli_volt(adc) + SOLAR_PANEL_VOLTAGE_OFFSET_MV


def adc_to_solar_panel_current_milli_amper(adc):
    return SOLAR_PANEL_CURRENT_CALIB_MULTIPLIER * adc_5v_to_milli_volt(adc)


def adc_3v3_bus_voltage_milli_volt(adc):
    return adc_3v3_to_milli_volt(adc) * RESISTOR_DIVIDER_3V3_COMPENSATION


def adc_5v_bus_voltage_milli_volt(adc):
    return adc_3v3_to_milli_volt(adc) * RESISTOR_DIVIDER_5V_COMPENSATION


def adc_12v_bus_voltage_milli_volt(adc):
    return adc_3v3_to_milli_volt(adc) * RESISTOR_DIVIDER_12V_COMPENSATION


def adc_to_bat_voltage(adc):
    return adc_5v_to_milli_volt(adc) * RESISTOR_DIVIDER_BAT_COMPENSATION


def adc_to_com_3v3_current_milli_amper(adc):
    return adc_3v3_to_milli_volt(adc) * COM_3V3_CURRENT_CALIB_MULTIPLIER


def adc_to_com_5v_current_milli_amper(adc):
    return adc_3v3_to_milli_volt(adc)


def adc_to_payload_current_milli_amper(adc):
    return PAYLOAD_CALIB_MULTIPLIER * adc + PAYLOAD_CALIB_OFFSET


def adc_to_obc_current_milli_amper(adc):
    return OBC_CALIB_MULTIPLIER * adc + OBC_CALIB_OFFSET


def adc_to_gps_current_milli_amper(adc):
    return GPS_CALIB_MULTIPLIER * adc + GPS_CALIB_OFFSET


def adc_to_adcs_current_milli_amper(adc):
    return GPS_CALIB_MULTIPLIER * adc + ADCS_CALIB_OFFSET


def temp_sensor_adc_val_to_celsius(adc_val):
    if adc_val == ADC_MAX_VALUE:
        logging.error("ADC value for temp sensor out of meaningful range")
        return sys.maxsize
    adc_ratio = adc_val / ADC_MAX_VALUE
    r2 = adc_ratio * TEMP_CALIB_R1_OHM / (1 - adc_ratio)
    if r2 == 0:
        logging.error("Invalid temp sensor value %d", adc_val)
        return -9999
    return resistance_to_celsius(r2)


def update_solar_panel_current_adc_to_milli_amper(dic, field):
    dic['adc_statistics'][field] = int(adc_to_solar_panel_current_milli_amper(
        dic['adc_statistics'][field]))


def unit_conversions_to_ground(dic):

    update_solar_panel_current_adc_to_milli_amper(dic, 'spxp_curr')
    update_solar_panel_current_adc_to_milli_amper(dic, 'spxn_curr')
    update_solar_panel_current_adc_to_milli_amper(dic, 'spyp_curr')
    update_solar_panel_current_adc_to_milli_amper(dic, 'spyn_curr')

    dic['adc_statistics']['sp_x_v'] = int(adc_to_solar_panel_voltage_milli_volt(
        dic['adc_statistics']['sp_x_v']))
    dic['adc_statistics']['sp_y_v'] = int(adc_to_solar_panel_voltage_milli_volt(
        dic['adc_statistics']['sp_y_v']))

    dic['adc_statistics']['bat_curr'] = int(adc_to_bat_current_milli_amper(
        dic['adc_statistics']['bat_curr']))

    dic['adc_statistics']['bat_v'] = int(adc_to_bat_voltage(
        dic['adc_statistics']['bat_v']))

    dic['adc_statistics']['uhf_curr_3v3'] = int(adc_to_com_3v3_current_milli_amper(
        dic['adc_statistics']['uhf_curr_3v3']))

    dic['adc_statistics']['uhf_curr_5v'] = int(adc_to_com_5v_current_milli_amper(
        dic['adc_statistics']['uhf_curr_5v']))

    dic['adc_statistics']['payload_curr'] = int(adc_to_payload_current_milli_amper(
        dic['adc_statistics']['payload_curr']))
    dic['adc_statistics']['adcs_curr'] = int(adc_to_adcs_current_milli_amper(
        dic['adc_statistics']['adcs_curr']))
    dic['adc_statistics']['gps_curr'] = int(adc_to_gps_current_milli_amper(
        dic['adc_statistics']['gps_curr']))
    dic['adc_statistics']['obc_curr'] = int(adc_to_obc_current_milli_amper(
        dic['adc_statistics']['obc_curr']))

    dic['adc_statistics']['sns_3v3'] = int(adc_3v3_bus_voltage_milli_volt(
        dic['adc_statistics']['sns_3v3']))

    dic['adc_statistics']['sns_5v'] = int(adc_5v_bus_voltage_milli_volt(
        dic['adc_statistics']['sns_5v']))

    dic['adc_statistics']['sns_12v_1'] = int(adc_12v_bus_voltage_milli_volt(
        dic['adc_statistics']['sns_12v_1']))
    dic['adc_statistics']['sns_12v_2'] = int(adc_12v_bus_voltage_milli_volt(
        dic['adc_statistics']['sns_12v_2']))

    dic['adc_statistics']['temp_sns1'] = int(temp_sensor_adc_val_to_celsius(
        dic['adc_statistics']['temp_sns1']))

    dic['adc_statistics']['temp_sns2'] = int(temp_sensor_adc_val_to_celsius(
        dic['adc_statistics']['temp_sns2']))
    return dic

