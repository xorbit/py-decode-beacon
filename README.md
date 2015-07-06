# Python beacon advertisement decoder

Copyright (c) 2015 Patrick Van Oosterwijck

Released under the [MIT license](LICENSE).

## Library

The file [decode_beacon.py](decode_beacon.py) provides an easily extensible decoder for beacon advertisement packets as received from BlueZ HCI events.  Currently it supports [Apple iBeacon](https://developer.apple.com/ibeacon/) and the free [AltBeacon](https://github.com/AltBeacon/spec) specifications.

I used various sources to try to understand the BlueZ HCI packet and iBeacon formats, this is documented in the [IBEACON.md](IBEACON.md) file.

## Examples

The file [decode_test.py](decode_test.py) contains a couple of simple hardcoded test HCI packets to test the decoder.

The file [bluez_scan.py](bluez_scan.py) contains a simple BlueZ HCI advertisement packet scanner based on [this code](https://github.com/switchdoclabs/iBeacon-Scanner-).
