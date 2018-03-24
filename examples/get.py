from treq_kerberos import TreqKerberosAuth
import treq_kerberos
from twisted.internet import defer, reactor

# Get a URL that requires Kerberos authentication.


@defer.inlineCallbacks
def example():
    url = 'https://errata.devel.redhat.com/'
    auth = TreqKerberosAuth()
    try:
        response = yield treq_kerberos.get(url, auth=auth)
        content = yield response.content()
        print(content)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    d = example()
    d.addCallback(lambda ign: reactor.stop())
    d.addErrback(lambda ign: reactor.stop())
    reactor.run()
