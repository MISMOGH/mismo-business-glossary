import re, json, io

SRC = "../_source"
OUT = "../data"

# ---- glossary terms, from the console's embedded baseline -------------------
html = open(f"{SRC}/glossary-console.html", encoding="utf-8").read()
m = re.search(r'<script type="application/json" id="baselineData">(.*?)</script>', html, re.S)
d = json.loads(m.group(1))
cols = d["cols"]
idx = {c: i for i, c in enumerate(cols)}

# The public page consumes lowercase keys with aka/related as ID arrays.
# The console baseline has no AKA/Related columns, so they start empty.
terms = []
for r in d["rows"]:
    terms.append({
        "id":         r[idx["ID"]],
        "term":       r[idx["Term"]],
        "definition": r[idx["Definition"]],
        "source":     r[idx["Source"]],
        "termType":   r[idx["TermType"]],
        "focusArea":  r[idx["FocusArea"]],
        "aka":        [],
        "related":    [],
    })

terms.sort(key=lambda t: t["term"].strip().lower())

meta = {
    "version": d["version"],
    "source": d["source"],
    "count": len(terms),
    "note": "Generated from the console's embedded baseline. Do not hand-edit; "
            "re-export from the console instead.",
}

# One term per line: valid JSON, but each change is a readable one-line git diff
# rather than a change inside a single 2MB line.
with io.open(f"{OUT}/glossary.json", "w", encoding="utf-8", newline="\n") as f:
    f.write('{\n')
    f.write('"meta": ' + json.dumps(meta, ensure_ascii=False) + ',\n')
    f.write('"terms": [\n')
    for i, t in enumerate(terms):
        f.write(json.dumps(t, ensure_ascii=False))
        f.write(',\n' if i < len(terms) - 1 else '\n')
    f.write(']\n}\n')

# ---- reference descriptions, from the public page --------------------------
pub = open(f"{SRC}/glossary-public-v1.html", encoding="utf-8").read()
m = re.search(r'<script id="ref" type="application/json">(.*?)</script>', pub, re.S)
ref = json.loads(m.group(1))
with io.open(f"{OUT}/reference.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(ref, f, ensure_ascii=False, indent=2)
    f.write("\n")

print("terms:", len(terms))
print("focusAreas:", len(ref["focusAreas"]),
      "termTypes:", len(ref["termTypes"]),
      "sources:", len(ref["sources"]))
