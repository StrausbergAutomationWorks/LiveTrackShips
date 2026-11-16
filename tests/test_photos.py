"""Vessel photos and the link out (backlog 346). The pure helpers, the book's queue, answers, cache and waiters,
and the three requests against a fake session holding real response shapes (bin\\lts346_probe.txt).
Runs inside the HA container: python lts_boxtest_clone.py test_photos.py"""
import asyncio
import json
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "custom_components"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from live_track_ships.photos import (                       # noqa: E402
    BATCH, FOUND_TTL_S, NONE_TTL_S, PhotoBook, files_by_imo, photo_from_imageinfo, plain, search_query,
    vessel_links)

passed = failed = 0


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


print("=== the link out ===")
check("by IMO", vessel_links("9321483", "563254800"),
      [{"label": "VesselFinder", "url": "https://www.vesselfinder.com/vessels/details/9321483"}])
check("by MMSI when there is no IMO", vessel_links(None, "366053209")[0]["url"],
      "https://www.vesselfinder.com/vessels/details/366053209")
check("neither: no link", vessel_links(None, None), [])
check("not digits: no link", vessel_links(None, "abc"), [])

print("=== the search ===")
check("one OR search for several", search_query(["9321483", "7390260"]), "haswbstatement:P458=9321483|P458=7390260")


def claim(v, rank="normal"):
    return {"mainsnak": {"datavalue": {"value": v}}, "rank": rank}


ents = {
    "Q1": {"claims": {"P458": [claim("7390260")], "P18": [claim("James R Barker.jpg")]}},
    "Q2": {"claims": {"P458": [claim("8306591")], "P18": [claim("Old.jpg", "deprecated"), claim("New.jpg")]}},
    "Q3": {"claims": {"P458": [claim("1111111")], "P18": [claim("NotAsked.jpg")]}},
    "Q4": {"claims": {"P458": [claim("7514701")]}},
}
got = files_by_imo(ents, ["7390260", "8306591", "7514701"])
check("an asked IMO with an image", got.get("7390260"), "James R Barker.jpg")
check("a deprecated image is skipped", got.get("8306591"), "New.jpg")
check("an item whose IMO was not asked is ignored", "1111111" in got, False)
check("an item with no image gives nothing", "7514701" in got, False)
check("nothing given, nothing found", files_by_imo(None, ["1"]), {})

print("=== the credit ===")
check("a Commons user link becomes its text",
      plain('<a href="//commons.wikimedia.org/wiki/User:Solomon203" title="User:Solomon203">Solomon203</a>'),
      "Solomon203")
check("entities unescaped, whitespace one line", plain("A &amp; B\n  photo"), "A & B photo")
check("cut to 120", len(plain("x" * 500)), 120)
check("None is empty", plain(None), "")

PAGE = {"title": "File:Alcatel-Lucent Lodbrog at Port of Keelung 20141220.jpg", "imageinfo": [{
    "thumburl": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/fa/Lodbrog.jpg/330px-Lodbrog.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo",
    "thumbwidth": 320, "thumbheight": 240,
    "descriptionurl": "https://commons.wikimedia.org/wiki/File:Alcatel-Lucent_Lodbrog_at_Port_of_Keelung_20141220.jpg",
    "extmetadata": {"Artist": {"value": '<a href="//commons.wikimedia.org/wiki/User:Solomon203">Solomon203</a>'},
                    "LicenseShortName": {"value": "CC BY-SA 4.0"},
                    "LicenseUrl": {"value": "https://creativecommons.org/licenses/by-sa/4.0"}}}]}
p = photo_from_imageinfo(PAGE)
check("the thumbnail, tracking parameters dropped", p["url"],
      "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/fa/Lodbrog.jpg/330px-Lodbrog.jpg")
check("the photo's page", p["page"].startswith("https://commons.wikimedia.org/wiki/File:"), True)
check("credit, licence, its link, the source",
      (p["credit"], p["licence"], p["licence_url"], p["source"]),
      ("Solomon203", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0", "Wikimedia Commons"))
check("size", (p["width"], p["height"]), (320, 240))
pd = photo_from_imageinfo({"imageinfo": [{"thumburl": "//upload.wikimedia.org/x.jpg", "descriptionurl": "http://commons.wikimedia.org/wiki/File:X.jpg",
                                          "extmetadata": {"Artist": {"value": "U.S. Coast Guard District 9 photo"},
                                                          "LicenseShortName": {"value": "Public domain"}}}]})
check("// and http:// become https://", (pd["url"], pd["page"]),
      ("https://upload.wikimedia.org/x.jpg", "https://commons.wikimedia.org/wiki/File:X.jpg"))
check("public domain: no licence link", "licence_url" in pd, False)
check("no author: a stated fallback, never empty",
      photo_from_imageinfo({"imageinfo": [{"thumburl": "https://a/b.jpg", "descriptionurl": "https://c/d"}]})["credit"],
      "Wikimedia Commons contributor")
check("no thumbnail: no photo", photo_from_imageinfo({"imageinfo": [{"descriptionurl": "https://c/d"}]}), None)
check("a non-https thumbnail: no photo", photo_from_imageinfo({"imageinfo": [{"thumburl": "ftp://x", "descriptionurl": "https://c"}]}), None)

print("=== the book ===")


class Clock:
    t = 1_000_000.0

    def __call__(self):
        return self.t


clock = Clock()
d = tempfile.mkdtemp()
path = os.path.join(d, "saw_vessel_photos.json")
book = PhotoBook(path, clock=clock)
calls = []
w1 = lambda: calls.append("a")      # noqa: E731
check("unknown: None, queued", book.photo("7390260", w1), None)
check("asking twice queues once", (book.photo("7390260", w1), len(book.take_batch())), (None, 1))
for i in range(BATCH + 5):
    book.photo(f"{9000000 + i}")
b1 = book.take_batch()
check(f"a batch is at most {BATCH}", len(b1), BATCH)
check("the rest wait for the next", len(book.take_batch()), 5)
book.photo("7390260", w1)
batch = book.take_batch()
waiters = book.settle(batch, {"7390260": {"url": "https://x/t.jpg"}})
check("the waiter is returned once", len(waiters), 1)
check("found: the photo, nothing queued", (book.photo("7390260"), book.take_batch()), ({"url": "https://x/t.jpg"}, []))
book.settle(["8306591"], {})
check("none found: None, and not asked again within 14 days", (book.photo("8306591"), book.take_batch()), (None, []))
clock.t += NONE_TTL_S + 1
check("after 14 days a ship with none is asked again", (book.photo("8306591"), book.take_batch()), (None, ["8306591"]))
check("a found photo is still fresh then", book.take_batch() == [] and book.photo("7390260") is not None, True)
clock.t += FOUND_TTL_S
check("after 30 days a found photo is kept but asked again", (book.photo("7390260") is not None, book.take_batch()), (True, ["7390260"]))
w2 = lambda: calls.append("b")      # noqa: E731
book.photo("7514701", w2)
book.forget_waiter("7514701", w2)
check("a forgotten waiter is not called", book.settle(["7514701"], {}), [])
book.save()
book2 = PhotoBook(path, clock=clock)
book2.load()
check("the cache is read back", book2.photo("7390260"), {"url": "https://x/t.jpg"})
open(path, "w").write("{not json")
book3 = PhotoBook(path, clock=clock)
book3.load()
check("a broken cache starts empty, no crash", book3.photo("7390260"), None)
check("no cache file: empty, no crash", (PhotoBook(os.path.join(d, "none.json")).load(), True)[1], True)

print("=== the three requests ===")


class Resp:
    def __init__(self, data):
        self.data = data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    def raise_for_status(self):
        pass

    async def json(self):
        return self.data


class Session:
    def __init__(self, answers):
        self.answers = list(answers)
        self.asked = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.asked.append((url, params, headers))
        return Resp(self.answers.pop(0))


search = {"query": {"search": [{"title": "Q1"}, {"title": "Q2"}]}}
entities = {"entities": ents}
commons = {"query": {"normalized": [{"from": "File:James R Barker.jpg", "to": "File:James R Barker.jpg"}],
                     "pages": {"1": dict(PAGE, title="File:James R Barker.jpg"),
                               "2": {"title": "File:New.jpg", "missing": ""}}}}
s = Session([search, entities, commons])
found = asyncio.run(PhotoBook(path).lookup(s, ["7390260", "8306591"]))
check("found by IMO", list(found), ["7390260"])
check("a missing Commons file is no photo", "8306591" in found, False)
check("three requests: search, entities, Commons", [a[0].split("/")[2] for a in s.asked],
      ["www.wikidata.org", "www.wikidata.org", "commons.wikimedia.org"])
check("the search is the OR of the IMOs", s.asked[0][1]["srsearch"], "haswbstatement:P458=7390260|P458=8306591")
check("every request names us (Wikimedia's User-Agent policy)",
      all("StrausbergAutomationWorks" in a[2]["User-Agent"] for a in s.asked), True)
s = Session([{"query": {"search": []}}])
check("no hits: one request, nothing found", (asyncio.run(PhotoBook(path).lookup(s, ["1"])), len(s.asked)), ({}, 1))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
