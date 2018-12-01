# py-levin

The Levin network protocol is an implementation of peer-to-peer (P2P) communications found in a large number of cryptocurrencies, including basically any cryptocurrency that is a descendant from the CryptoNote project. 

This module provides the building blocks to create and parse Levin packets.

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

### References
- [Monerujo](https://github.com/m2049r/xmrwallet/tree/master/app/src/main/java/com/m2049r/levin)
- [Monero codebase](https://github.com/monero-project/monero)
- [CVE-2018-3972](https://www.talosintelligence.com/reports/TALOS-2018-0637/)

### Thanks

- m2049r
- notmike

### License

© 2018 WTFPL – Do What the Fuck You Want to Public License