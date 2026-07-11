"""
Loader for nigs.json — Orthodox Tewahedo monthly commemorations ("Nigs" days),
grouped by day-of-month ("1"-"30"), each entry:
    {id, name: {amharic, english}, description: {amharic, english}, major: bool, negs: [int]}
where `negs` lists the Ethiopian months in which that day is a major feast.

Ported from kenat/src/nigs.json (consumed there by MonthGrid.ts in 'christian' mode).
Loaded lazily and cached via importlib.resources, which works both from a source
checkout and from an installed wheel.
"""
import json
import importlib.resources as resources

_cache = None


def get_orthodox_days_by_day():
    """
    Returns the parsed nigs.json content: a dict mapping day-of-month strings
    ("1".."30") to a list of commemoration entries.
    """
    global _cache
    if _cache is None:
        data = resources.files('kenat').joinpath('nigs.json').read_text(encoding='utf-8')
        _cache = json.loads(data)
    return _cache
