# Decoding an iBeacon advertisement packet received as a BlueZ HCI event

This document contains information on how to decode an iBeacon advertisement packet.  The information was gathered from various sources such as the [BlueZ source](http://www.bluez.org/download/) and [this Stackoverflow answer](http://stackoverflow.com/questions/18906988/what-is-the-ibeacon-bluetooth-profile/19040616#19040616).

To hopefully help understand the structure of the BlueZ event packet containing the iBeacon advertisement, we'll work from an example.

### Example BlueZ packet for iBeacon

```
04 3E 2A 02 01 03 00 EC F8 00 EE F3 0C 1E 02 01
04 1A FF 4C 00 02 15 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4E C1 BB
```

### Byte 0:
```
04: Packet type HCI_EVENT_PKT
```

When you set a filter for this packet type, it's the only ones you'll get.

### Byte 1:
```
3E: Event LE_META_EVENT
```

The only event you're interested in if you're just scanning for beacons.

### Byte 2:
```
2A: Packet length = 42
```

This is the length of the "LE meta event" packet.

### Byte 3:
```
02: The meta event is EVT_LE_ADVERTISING_REPORT
```

The only event you're interested in if you're just scanning for beacons.

### Byte 4:
```
01: The number of advertising reports in the packet = 1
```

This can be followed by one or more LE advertising info structures,
depending on this number.

### Byte 5, byte 0 of LE advertising info:
```
03: Event type of LE advertising info structure
```

First byte of the LE advertising info structure. Don't know the values for
this.

### Byte 6, byte 1 of LE advertising info:
```
00: BT device address type
```

Part of the LE advertising info structure. Don't know the values for this.

### Byte 7-12, byte 2-7 of LE advertising info:
```
EC F8 00 EE F3 0C: BT device address (MAC address) = 0C:F3:EE:00:F8:EC
```

Part of the LE advertising info structure.

### Byte 13, byte 8 of LE advertising info:
```
1E: Advertising data length = 30
```

The advertising data is embedded inside the LE advertising info structure
after this length byte.

### Byte 14, byte 9 of LE advertising info, byte 0 of ad data:
```
02: Length of first ad structure = 2
```

I think this is always 2 for an iBeacon.

### Byte 15, byte 10 of LE advertising info, byte 1 of ad data:
```
01: Ad structure type "flags"
```

### Byte 16, byte 11 of LE advertising info, byte 2 of ad data:
```
04: Ad flags
```

Meaning of flags:
* bit 0: LE Limited Discoverable Mode
* bit 1: LE General Discoverable Mode
* bit 2: BR/EDR Not Supported
* bit 3: Simultaneous LE and BR/EDR to Same Device Capable (controller)
* bit 4: Simultaneous LE and BR/EDR to Same Device Capable (Host)

Source: [this Stackoverflow answer](http://stackoverflow.com/questions/18906988/what-is-the-ibeacon-bluetooth-profile/19040616#19040616)

### Byte 17, byte 12 of LE advertising info, byte 3 of ad data:
```
1A: Length of second ad structure = 26
```

### Byte 18, byte 13 of LE advertising info, byte 4 of ad data:
```
FF: Ad structure type "manufacturer specific"
```

### Byte 19-20, byte 14-15 of LE advertising info, byte 5-6 of ad data, byte 0-1 of mfg spec data:
```
4C 00: Manufacturer code 0x004C = Apple
```

16-bit little endian format, complete manufacturers list on the [Bluetooth SIG site](https://www.bluetooth.org/en-us/specification/assigned-numbers/company-identifiers).

### Byte 21, byte 16 of LE advertising info, byte 7 of ad data, byte 2 of mfg spec data:
```
02: iBeacon mfg spec ad indicator
```

### Byte 22, byte 17 of LE advertising info, byte 8 of ad data, byte 3 of mfg spec data:
```
15: Mfg spec data length = 21
```

### Byte 23-38, byte 18-33 of LE advertising info, byte 9-24 of ad data, byte 4-19 of mfg spec data, byte 0-15 of iBeacon data:
```
8D EE FB B9 F7 38 42 97 80 40 96 66 8B B4 42 81: UUID = 8deefbb9f7384297804096668bb44281
```

### Byte 39-40, byte 34-35 of LE advertising info, byte 25-26 of ad data, byte 20-21 of mfg spec data, byte 16-17 of iBeacon data:
```
13 88: Major = 0x1388 = 5000
```

16-bit big endian format.

### Byte 41-42, byte 36-37 of LE advertising info, byte 27-28 of ad data, byte 22-23 of mfg spec data, byte 18-19 of iBeacon data:
```
0F 4E: Minor = 0x0F4E = 3918
```

16-bit big endian format.

### Byte 43, byte 38 of LE advertising info, byte 29 of ad data, byte 24 of mfg spec data, byte 20 of iBeacon data:
```
C1: Reference RSSI for the beacon at 1 meter distance = -63 dBm
```

Signed (2's complement) byte value indicating signal strength.  This is characterized by the manufacturer during production and by using this calibration value it is possible to do distance calculations using beacons with different transmit power.

### Byte 44, byte 39 of LE advertising info
```
BB: Observed RSSI of the beacon advertisement = -69 dBm
```

Signed (2's complement) byte value indicating signal strength.  This is the signal strength actually measured by the BLE radio while receiving the advertisement packet.  Together with the reference RSSI, this value can be used for rough distance calculations or, when multiple beacons are used, for position triangulation.

