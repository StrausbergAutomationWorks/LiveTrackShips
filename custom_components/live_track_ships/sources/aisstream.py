"""aisstream.io - the primary source. Global, free, websocket push.

⚠ SINCE 2026-10-30 THE CONNECTION IS SHARED (backlog 315): saw_livetrack.aisstream
holds ONE client per Home Assistant, at most two connections per API key - an
AREA subscription (the union of every area consumer's boxes; every Ships
aisstream entry is one) and a VESSELS subscription (MMSI lists; Live Track
SALT). The parser, the heartbeat, the backoff with jitter, binary frames and
the refusal frame all moved there VERBATIM from this file at ccebaee; read
35_Dependencies/third_party/aisstream/SSOT.md for the service's rules, which
bind every consumer. What stays here is the Source seam: this adapter adds the
entry's boxes as one area consumer and yields what the client delivers.

⚠ TWO SHIPS ENTRIES ON ONE KEY NOW SHARE ONE CONNECTION. Before, each took one
of aisstream's three per account and per IP. A change of boxes (an options
change reloads the entry) replaces the subscription on the open socket, paced
at most once a second by the client; the last consumer of a connection closes
it.

⚠ TEAR DOWN CLEANLY. close() removes the consumer; a consumer left behind keeps
its connection open and its queue growing.
"""

from __future__ import annotations

import asyncio

from saw_livetrack import aisstream as _lib

from .statics import StaticCache


class AisStreamSource:
    """One Ships entry's boxes on the instance's shared aisstream client."""

    domain = "live_track_ships"

    def __init__(self, session, api_key, boxes, statics=None, store=None,
                 consumer=None, create_task=None, mmsis=None):
        self._session = session
        self._key = api_key
        self._boxes = boxes
        # Backlog 343: a watch entry's list. With MMSIs this is a VESSELS
        # consumer (worldwide, the list only), else an AREA consumer.
        self._mmsis = list(mmsis) if mmsis else None
        # store is hass.data in production: one client per Home Assistant. A
        # private client when none is given (tests, scripts).
        self._client = _lib.shared(store if store is not None else {})
        self._consumer = consumer or f"{self.domain}:{id(self)}"
        self._create_task = create_task
        # The client's connections parse into client.statics, the instance's
        # one cache (Ships loads and saves it, item 262). This parser serves
        # _to_observation only.
        self._parser = _lib.Parser(
            statics if statics is not None else self._client.statics,
            self.domain)
        self._added = False

    @property
    def statics(self) -> StaticCache:
        return self._client.statics

    def _to_observation(self, obj):
        """One aisstream message -> Observation or None (the shared parser)."""
        return self._parser._to_observation(obj)

    async def observations(self):
        """Yield Observations until closed. The client reconnects; nothing
        here does."""
        queue: asyncio.Queue = asyncio.Queue()
        if self._mmsis:
            self._client.add_vessels(self._consumer, self._session, self._key,
                                     self._mmsis, queue.put_nowait,
                                     self.domain, create_task=self._create_task)
        else:
            self._client.add_area(self._consumer, self._session, self._key,
                                  self._boxes, queue.put_nowait, self.domain,
                                  create_task=self._create_task)
        self._added = True
        try:
            while True:
                yield await queue.get()
        finally:
            await self.close()

    async def close(self):
        if self._added:
            self._added = False
            await self._client.remove(self._consumer)
