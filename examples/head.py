from treq_kerberos import TreqKerberosAuth
import treq_kerberos
from twisted.internet import defer
from twisted.internet.task import react

# HEAD a URL that requires Kerberos authentication.


@defer.inlineCallbacks
def example(reactor):
    url = 'https://errata.devel.redhat.com/'
    auth = TreqKerberosAuth()
    response = yield treq_kerberos.head(url, auth=auth)
    headers = yield response.headers
    print(headers)


if __name__ == '__main__':
    react(example)
