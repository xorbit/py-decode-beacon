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
    #print ' '.join('%02x' % ord(c) for c in ad_struct[:27])
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
    #print ' '.join('%02x' % ord(c) for c in ad_struct[:28])
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

# List of ad_struct decoders for different types of beacon
decode_ad_struct_list = [decode_ibeacon, decode_altbeacon]

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
    if aih.event == 0x03 and aih.bdaddr_type == 0x00 and \
        aih.length + 10 <= len(ad_packet):
      # This is valid, update the adinfo length
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
          #print beacon_data
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
