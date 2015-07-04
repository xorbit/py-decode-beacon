import decode_beacon
import struct

# BlueZ message with 1 iBeacon advertisement
bz1 = ''.join([chr(int(c, 16)) for c in ("""04 3E 2A 02 01 03 00 EC F8 00 EE F3 0C 1E 02 01
04 1A FF 4C 00 02 15 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4E C1 BB""".split())])
print decode_beacon.bluez_decode_beacons(bz1)

# BlueZ message with 2 iBeacon advertisements, the second without flags
bz2 = ''.join([chr(int(c, 16)) for c in ("""04 3E 4F 02 02
03 00 EC F8 00 EE F3 0C 1E 02 01
04 1A FF 4C 00 02 15 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4E C1 BB
03 00 EC F8 00 EE F3 0D 1B
1A FF 4C 00 02 15 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4F C1 B0
""".split())])

# BlueZ message with 1 iBeacon and 1 AltBeacon advertisement
print decode_beacon.bluez_decode_beacons(bz2)
bz3 = ''.join([chr(int(c, 16)) for c in ("""04 3E 50 02 02
03 00 EC F8 00 EE F3 0C 1E 02 01
04 1A FF 4C 00 02 15 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4E C1 BB
03 00 EC F8 00 EE F3 0D 1C
1B FF 44 01 BE AC 8D EE FB B9 F7 38 42 97 80
40 96 66 8B B4 42 81 13 88 0F 4F C1 55
B1
""".split())])
print decode_beacon.bluez_decode_beacons(bz3)

