# py-levin

> The Levin network protocol is an implementation of peer-to-peer (P2P) communications found in a large number of cryptocurrencies, including basically any cryptocurrency that is a descendant from the CryptoNote project.

## Example usage:

Ask a node for it's peer list, sorted on `last_seen`:

`python3 peer_retreiver.py 212.83.175.67 18080`

```python
>> created packet 'handshake'
>> sent packet 'handshake'
<< received packet 'support_flags'
<< parsed packet 'support_flags'
<< received packet 'handshake'
<< parsed packet 'handshake'

99.48.XX.XX:18080
62.24.XX.XX:18080
93.44.XX.XX:18080
238.137.XX.XX:18080
163.86.XX.XX:18080
250.227.XX.XX:18080
[...]
```

### Some notes

A Levin header (33 bytes) looks like this:

1. `u_int64` - A levin signature. `01 21 01 01 01 01 01 01` also known as 'Benders nightmare'.
2. `u_int64` - Payload size as an indicator of how many bytes to read from the network.
3. `bool` - Recipient should return data.
4. `u_int32` - The command. `e9 03 00 00` - Possible commands: `1001`, `1007`, etc. See `constants.py`.
5. `int32` - Return code.
6. `u_int32` - Flags.
5. `u_int32` - Protocol version. Usually `01`

The payload that comes after that is a serialized Boost struct, which can be found 
in the Monero codebase, e.g: [cryptonote_protocol_defs.h](https://github.com/monero-project/monero/blob/58ce16d4d91518b674a5d46419809f56f71d9114/src/cryptonote_protocol/cryptonote_protocol_defs.h).
The terminology for a (possible nested collection) of structs is called a `Section()` in this module. 

For the actual serialization from the perspective of Monero, check out [portable_storage_to_bin.h](https://github.com/monero-project/monero/blob/58ce16d4d91518b674a5d46419809f56f71d9114/contrib/epee/include/storages/portable_storage_to_bin.h)

For deserialization look at `Reader.read_storage_entry()` and `Reader.read()`.

Data is almost always in little-endian byte order, with the exception of keys (strings) for values in serialized structs.

Lastly, this module is presented as 'best effort' and, for example, does not guarantee that all Levin data types are supported.

### References
- [Monerujo](https://github.com/m2049r/xmrwallet/tree/master/app/src/main/java/com/m2049r/levin)
- [Monero codebase](https://github.com/monero-project/monero)
- [CVE-2018-3972](https://www.talosintelligence.com/reports/TALOS-2018-0637/)

### Thanks

- Big thanks to [m2049r](https://github.com/m2049r/) for his Java implementation of Levin on Monerujo (remote node finder).
- notmike

### License

© 2018 WTFPL – Do What the Fuck You Want to Public License