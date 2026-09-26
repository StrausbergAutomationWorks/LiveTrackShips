"""How the instance ceiling is shared between config entries (SSOT item 253).

⚠ WHY: INSTANCE_MAX_VESSELS (item 246) used to be FIRST-COME. An entry that
heard its vessels first kept its places, and a later entry - or one losing
vessels to its own nearest-N cap - could not add any while the map was full.
Measured 2026-09-23/24: aisstream Oslo-Hamburg held 581 back; a new Digitraffic
Finland entry showed only a few ships until another entry was disabled. A push
source with a queue beats a polling source to every freed slot.

⚠ THE RULE (Lee, 2026-09-24: "use a per-entry quota"): each entry is entitled
to an EQUAL share of the ceiling. An entry that needs less than its share takes
only what it needs, and what it leaves is shared equally among the rest - max-min
fairness, the water-filling allocation. So an entry never gets less than an
equal share if it can fill one, and no slot sits unused while an entry wants
it. A fixed equal split would leave a quiet entry's slots empty while a busy
one was held back.

Pure standard library, deterministic, testable without Home Assistant.
"""

from __future__ import annotations


def effective_ceiling(settings, ceiling: int, floor: int = 1) -> int:
    """The instance ceiling in force (item 264): the LOWEST valid user setting,
    never above `ceiling` nor below `floor`; `ceiling` when nobody set one.
    A value that is not a number is ignored, never read as zero."""
    values = []
    for v in settings:
        if v is None or isinstance(v, bool):
            continue
        try:
            values.append(int(float(v)))
        except (TypeError, ValueError):
            continue
    if not values:
        return int(ceiling)
    return max(int(floor), min(int(ceiling), min(values)))


def allocate(demands: dict[str, int], total: int) -> dict[str, int]:
    """entry_id -> number of vessels it may show. Sum never exceeds total.

    `demands` is what each entry could show: its in-range candidates not owned
    by another entry, already capped by its own max_vessels. Leftover slots
    that do not divide evenly go to entries in entry_id order, so two passes
    with the same demands always give the same answer."""
    alloc: dict[str, int] = {}
    remaining = max(0, int(total))
    pending = sorted(demands, key=lambda e: (max(0, int(demands[e])), e))
    while pending:
        share = remaining // len(pending)
        first = pending[0]
        want = max(0, int(demands[first]))
        if want <= share:
            alloc[first] = want
            remaining -= want
            pending.pop(0)
            continue
        # Everyone left wants at least an equal share: split what remains.
        extra = remaining - share * len(pending)
        for i, e in enumerate(sorted(pending)):
            alloc[e] = share + (1 if i < extra else 0)
        break
    return alloc
