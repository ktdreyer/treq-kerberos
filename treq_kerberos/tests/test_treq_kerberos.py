import os
from treq_kerberos import TreqKerberosAuth
import treq_kerberos
from treq.testing import StubTreq
from twisted.web.resource import Resource
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


class _ReleaseTestResource(Resource):
    """
    A twisted.web.resource.Resource that represents a kerberized
    response.
    """
    isLeaf = True

    def render(self, request):
        # If request.headers lacks "Authorization" header, return a 401 with
        # "WWW-Authenticate: Negotiate" header.
        auth_header = request.getHeader('authorization')
        if auth_header:
            if auth_header == 'Negotiate NEGOTIATEDETAILSHERE':
                request.setResponseCode(200)
                return '<html>success</html>'
            request.setResponseCode(403)
            return 'failed SPNEGO auth'
        request.setResponseCode(401)
        request.setHeader(b'WWW-Authenticate', b'Negotiate')
        return 'retry with SPNEGO authentication'


class FakeKerberosContext(object):
    pass


class FakeKerberos(object):
    """ Simple kerberos client that returns a static NEGOTIATEDETAILS text """
    def authGSSClientInit(self, principal):
        return (None, FakeKerberosContext())

    def authGSSClientStep(self, krb_context, *args):
        return

    def authGSSClientResponse(self, krb_context):
        return 'NEGOTIATEDETAILSHERE'


class TestGet(object):
    @pytest.fixture(autouse=True)
    def patch_deps(self, monkeypatch):
        monkeypatch.setattr('treq_kerberos.treq',
                            StubTreq(_ReleaseTestResource()))
        monkeypatch.setattr('treq_kerberos.kerberos', FakeKerberos())

    @pytest.inlineCallbacks
    def test_get(self):
        url = 'https://example.com/'
        auth = TreqKerberosAuth()
        response = yield treq_kerberos.get(url, auth=auth)
        assert response.code == 200
        content = yield response.content()
        assert content == '<html>success</html>'

    # TODO: test_post, test_put, test_patch
