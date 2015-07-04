# bluez_beacon_scan.py
# BlueZ beacon scanner demo
# Copyright (c) 2015 Patrick Van Oosterwijck
# MIT Licensed
#
# Based on https://github.com/adamf/BLE/blob/master/ble-scanner.py

import decode_beacon
import bluetooth._bluetooth as bluez
import struct


OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_ENABLE = 0x000C

try:
  # Open the bluetooth device
  sock = bluez.hci_open_dev(0)
  print "BLE scan started"
except:
  # Failed to open
  sock = None
  print "Failed to open BLE device."

if sock:
  # We have device access, start BLE scan
  cmd_pkt = struct.pack("<BB", 0x01, 0x00)
  bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)
  # Loop
  while True:
    # Save the current filter setting
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    # Set filter for getting HCI events
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
    # Get and decode data
    print decode_beacon.bluez_decode_beacons(sock.recv(255))
    # Restore the filter setting
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)

