.. _core:

=================
 Blockchain core
=================

Transaction class
-----------------

.. autoclass:: dposlib.blockchain.tx.Transaction
    :members:

Crypto utils
------------

.. automodule:: dposlib.ark.crypto
    :members:

Signature utils
---------------

.. automodule:: dposlib.ark.sig
    :members:

Transaction builders
--------------------

.. autofunction:: dposlib.ark.v3.transfer

.. autofunction:: dposlib.ark.v3.registerSecondSecret

.. autofunction:: dposlib.ark.v3.registerSecondPublicKey

.. autofunction:: dposlib.ark.v3.registerAsDelegate

.. autofunction:: dposlib.ark.v3.upVote

.. autofunction:: dposlib.ark.v3.downVote

.. autofunction:: dposlib.ark.v3.registerMultiSignature

.. autofunction:: dposlib.ark.v3.registerIpfs

.. autofunction:: dposlib.ark.v3.multiPayment

.. autofunction:: dposlib.ark.v3.delegateResignation

.. autofunction:: dposlib.ark.v3.htlcSecret

.. autofunction:: dposlib.ark.v3.htlcLock

.. autofunction:: dposlib.ark.v3.htlcClaim

.. autofunction:: dposlib.ark.v3.htlcRefund

API
---

.. automodule:: dposlib.ark.v2.api
    :members:
