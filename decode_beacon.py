# decode_beacon.py
# Beacon advertisement data decoder
# Copyright (c) 2015 Patrick Van Oosterwijck
# MIT Licensed
#
# For now it only decodes iBeacon and AltBeacon data, it is easily extended
# to support other formats.
# Based on https://github.com/adamf/BLE/blob/master/ble-scanner.py and BlueZ
# source code.

import struct
from collections import namedtuple
import uuid


def decode_ibeacon(ad_struct):
  """Ad structure decoder for iBeacon
  Returns a dictionary with the following fields if the ad structure is a
  valid mfg spec iBeacon structure:
    adstruct_bytes: <int> Number of bytes this ad structure consumed
    type: <string> 'ibeacon' for Apple iBeacon
    uuid: <string> UUID
    major: <int> iBeacon Major
    minor: <int> iBeacon Minor
    rssi_ref: <int> Reference signal @ 1m in dBm
  If this isn't a valid iBeacon structure, it returns a dict with these
  fields:
    adstruct_bytes: <int> Number of bytes this ad structure consumed
    type: None for unknown
  """
  # Get the length of the ad structure (including the length byte)
  adstruct_bytes = ord(ad_struct[0]) + 1
  # Create the return object
  ret = { 'adstruct_bytes': adstruct_bytes, 'type': None }
  # Is the length correct and is our data long enough?
  if adstruct_bytes == 0x1B and adstruct_bytes <= len(ad_struct):
    # Decode the ad structure assuming iBeacon format
    iBeaconData = namedtuple('iBeaconData', 'adstruct_bytes adstruct_type '
                  + 'mfg_id_low mfg_id_high ibeacon_id ibeacon_data_len '
                  + 'uuid major minor rssi_ref')
    bd = iBeaconData._make(struct.unpack('>BBBBBB16sHHb', ad_struct[:27]))
    # Check whether all iBeacon specific values are correct
    if bd.adstruct_bytes == 0x1A and bd.adstruct_type == 0xFF and \
        bd.mfg_id_low == 0x4C and bd.mfg_id_high == 0x00 and \
        bd.ibeacon_id == 0x02 and bd.ibeacon_data_len == 0x15:
      # This is a valid iBeacon ad structure
      # Fill in the return structure with the data we extracted
      ret['type'] = 'ibeacon'
      ret['uuid'] = str(uuid.UUID(bytes=bd.uuid))
      ret['major'] = bd.major
      ret['minor'] = bd.minor
      ret['rssi_ref'] = bd.rssi_ref
  # Return the object
  return ret

def decode_altbeacon(ad_struct):
  """Ad structure decoder for AltBeacon
  Returns a dictionary with the following fields if the ad structure is a
  valid mfg spec AltBeacon structure:
    adstruct_bytes: <int> Number of bytes this ad structure consumed
    type: <string> 'altbeacon' for AltBeacon
    mfg_id: <int> indicating Bluetooth SIG assigned manufacturer code
    beacon_id: <string> hex string representing 20 byte beacon id
    mfg_res: <int> manufacturer reserved value
    rssi_ref: <int> Reference signal @ 1m in dBm
  If this isn't a valid AltBeacon structure, it returns a dict with these
  fields:
    adstruct_bytes: <int> Number of bytes this ad structure consumed
    type: None for unknown  
  """
  # Get the length of the ad structure (including the length byte)
  adstruct_bytes = ord(ad_struct[0]) + 1
  # Create the return object
  ret = { 'adstruct_bytes': adstruct_bytes, 'type': None }
  # Is the length correct and is our data long enough?
  if adstruct_bytes == 0x1C and adstruct_bytes <= len(ad_struct):
    # Decode the ad structure assuming AltBeacon format
    AltBeaconData = namedtuple('AltBeaconData', 'adstruct_bytes '
                  + 'adstruct_type mfg_id beacon_code beacon_id '
                  + 'rssi_ref mfg_res')
    bd = AltBeaconData._make(struct.unpack('<BBHH20sbB', ad_struct[:28]))
    # Check whether all AltBeacon specific values are correct
    if bd.adstruct_bytes == 0x1B and bd.adstruct_type == 0xFF and \
        bd.beacon_code == 0xACBE:
      # This is a valid AltBeacon ad structure
      # Fill in the return structure with the data we extracted
      ret['type'] = 'altbeacon'
      ret['mfg_id'] = bd.mfg_id
      ret['beacon_id'] = ''.join('%02x' % ord(c) for c in bd.beacon_id)
      ret['mfg_res'] = bd.mfg_res
      ret['rssi_ref'] = bd.rssi_ref
  # Return the object
  return ret

def decode_eddystone(ad_struct):
  """Ad structure decoder for Eddystone
  Returns a dictionary with the following fields if the ad structure is a
  valid mfg spec Eddystone structure:
    adstruct_bytes: <int> Number of bytes this ad structure consumed
    type: <string> 'eddystone' for Eddystone
  If it is an Eddystone UID ad structure, the dictionary also contains:
    sub_type: <string> 'uid'
    namespace: <string> hex string representing 10 byte namespace
    instance: <string> hex string representing 6 byte instance
    rssi_ref: <int> Reference signal @ 1m in dBm
  If it is an Eddystone URL ad structure, the dictionary also contains:
    sub_type: <string> 'url'
    url: <string> URL
    rssi_ref: <int> Reference signal @ 1m in dBm
  If it is an Eddystone TLM ad structure, the dictionary also contains:
    sub_type: <string> 'tlm'
    tlm_version: <int> Only version 0 is decoded to produce the next fields
    vbatt: <float> battery voltage in V
    temp: <float> temperature in degrees Celsius
    adv_cnt: <int> running count of advertisement frames
    sec_cnt: <float> time in seconds since boot
  If this isn't a valid Eddystone structure, it returns a dict with these
  fields:
    adstruct_bytes: <int> Number of bytes this ad structure consumed
    type: None for unknown  
  """
  # Get the length of the ad structure (including the length byte)
  adstruct_bytes = ord(ad_struct[0]) + 1
  # Create the return object
  ret = { 'adstruct_bytes': adstruct_bytes, 'type': None }
  # Is our data long enough to decode as Eddystone?
  if adstruct_bytes >= 5 and adstruct_bytes <= len(ad_struct):
    # Decode the common part of the Eddystone data
    EddystoneCommon = namedtuple('EddystoneCommon', 'adstruct_bytes '
                    + 'service_data eddystone_uuid sub_type')
    ec = EddystoneCommon._make(struct.unpack('<BBHB', ad_struct[:5]))
    # Is this a valid Eddystone ad structure?
    if ec.eddystone_uuid == 0xFEAA and ec.service_data == 0x16:
      # Fill in the return data we know at this point
      ret['type'] = 'eddystone'
      # Now select based on the sub type
      # Is this a UID sub type? (Accomodate beacons that either include or
      # exclude the reserved bytes)
      if ec.sub_type == 0x00 and (ec.adstruct_bytes == 0x15 or
                                  ec.adstruct_bytes == 0x17):
        # Decode Eddystone UID data (without reserved bytes)
        EddystoneUID = namedtuple('EddystoneUID', 'rssi_ref '
                      + 'namespace instance')
        ei = EddystoneUID._make(struct.unpack('>b10s6s', ad_struct[5:22]))
        # Fill in the return structure with the data we extracted
        ret['sub_type'] = 'uid'
        ret['namespace'] = ''.join('%02x' % ord(c) for c in ei.namespace)
        ret['instance'] = ''.join('%02x' % ord(c) for c in ei.instance)
        ret['rssi_ref'] = ei.rssi_ref - 41
      # Is this a URL sub type?
      if ec.sub_type == 0x10:
        # Decode Eddystone URL header
        EddyStoneURL = namedtuple('EddystoneURL', 'rssi_ref url_scheme')
        eu = EddyStoneURL._make(struct.unpack('>bB', ad_struct[5:7]))
        # Fill in the return structure with extracted data and init the URL
        ret['sub_type'] = 'url'
        ret['rssi_ref'] = eu.rssi_ref - 41
        ret['url'] = ['http://www.', 'https://www.', 'http://', 'https://'] \
                      [eu.url_scheme & 0x03]
        # Go through the remaining bytes to build the URL
        for c in ad_struct[7:adstruct_bytes]:
          # Get the character code
          c_code = ord(c)
          # Is this an expansion code?
          if c_code < 14:
            # Add the expansion code
            ret['url'] += ['.com', '.org', '.edu', '.net', '.info', '.biz',
                          '.gov'][c_code if c_code < 7 else c_code - 7]
            # Add the slash if that variant is selected
            if c_code < 7: ret['url'] += '/'
          # Is this a graphic printable ASCII character?
          if c_code > 0x20 and c_code < 0x7F:
            # Add it to the URL
            ret['url'] += c
      # Is this a TLM sub type?
      if ec.sub_type == 0x20 and ec.adstruct_bytes == 0x11:
        # Decode Eddystone telemetry data
        EddystoneTLM = namedtuple('EddystoneTLM', 'tlm_version '
                      + 'vbatt temp adv_cnt sec_cnt')
        et = EddystoneTLM._make(struct.unpack('>BHhLL', ad_struct[5:18]))
        # Fill in generic TLM data
        ret['sub_type'] = 'tlm'
        ret['tlm_version'] = et.tlm_version
        # Fill the return structure with data if version 0
        if et.tlm_version == 0x00:
          ret['vbatt'] = et.vbatt / 1000.0
          ret['temp'] = et.temp / 256.0
          ret['adv_cnt'] = et.adv_cnt
          ret['sec_cnt'] = et.sec_cnt / 10.0
  # Return the object
  return ret

# List of ad_struct decoders for different types of beacon
decode_ad_struct_list = [decode_ibeacon, decode_altbeacon, decode_eddystone]

def decode_ad_report(ad_packet):
  """Decode a Bluetooth LE advertisement report
  Returns a dictionary with the following fields:
    adinfo_bytes: <int> number of bytes this ad info consumed
    type: <string> or None based on decode success
    Plus other beacon specific data
  """
  # Initialize return object
  ret = { 'type': None, 'adinfo_bytes': len(ad_packet) }
  # Check that we have the minimum ad info header length
  if len(ad_packet) >= 9:
    # Decode advertising report header
    AdInfoHeader = namedtuple('AdInfoHeader', 'event bdaddr_type '
                              + 'bdaddr length')
    aih = AdInfoHeader._make(struct.unpack('<BB6sB', ad_packet[:9]))
    # Check if this is valid advertisement info
    if aih.bdaddr_type <= 0x01 and aih.length + 10 <= len(ad_packet):
      # This is (likely) valid (many more checks later), update the
      # adinfo length
      ret['adinfo_bytes'] = aih.length + 10
      # Add Bluetooth device address to return object
      ret['bdaddr'] = ':'.join(reversed(['%02X' % ord(b)
                                          for b in aih.bdaddr]))
      # Move to first ad struct
      ad_struct = ad_packet[9:]
      # Create default beacon_data
      beacon_data = {}
      # Iterate over ad structs
      while len(ad_struct) > 1:
        # Try different beacon decoders
        for decoder in decode_ad_struct_list:
          # Run a decoder
          beacon_data = decoder(ad_struct)
          # Stop if this decoder recognized the data
          if beacon_data['type']:
            break
        # Stop if we decoded the beacon data
        if beacon_data['type']:
          break
        # Go to the next ad struct
        ad_struct = ad_struct[beacon_data['adstruct_bytes']:]
      # Add beacon data to return object
      for key, val in beacon_data.iteritems():
        if key != 'adstruct_bytes':
          ret[key] = val
      # Add observed RSSI to return object
      ret['rssi_obs'], = struct.unpack('<b', ad_packet[aih.length + 9])
  # Return the return object
  return ret

def bluez_decode_beacons(bluez_packet):
  """BlueZ event packet decoder
  Identifies a beacon advertisement packet and extracts its data.
  Returns an array with dictionaries containing beacon data.
  """
  # Initialize beacons list
  beacons = []
  # Check if the packet is the minimum length to be able to unpack the
  # BlueZ packet header
  if len(bluez_packet) >= 5:
    # Decode BlueZ header to see if the packet contains LE advertising info
    BlueZHeader = namedtuple('BlueZHeader', 'hci_packet_type event '
                              + 'length meta_event report_num')
    bzh = BlueZHeader._make(struct.unpack('<BBBBB', bluez_packet[:5]))
    # Check if this is a valid LE advertisement packet
    if bzh.hci_packet_type == 0x04 and bzh.event == 0x3E and \
        bzh.meta_event == 0x02 and bzh.report_num > 0 and \
        bzh.length + 3 == len(bluez_packet):
      # Track reports
      reports = bzh.report_num
      # Move to the first advertising report
      ad_packet = bluez_packet[5:]
      # Iterate over the advertising reports
      while reports > 0 and len(ad_packet) >= 9:
        # Decode the advertising report
        ad_report = decode_ad_report(ad_packet)
        # Decrement reports counter
        reports -= 1
        # Move on to the next advertising report
        ad_packet = ad_packet[ad_report['adinfo_bytes']:]
        # Is this a valid beacon?
        if ad_report['type']:
          # Remove the adinfo_bytes
          del ad_report['adinfo_bytes']
          # Add this beacon to the beacons list
          beacons.append(ad_report)
  # Return the beacons list
  return beacons
