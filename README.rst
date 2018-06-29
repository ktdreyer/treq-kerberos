Kerberos authentication with Twisted's treq
===========================================

treq-kerberos adds Kerberos (SPNEGO/HTTP Negotiate) authentication for treq.

`treq <https://github.com/twisted/treq>`_ is a requests-like library for
making HTTP requests asynchronously (non-blocking) using the Twisted framework.

treq-kerberos is inspired by `requests-kerberos
<https://github.com/requests/requests-kerberos>`_.


Simple Example: making a request
--------------------------------

GET a URL that requires Kerberos authentication:

.. code-block:: python

    from treq_kerberos import TreqKerberosAuth
    import treq_kerberos
    from twisted.internet import defer, reactor


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
        example().addCallback(lambda ign: reactor.stop())
        reactor.run()


(See the full script at ``examples/get.py``.)


Preemptive authentication
-------------------------

Ordinarily, web clients attempt HTTP Negotiate authentication only after
receiving a HTTP ``401`` response from the web server. The client then retries
with the proper ``Authentication: Negotiate ...`` header.

If you know your web server will always prompt for HTTP Negotiate
authentication, you can skip the first round-trip by setting the
``force_preemptive=True`` keyword argument when instantiating
``TreqKerberosAuth``. (This behavior is identical to request-kerberos's
``force_preemptive`` kwarg for ``HTTPKerberosAuth``.)

.. code-block:: python

    @defer.inlineCallbacks
    def example():
        url = 'https://errata.devel.redhat.com/'
        auth = TreqKerberosAuth(force_preemptive=True)
        response = yield treq_kerberos.get(url, auth=auth)
        # ...


Integration with treq upstream
------------------------------

At the time of this writing, treq supports HTTP Basic authentication by passing
a ``(username, password)`` tuple via an ``auth`` kwarg.

This module borrows that same ``auth`` concept. You pass in a
``TreqNegotiateAuth`` object instead of the username and password tuple.

Eventually treq may allow more flexible authentication designs that could be
suitable to third parties. When this is available in treq upstream, I want
treq-kerberos module to support it, ideally minimizing the API changes to
support such a future transition.

TODO:
=====
* Rewrite to use python-gssapi instead of python-kerberos (similar to
  `requests-gssapi <https://github.com/pythongssapi/requests-gssapi>`_).
* Better API documentation
