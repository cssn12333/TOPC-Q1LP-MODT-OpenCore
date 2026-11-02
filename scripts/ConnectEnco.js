// One-shot use of the built-in IOBluetooth API. No scan, daemon or pairing deletion.
ObjC.import('Foundation');
ObjC.import('IOBluetooth');
function run(argv) {
    var address = argv.length === 1 ? String(argv[0]).trim() : '';
    if (!/^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$/.test(address)) {
        throw new Error('Expected the locally recorded headset address');
    }
    var device = $.IOBluetoothDevice.deviceWithAddressString(address);
    if (device.isNil()) throw new Error('IOBluetooth device unavailable');
    var status = Number(device.openConnection);
    return JSON.stringify({operation: 'openConnection without inquiry', status: status,
        connected: Boolean(device.isConnected), paired: Boolean(device.isPaired)});
}
