# CertSlayer
This is a tool to instantly test if an application handles SSL certificates the way it is supposed to.

## Todo
* Add an option to set the listening port of the proxy server :)
* Add more certificate test cases

## Usage

- Remember to install certslayer.net.crt as a trusted root CA Certificate

> python CertSlayer.py -h

```
Usage: CertSlayer.py [options]

Options:
  -h, --help            show this help message and exit
  -d DOMAINS_ARG, --domains=DOMAINS_ARG   Set a list of comma-separated domains
  -v, --verbose         Verbose mode
```

> python CertSlayer.py -d www.google.com


The proxy server binds to 8080 and redirects the connections made to the monitored domains to a
rouge web server that it is setup on the fly with a specific test certificate.

It generates a .CSV with the results of every test:

Example:
```
Client Address,Hostname,Current TestCase,Expected,Actual
127.0.0.1,www.google.com,Trusted CA Invalid Signature,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Signed with Unknown CA,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Signed with CertSlayer CA,Certificate Accepted,Certificate Accepted
127.0.0.1,www.google.com,Self Signed Certificate,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Wrong CNAME,Certificate Rejected,Certificate Accepted
127.0.0.1,www.google.com,Signed with MD5,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Signed with MD4,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Expired Certificate,Certificate Rejected,Certificate Rejected
127.0.0.1,www.google.com,Not Yet Valid Certificate,Certificate Rejected,Certificate Rejected
```
## Author
* [Enrique Nissim](https://twitter.com/kiqueNissim) (developer)