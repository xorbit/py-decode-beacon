import decode_beacon
import struct

print "BlueZ message with 1 iBeacon advertisement"
bz1 = ''.join([chr(int(c, 16)) for c in ("""
04 3E 2A 02 01 03 00 EC F8 00 EE F3 0C 1E 02 01
04 1A FF 4C 00 02 15 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4E C1 BB""".split())])
print decode_beacon.bluez_decode_beacons(bz1)

print "BlueZ message with 2 iBeacon advertisements, the second without flags"
bz2 = ''.join([chr(int(c, 16)) for c in ("""
04 3E 4F 02 02
03 00 EC F8 00 EE F3 0C 1E 02 01
04 1A FF 4C 00 02 15 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4E C1 BB
03 00 EC F8 00 EE F3 0D 1B
1A FF 4C 00 02 15 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4F C1 B0
""".split())])
print decode_beacon.bluez_decode_beacons(bz2)

print "BlueZ message with 1 iBeacon and 1 AltBeacon advertisement"
bz3 = ''.join([chr(int(c, 16)) for c in ("""
04 3E 50 02 02
03 00 EC F8 00 EE F3 0C 1E 02 01
04 1A FF 4C 00 02 15 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4E C1 BB
03 00 EC F8 00 EE F3 0D 1C
1B FF 44 01 BE AC 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4F C1 55
B1
""".split())])
print decode_beacon.bluez_decode_beacons(bz3)

print "BlueZ message with an Eddystone UID advertisement"
bz4 = ''.join([chr(int(c, 16)) for c in ("""
04 3E 29 02 01 00 00 6D 5F 57 C5 17 01 1D 02 01 06 03 03 AA FE
15 16 AA FE 00 DE 5D C3 34 87 F0 2E 47 7D 40 58 01 17 C5 57 5F 6D B8
""".split())])
print decode_beacon.bluez_decode_beacons(bz4)

print "BlueZ message with an Eddystone URL advertisement"
bz5 = ''.join([chr(int(c, 16)) for c in ("""
04 3E 27 02 01 00 00 6D 5F 57 C5 17 01 1B 02 01 06 03 03 AA FE
13 16 AA FE 10 DE 02 74 6F 6B 2E 74 63 2F 57 6A 2F 42 43 56 B8
""".split())])
print decode_beacon.bluez_decode_beacons(bz5)

print "BlueZ message with an Eddystone TLM advertisement"
bz6 = ''.join([chr(int(c, 16)) for c in ("""
04 3E 25 02 01 00 00 6D 5F 57 C5 17 01 19 02 01 06 03 03 AA FE
11 16 AA FE 20 00 0C 3C 20 00 00 00 0F BC 00 00 49 BA B7
""".split())])
print decode_beacon.bluez_decode_beacons(bz6)
