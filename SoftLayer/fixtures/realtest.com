$ORIGIN realtest.com.
$TTL 86400
@ IN SOA ns1.softlayer.com. support.softlayer.com. (
                       2014052300        ; Serial
                       7200              ; Refresh
                       600               ; Retry
                       1728000           ; Expire
                       43200)            ; Minimum

@                      86400    IN NS    ns1.softlayer.com.
@                      86400    IN NS    ns2.softlayer.com.

                        IN MX 10 test.realtest.com.
testing                86400    IN A     127.0.0.1
testing1               86400    IN A     12.12.0.1
server2      IN   A  1.0.3.4
ftp                             IN  CNAME server2
dev.realtest.com    IN  TXT "This is just a test of the txt record"
    IN  AAAA  2001:db8:10::1
spf  IN TXT "v=spf1 ip4:192.0.2.0/24 ip4:198.51.100.123 a -all"

