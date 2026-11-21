"""Vessel photos and the link out (backlog 346). Since saw-livetrack 0.2.43 (2026-11-21) the lookup is the library's
(saw_livetrack.vessel_photos: by IMO, and by MMSI when the IMO finds nothing; added 2026-11-21),
and its pure helpers, queue, cache, waiters and requests are tested THERE (tests/test_vessel_photos.py). This file
checks the link out and how this integration asks the book. Invented numbers only.
Runs inside the HA container: python lts_boxtest_clone.py test_photos.py"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "custom_components"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from saw_livetrack import vessel_photos as lib                 # noqa: E402
from live_track_ships.photos import STORE_KEY, vessel_links    # noqa: E402

passed = failed = 0


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


print("=== the link out ===")
check("by IMO", vessel_links("9000001", "300000001"),
      [{"label": "VesselFinder", "url": "https://www.vesselfinder.com/vessels/details/9000001"}])
check("by MMSI when there is no IMO", vessel_links(None, "300000001")[0]["url"],
      "https://www.vesselfinder.com/vessels/details/300000001")
check("neither: no link", vessel_links(None, None), [])
check("not digits: no link", vessel_links(None, "abc"), [])

print("=== the library's book ===")
check("the store key is the library's", STORE_KEY, lib.STORE_KEY)
check("not this integration's old key", STORE_KEY != "saw_vessel_photos", True)

src = (ROOT / "custom_components" / "live_track_ships" / "photos.py").read_text(encoding="utf-8")
check("no lookup code left here", ("wbgetentities" in src, "class PhotoBook" in src), (False, False))
check("shared() starts the library's book", "await _lib.shared(hass.data, hass.config.path(\".storage\")" in src)

geo = (ROOT / "custom_components" / "live_track_ships" / "geo_location.py").read_text(encoding="utf-8")
check("asks by IMO and MMSI", "book.photo(imo, self._obs.identity, self._photo_arrived)" in geo)
check("forgets its waiter on removal", "book.forget_waiter(self._photo_arrived)" in geo)
check("no per-IMO waiter bookkeeping left", "_photo_imo" in geo, False)

print("=== the fallback, as this integration asks ===")
book = lib.PhotoBook("/nonexistent/x.json")
calls = []
cb = lambda: calls.append(1)                                    # noqa: E731
book.photo("9000001", "300000001", cb)
check("IMO asked first", book.take_batch(), ["imo:9000001"])
for f in book.settle(["imo:9000001"], {}):
    f()
check("the entity is told", calls, [1])
book.photo("9000001", "300000001", cb)
check("then the MMSI", book.take_batch(), ["mmsi:300000001"])
photo = {"url": "https://img.example.org/a.jpg", "page": "https://commons.example.org/a", "credit": "Ann Example",
         "licence": "CC0", "source": "Wikimedia Commons"}
book.settle(["mmsi:300000001"], {"mmsi:300000001": photo})
check("the MMSI's photo is shown", book.photo("9000001", "300000001", cb), photo)
book.photo(None, "300000002", cb)
check("a vessel without an IMO is asked by MMSI at once", book.take_batch(), ["mmsi:300000002"])

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
