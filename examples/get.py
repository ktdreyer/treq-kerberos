from treq_kerberos import TreqKerberosAuth
import treq_kerberos
from twisted.internet import defer
from twisted.internet.task import react

# Get a URL that requires Kerberos authentication.


@defer.inlineCallbacks
def example(reactor):
    url = 'https://errata.devel.redhat.com/'
    auth = TreqKerberosAuth()
    response = yield treq_kerberos.get(url, auth=auth)
    content = yield response.content()
    print(content)


if __name__ == '__main__':
    react(example)
