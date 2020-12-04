import os
from treq_kerberos import TreqKerberosAuth
import treq_kerberos
from treq.testing import StubTreq
from twisted.web.resource import Resource
import pytest
import pytest_twisted

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


class FakeTestResource(Resource):
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
                return b'<html>success</html>'
            request.setResponseCode(403)
            return b'failed SPNEGO auth'
        request.setResponseCode(401)
        request.setHeader(b'WWW-Authenticate', b'Negotiate')
        return b'retry with SPNEGO authentication'


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


class TestRequests(object):
    @pytest.fixture(autouse=True)
    def patch_deps(self, monkeypatch):
        monkeypatch.setattr('treq_kerberos.treq',
                            StubTreq(FakeTestResource()))
        monkeypatch.setattr('treq_kerberos.kerberos', FakeKerberos())

    url = 'https://example.com/'
    auth = TreqKerberosAuth()

    @pytest_twisted.inlineCallbacks
    def test_get(self):
        response = yield treq_kerberos.get(self.url, auth=self.auth)
        yield self.assert_response_ok(response)

    @pytest_twisted.inlineCallbacks
    def test_put(self):
        response = yield treq_kerberos.put(self.url, auth=self.auth)
        yield self.assert_response_ok(response)

    @pytest_twisted.inlineCallbacks
    def test_patch(self):
        response = yield treq_kerberos.patch(self.url, auth=self.auth)
        yield self.assert_response_ok(response)

    @pytest_twisted.inlineCallbacks
    def test_post(self):
        response = yield treq_kerberos.post(self.url, auth=self.auth)
        yield self.assert_response_ok(response)

    @pytest_twisted.inlineCallbacks
    def test_head(self):
        response = yield treq_kerberos.head(self.url, auth=self.auth)
        assert response.code == 200
        content = yield response.content()
        assert content == b''

    @pytest_twisted.inlineCallbacks
    def test_delete(self):
        response = yield treq_kerberos.delete(self.url, auth=self.auth)
        yield self.assert_response_ok(response)

    @pytest_twisted.inlineCallbacks
    def assert_response_ok(self, response):
        assert response.code == 200
        content = yield response.content()
        assert content == b'<html>success</html>'
