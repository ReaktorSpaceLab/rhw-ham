from collections import OrderedDict
from ctypes import LittleEndianStructure, Structure, Union, c_uint8, c_uint16, c_uint32,\
    string_at, byref, sizeof, c_bool, c_int16, Array, c_char
import json
import logging
import struct

from telemetry_unit_conversions import \
    temp_sensor_adc_val_to_celsius, adc_to_bat_current_milli_amper, \
    adc_to_solar_panel_current_milli_amper, adc_to_gps_current_milli_amper,\
    adc_to_adcs_current_milli_amper, adc_to_obc_current_milli_amper,\
    adc_to_payload_current_milli_amper, adc_to_solar_panel_voltage_milli_volt, \
    adc_to_bat_voltage, adc_3v3_bus_voltage_milli_volt, adc_5v_bus_voltage_milli_volt,\
    adc_12v_bus_voltage_milli_volt, adc_to_com_3v3_current_milli_amper,\
    adc_to_com_5v_current_milli_amper


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s.%(msecs)03dZ - %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%S")


def format_all_fields(self):
    def format_struct(struct):
        if issubclass(struct.__class__, Structure):
            return "\n" + str(struct)
        else:
            return struct
    # pylint: disable=protected-access
    return "\n".join([field[0] + ": " +
                      str(format_struct(getattr(self, field[0]))) for field in self._fields_])


def _serialize_ctypes_array_element(element):
    if issubclass(element.__class__, Array):
        return [_serialize_ctypes_array_element(x) for x in element]
    elif issubclass(element.__class__, Structure) or issubclass(element.__class__, Union):
        return _ctypes_obj_to_dic(element)
    else:
        return element


def _ctypes_obj_to_dic(obj):
    result = OrderedDict()
    # pylint: disable=protected-access
    for field in obj._fields_:
        field_name = field[0]
        field_val = getattr(obj, field_name)
        value_class = field_val.__class__
        if issubclass(value_class, Array):
            result[field_name] = [_serialize_ctypes_array_element(val) for val in field_val]
        elif issubclass(value_class, Structure) or issubclass(value_class, Union):
            result[field_name] = _ctypes_obj_to_dic(field_val)
        else:
            if isinstance(field_val, (bytes, bytearray)):
                result[field_name] = field_val.decode("utf-8")
            else:
                result[field_name] = field_val
    return result


def ctypes_obj_to_dic(obj):
    return obj.unit_conversions_to_ground(_ctypes_obj_to_dic(obj))


class MessageData(LittleEndianStructure):
    _pack_ = 1

    def __str__(self):
        return format_all_fields(self)

    @classmethod
    def unit_conversions_to_ground(cls, dic):
        return dic


class CanStatistics(MessageData):
    _fields_ = [('rx_frame_count', c_uint32),
                ('tx_frame_count', c_uint32),
                ('error_count', c_uint32),
               ]


class ADCData(MessageData):
    _fields_ = [
        # ADC0
        ('spxp_curr', c_uint16),
        ('spxn_curr', c_uint16),
        ('spyp_curr', c_uint16),
        ('spyn_curr', c_uint16),
        ('sp_x_v', c_uint16),
        ('sp_y_v', c_uint16),
        ('bat_curr', c_uint16),
        ('bat_v', c_uint16),

        # ADC1
        ('uhf_curr_3v3', c_uint16),
        ('uhf_curr_5v', c_uint16),
        ('payload_curr', c_uint16),
        ('adcs_curr', c_uint16),
        ('gps_curr', c_uint16),
        ('obc_curr', c_uint16),
        ('sns_3v3', c_uint16),
        ('sns_5v', c_uint16),

        # ADC2
        ('sns_12v_1', c_uint16),
        ('sns_12v_2', c_uint16),
        ('temp_sns1', c_uint16),
        ('temp_sns2', c_uint16)
    ]

class MpptPanelTelemetry(MessageData):
    _fields_ = [('current_mppt_value', c_uint16)]


class MpptStatistics(MessageData):
    _fields_ = [('panels', MpptPanelTelemetry * 2)]

    def __str__(self):
        strs = [str(x) for x in self.panels]
        return "\n".join(strs)


class EpsStatistics(MessageData):
    _fields_ = [('boot_count', c_uint32),
                ('periodic_boot_count', c_uint16),
                ('boot_reasons', c_uint8 * 12),
                ('last_boot_reason', c_uint8),
                ('total_uptime_s', c_uint32),
                ('uptime_s', c_uint32),
                ('memory_violation_reset_has_occured', c_bool),
                ('internal_temp', c_int16)]


class PowerLevelsBits(MessageData):
    _fields_ = [('payload', c_uint16, 1),
                ('gps', c_uint16, 1),
                ('obc', c_uint16, 1),
                ('adcs', c_uint16, 1),
                ("battery_heater1", c_uint16, 1),
                ("battery_heater2", c_uint16, 1),
                ("charging", c_uint16, 1),
                ("uhf_a", c_uint16, 1),
                ("uhf_b", c_uint16, 1),
                ("toggle_3v3", c_uint16, 1),
                ("toggle_5v", c_uint16, 1),
                ("antenna_deployment1", c_uint16, 1),
                ("antenna_deployment2", c_uint16, 1)
               ]


class PowerLevels(Union):
    _fields_ = [('raw', c_uint16),
                ('structured', PowerLevelsBits)]

    def __str__(self):
        return format_all_fields(self)


class PowerStatistics(MessageData):
    _fields_ = [
        ('target_power_levels', PowerLevels),
        ('actual_power_levels', PowerLevels),
        ('state', c_uint8, 1),
        ('reserved', c_uint8, 7),
    ]


class AntennaStatistics(MessageData):
    _fields_ = [
        ('deployment_sensed', c_uint8, 4),
        ('deployment_rounds', c_uint8, 4),
    ]


class SubsystemHeartbeatStatistics(MessageData):
    _fields_ = [
        ('uhf_failures', c_uint16),
    ]


# See system-state.h for reference
class EpsStatisticsMessage(MessageData):
    _fields_ = [('timestamp', c_uint32),
                ('can_statistics', CanStatistics),
                ('eps_statistics', EpsStatistics),
                ('adc_statistics', ADCData),
                ('mppt_statistics', MpptStatistics),
                ('power_statistics', PowerStatistics),
                ('subsystem_hearbeat_statistics', SubsystemHeartbeatStatistics),
                ('antenna_statistics', AntennaStatistics),
               ]

    @classmethod
    def _update_solar_panel_current_adc_to_milli_amper(cls, dic, field):
        dic['adc_statistics'][field] = int(adc_to_solar_panel_current_milli_amper(
            dic['adc_statistics'][field]))

    @classmethod
    def unit_conversions_to_ground(cls, dic):
        cls._update_solar_panel_current_adc_to_milli_amper(dic, 'spxp_curr')
        cls._update_solar_panel_current_adc_to_milli_amper(dic, 'spxn_curr')
        cls._update_solar_panel_current_adc_to_milli_amper(dic, 'spyp_curr')
        cls._update_solar_panel_current_adc_to_milli_amper(dic, 'spyn_curr')

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


class UhfStatistics(MessageData):
    _fields_ = [('boot_count', c_uint32),
                ('last_boot_reason', c_uint16),
                ('memory_violation_reset_has_occured', c_bool),
                ('internal_temp', c_int16),
                ('current_csp_packet_number', c_uint32),
                ('allowed_relay_packet_count', c_uint16),
                ('rx_csp_frame_count', c_uint32),
                ('rx_relay_frame_count', c_uint32),
                ('tx_csp_frame_count', c_uint32),
                ('rx_fifo_error_count', c_uint32),
                ('tx_fifo_error_count', c_uint32),
               ]


class UhfStatisticsMessage(MessageData):
    _fields_ = [('can_statistics', CanStatistics),
                ('uhf_statistics', UhfStatistics)]

class RadioPacketType:
    CSP = 1
    RELAY = 2

    TYPES = {CSP, RELAY}


LENGTH_TYPE = ">B"
LENGTH_HEADER_SIZE = 1


class HWRadioPacket:
    def __init__(self, packet_type, payload, with_signature=False,
                 target_id=None, serial=None, cmac=None):
        if packet_type not in RadioPacketType.TYPES:
            raise ValueError("Packet type must be valid")
        self.payload = payload
        self.packet_type = packet_type

        if with_signature and packet_type == RadioPacketType.CSP:
            if not serial and not cmac:
                self.serial = bytearray(struct.pack("<I", 0)) # Here we would in reality get the next available packet number
                self.payload += self.serial

                # Calculate after serial added
                self.cmac = bytearray([ 0x0, 0x0, 0x0, 0x0 ]) # Here we would in reality sign for real
                self.payload += self.cmac
            elif cmac and serial:
                self.serial = serial
                self.cmac = cmac
                self.payload += serial + cmac
            else:
                raise AssertionError("Either give both CMAC and serial or "
                                     "neither")

        self.sat_packet = bytearray([packet_type]) + self.payload
        self.length_header = bytearray(struct.pack(LENGTH_TYPE, len(self.sat_packet)))
        self.bytes = self.length_header + self.sat_packet

    def __str__(self):
        return " ".join(map(lambda b: "%02X" % b, self.bytes))

    def get_bytes(self):
        return self.bytes

    def get_bytes_without_len(self):
        return self.sat_packet

    def len_without_len_field(self):
        return len(self.bytes) - len(self.length_header)

    @classmethod
    def from_bytes(cls, data, with_signature=False):
        if len(data) == 0:
            raise ValueError("Packet can't be empty")
        if len(data) < 2:
            raise ValueError("Packet should contain atleast length and type")
        if data[1] not in RadioPacketType.TYPES:
            raise ValueError("Second byte should define the packet type")
        packet_len = struct.unpack(LENGTH_TYPE, data[0:LENGTH_HEADER_SIZE])[0]
        if packet_len != (len(data) - LENGTH_HEADER_SIZE):
            logging.debug("Too many bytes for HW_RADIO_PACKET ignoring leftovers")
            logging.debug(data)

        cmac = None
        serial = None
        if with_signature:
            cmac = data[-COUNTER_SIZE_BYTES:]
            serial = data[-CMAC_SIZE_BYTES-COUNTER_SIZE_BYTES:-CMAC_SIZE_BYTES]
            # Skip trailing cmac and counter so we can compare recalculated
            # value
            payload = data[LENGTH_HEADER_SIZE + 1:-CMAC_SIZE_BYTES-COUNTER_SIZE_BYTES]
        else:
            payload = data[LENGTH_HEADER_SIZE + 1:LENGTH_HEADER_SIZE + packet_len]
        packet = HWRadioPacket(data[LENGTH_HEADER_SIZE], payload,
                               with_signature, serial=serial, cmac=cmac)

        if with_signature:
            packet.cmac = cmac
            packet.serial = serial

        return packet

    @classmethod
    def packets_from_bytes(cls, data, with_signature=False):
        packets = []
        idx = 0
        while idx < len(data):
            packet = HWRadioPacket.from_bytes(data[idx:], with_signature)
            packets.append(packet)
            idx += len(packet.get_bytes())
        return packets


HEADER_SIZE = 4
HEADER_PLUS_LENGTH_SIZE = HEADER_SIZE + 2


class CspIdBits(LittleEndianStructure):
    _fields_ = [('crc', c_uint32, 1),
                ('rdp', c_uint32, 1),
                ('xtea', c_uint32, 1),
                ('hmac', c_uint32, 1),
                ("reserved", c_uint32, 4),
                ("src_port", c_uint32, 6),
                ("dst_port", c_uint32, 6),
                ("dst", c_uint32, 5),
                ("src", c_uint32, 5),
                ("priority", c_uint32, 2), ]


class CspHeader(Union):
    _fields_ = [("structured", CspIdBits),
                ("raw", c_uint32)]

    def get_bytes(self):
        return struct.pack(">I", self.raw)


class CspPacket:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    def __init__(self, src, dst, dst_port, src_port, payload,
                 priority=0, hmac=False, xtea=False, rdp=False,
                 crc=False):

        self.len = struct.pack(">H", len(payload))
        header_bits = CspIdBits(src=src, dst=dst, dst_port=dst_port, src_port=src_port,
                                priority=priority, hmac=hmac, xtea=xtea, rdp=rdp, crc=crc)
        self.header = CspHeader(structured=header_bits)
        self.src = src
        self.dst = dst
        self.dst_port = dst_port
        self.src_port = src_port
        self.payload = payload
        self.priority = priority
        self.hmac = hmac
        self.xtea = xtea
        self.rdp = rdp
        self.crc = crc

    def __str__(self):
        payload_str = " ".join(map(lambda b: "%02X" %b, self.payload)) if len(self.payload) < 10 else ""
        rdp_str = " RDP(" + str(Rdp.from_bytes(self.payload)) + ")" \
            if self.rdp else ""
        return "CSP(src %d:%d dst %d:%d prio %s hmac %s xtea %s rdp %s " \
               "crc %s data[%d] [%s]%s)" % (
                   self.src, self.src_port, self.dst, self.dst_port, self.priority,
                   _print_bool(self.hmac),
                   _print_bool(self.xtea),
                   _print_bool(self.rdp),
                   _print_bool(self.crc),
                   len(self.payload), payload_str, rdp_str)

    @classmethod
    def from_header(cls, header, payload):
        return CspPacket(header.structured.src, header.structured.dst, header.structured.dst_port,
                         header.structured.src_port, payload, priority=header.structured.priority,
                         hmac=header.structured.hmac, xtea=header.structured.xtea,
                         rdp=header.structured.rdp, crc=header.structured.crc
                         )

    @classmethod
    def from_bytes(cls, data, with_length=True):
        if not data:
            raise ValueError("argument should be iterable")
        if len(data) < HEADER_PLUS_LENGTH_SIZE:
            raise ValueError("Csp packet has to have at least 32bit header and 16bit length field")
        header = CspHeader(raw=struct.unpack(">I", data[0:4])[0])
        if with_length:
            length = struct.unpack(">H", data[4:HEADER_PLUS_LENGTH_SIZE])[0]
            if len(data) < length + HEADER_PLUS_LENGTH_SIZE:
                raise ValueError("No support for buffering,"
                                 " argument should enough bytes to satifsfy length field length")
            return cls.from_header(header,
                                   data[HEADER_PLUS_LENGTH_SIZE:HEADER_PLUS_LENGTH_SIZE+length])
        else:
            return cls.from_header(header, data[HEADER_SIZE:])

    @classmethod
    def packets_from_bytes(cls, data):
        packets = []
        idx = 0
        while idx < len(data):
            try:
                packet = cls.from_bytes(data[idx:])
                packets.append(packet)
                idx += len(packet.get_bytes())
            except ValueError:
                logging.debug("Tried to parse malformed or"
                              " incomplete csp packet from bytes: %s", data[idx:])
                break
        return packets

    def get_bytes(self, with_length=True):
        if with_length:
            return self.header.get_bytes() + self.len + self.payload
        else:
            return self.header.get_bytes() + self.payload


def uhf_to_json(str):
    data = bytes.fromhex(str)
    packet = HWRadioPacket.from_bytes(data, with_signature=False)
    csp_packet = CspPacket.from_bytes(packet.payload)
    msg = UhfStatisticsMessage.from_buffer_copy(csp_packet.payload)
    print(json.dumps(ctypes_obj_to_dic(msg), indent=1, sort_keys=False))

def eps_to_json(str):
    data = bytes.fromhex(str)
    packet = HWRadioPacket.from_bytes(data, with_signature=False)
    csp_packet = CspPacket.from_bytes(packet.payload)
    msg = EpsStatisticsMessage.from_buffer_copy(csp_packet.payload)
    print(json.dumps(ctypes_obj_to_dic(msg), indent=1, sort_keys=False))
