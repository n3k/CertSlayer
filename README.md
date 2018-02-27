# CertSlayer
This is a tool to instantly test if an application handles SSL certificates the way it is supposed to.

## Todo
* Add more certificate test cases
* Implement this http://www.cs.bham.ac.uk/~garciaf/publications/spinner.pdf
* Implement STARTTLS

## Usage
The tool supports two modes:
- Proxy: certslayer sets itself as a proxy and monitors for the specified target domains.
- Standalone: certslayer creates a web server configured with the special test certificate. I found this service http://cybernetnews.com/create-free-dns/ to be useful.
- In both cases it will be necessary to install certslayer.net.crt as a trusted root CA Certificate.

> python CertSlayer.py -h

```
Usage: CertSlayer.py [options]

Options:
  -h, --help            show this help message and exit
  -d DOMAINS_ARG, --domain=DOMAINS_ARG
                        Domain to be monitored, might be used multiple times
                        and supports regular expressions (Only valid for proxy
                        mode)
  -p PORT_ARG, --port=PORT_ARG
                        port to listen
  -m MODE_ARG, --mode=MODE_ARG
                        Operation mode: proxy or standalone
  -i HOST_ARG, --hostname=HOST_ARG
                        Hostname: the IP address or Domain name that the
                        certificate CN will stand for (Only valid for
                        standalone mode)
  -v, --verbose         Verbose mode
```

> python CertSlayer.py -d www.google.com -m proxy -p 9090


The proxy server binds to 9090 and redirects the connections made to the monitored domains to a
rogue web server that is setup on the fly with a specific test certificate.

It generates a .CSV with the results of every test:

Example:
```
Client Address,Hostname,Current TestCase,Expected,Actual
127.0.0.1,www.google.com,Trusted CA Invalid Signature,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Signed with Unknown CA,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Signed with CertSlayer CA,Certificate Accepted,Certificate Accepted
127.0.0.1,www.google.com,Self Signed Certificate,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Wrong CNAME,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Signed with MD5,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Signed with MD4,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Expired Certificate,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Not Yet Valid Certificate,Certificate Rejected,Certificate Rejected
```
## Author
* [Enrique Nissim](https://twitter.com/kiqueNissim) (developer)
