from urlparse import urlparse
import kerberos
import treq
from twisted.internet import defer
from twisted.internet import threads

# This module is a drop-in replacement for the treq module, so we provide all
# the methods treq provides:
from treq import *  # NOQA: F401,F403

__version__ = '1.0.0'


class TreqKerberosAuth(object):
    """ Similar to requests-kerberos's HTTPKerberosAuth """
    def __init__(self, force_preemptive=False):
        self.force_preemptive = force_preemptive


def get(url, **kwargs):
    return request('GET', url, **kwargs)


def put(url, data=None, **kwargs):
    return request('PUT', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return request('PATCH', url, data=data, **kwargs)


def post(url, data=None, **kwargs):
    return request('POST', url, data=data, **kwargs)


def head(url, **kwargs):
    return request('HEAD', url, **kwargs)


def delete(url, **kwargs):
    return request('DELETE', url, **kwargs)


@defer.inlineCallbacks
def request(method, url, **kwargs):
    """
    Pass auth=HTTPKerberosAuth() kwarg
    """
    auth = kwargs.get('auth')
    headers = kwargs.get('headers', {})
    # headers = headers.copy() # ? We do modify the dict in place here...
    if isinstance(auth, TreqKerberosAuth):
        del kwargs['auth']
        if auth.force_preemptive:
            # Save a round-trip and set the Negotiate header on the first req.
            headers['Authorization'] = yield negotiate_header(url)
    response = yield treq.request(method=method, url=url, headers=headers,
                                  **kwargs)
    # Retry if we got a 401 / Negotiate response.
    if response.code == 401 and isinstance(auth, TreqKerberosAuth):
        auth_mechs = response.headers.getRawHeaders('WWW-Authenticate')
        if 'Negotiate' in auth_mechs:
            headers['Authorization'] = yield negotiate_header(url)
            response = yield treq.request(method=method, url=url,
                                          headers=headers, **kwargs)
    defer.returnValue(response)


@defer.inlineCallbacks
def negotiate_header(url):
    """
    Return the "Authorization" HTTP header value to use for this URL.
    """
    hostname = urlparse(url).hostname
    _, krb_context = kerberos.authGSSClientInit('HTTP@%s' % hostname)
    # authGSSClientStep goes over the network to the KDC (ie blocking).
    yield threads.deferToThread(kerberos.authGSSClientStep,
                                krb_context, '')
    negotiate_details = kerberos.authGSSClientResponse(krb_context)
    defer.returnValue('Negotiate ' + negotiate_details)
