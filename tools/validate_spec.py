#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка целостности спецификации шаблона на всех языках.

Запуск: python3 tools/validate_spec.py
Ничего не печатает, кроме итога и найденных проблем; код возврата 1 при ошибках.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "docs", "spec")

problems = []


def fail(where, msg):
    problems.append("%s: %s" % (where, msg))


schema = json.load(open(os.path.join(SPEC, "schema.json"), encoding="utf-8"))
version = json.load(open(os.path.join(ROOT, "version.json"), encoding="utf-8"))
migrations = json.load(open(os.path.join(SPEC, "migrations.json"), encoding="utf-8"))
LANGS = schema["languages"]
by_key = {db["key"]: db for db in schema["databases"]}

col_re = re.compile(r'"([^"]+)"\s+(.+?)(?=,\s*"|\s*\)\s*$)', re.S)
com_re = re.compile(r"\s*COMMENT\s+'(.*?)'\s*$", re.S)
add_re = re.compile(r'ADD COLUMN "([^"]+)" (RELATION|ROLLUP|FORMULA)\((.*)\)\s*$', re.S)


def columns(db, lang):
    """{имя поля: тип} из DDL."""
    ddl = db["ddl"][lang]
    body = ddl[ddl.index("(") + 1:]
    out = {}
    for name, rest in col_re.findall(body):
        out[name] = com_re.sub("", rest).strip()
    return out


def title_field(db, lang):
    for name, typ in columns(db, lang).items():
        if typ == "TITLE":
            return name
    return None


# 1. Кавычки в DDL: ASCII-апостроф внутри одинарных кавычек ломает разбор.
for db in schema["databases"]:
    for lang in LANGS:
        for text, where in [(db["ddl"][lang], "ddl %s/%s" % (db["key"], lang))]:
            if text.count("'") % 2:
                fail(where, "нечётное число одинарных кавычек")
            for m in re.finditer(r"'([^']*)'", text):
                if "'" in m.group(1):
                    fail(where, "апостроф внутри одинарных кавычек: %r" % m.group(1))
        if not title_field(db, lang):
            fail("ddl %s/%s" % (db["key"], lang), "нет поля TITLE")

# 2. Одинаковый набор полей во всех языках.
for db in schema["databases"]:
    counts = {lang: len(columns(db, lang)) for lang in LANGS}
    if len(set(counts.values())) != 1:
        fail("ddl " + db["key"], "разное число полей по языкам: %s" % counts)

# 3. Связи: цели существуют, набор statement одинаков по языкам.
rel_fields = {(k, lang): set() for k in by_key for lang in LANGS}
for rel in schema["relations"]:
    on = rel["on"]
    if on not in by_key:
        fail("relations", "неизвестная база %r" % on)
        continue
    lens = {lang: len(rel["statements"][lang]) for lang in LANGS}
    if len(set(lens.values())) != 1:
        fail("relations " + on, "разное число statement по языкам: %s" % lens)
    for lang in LANGS:
        for s in rel["statements"][lang]:
            m = add_re.search(s)
            if not m:
                fail("relations %s/%s" % (on, lang), "не разобран: %s" % s)
                continue
            name, args = m.group(1), m.group(3)
            rel_fields[(on, lang)].add(name)
            tgt = re.search(r"\[ID:([a-z]+)\]", args)
            if not tgt or tgt.group(1) not in by_key:
                fail("relations %s/%s" % (on, lang), "неизвестная цель в %s" % s)
                continue
            dual = re.search(r"DUAL\s+'([^']+)'", args)
            if dual:
                rel_fields[(tgt.group(1), lang)].add(dual.group(1))

# 4. Формулы и роллапы ссылаются на существующие поля.
for comp in schema["computed"]:
    on = comp["on"]
    for lang in LANGS:
        cols = columns(by_key[on], lang)
        for s in comp["statements"][lang]:
            m = add_re.search(s)
            if not m:
                fail("computed %s/%s" % (on, lang), "не разобран: %s" % s)
                continue
            name, kind, args = m.group(1), m.group(2), m.group(3)
            if kind == "FORMULA":
                for prop in re.findall(r'prop\("([^"]+)"\)', args):
                    if prop not in cols:
                        fail("computed %s/%s" % (on, lang),
                             "формула %r ссылается на несуществующее поле %r" % (name, prop))
            else:
                a = re.findall(r"'([^']*)'", args)
                if len(a) != 3:
                    fail("computed %s/%s" % (on, lang), "роллап %r: ожидалось три аргумента" % name)
                    continue
                rel_prop, target_prop, _func = a
                if rel_prop not in rel_fields[(on, lang)] and rel_prop not in cols:
                    fail("computed %s/%s" % (on, lang),
                         "роллап %r идёт по несуществующей связи %r" % (name, rel_prop))
                    continue
                if not any(target_prop in columns(by_key[k], lang) for k in by_key):
                    fail("computed %s/%s" % (on, lang),
                         "роллап %r тянет несуществующее поле %r" % (name, target_prop))

# 5. Стартовые полномочия: значения из реальных списков базы полномочий.
powers_cols_raw = {lang: columns(by_key["powers"], lang) for lang in LANGS}
colmap = schema["seed"]["permissions_columns"]
for i, row in enumerate(schema["seed"]["permissions"]):
    for lang in LANGS:
        for key, value in row[lang].items():
            if key not in colmap:
                fail("seed[%d]/%s" % (i, lang), "нет отображения для колонки %r" % key)
                continue
            colname = colmap[key][lang]
            spec = powers_cols_raw[lang].get(colname)
            if spec is None:
                fail("seed[%d]/%s" % (i, lang), "в базе полномочий нет колонки %r" % colname)
                continue
            if spec.startswith("SELECT("):
                opts = re.findall(r"'([^']+)'", spec)
                if value not in opts:
                    fail("seed[%d]/%s" % (i, lang),
                         "значение %r не входит в список колонки %r" % (value, colname))

# 6. Конституции: плейсхолдеры и поля-заголовки в таблице маршрутизации.
ph_re = re.compile(r"\[ID:([a-z:]+)\]")
sets = {}
for lang in LANGS:
    path = os.path.join(SPEC, "constitution.%s.txt" % lang)
    if not os.path.exists(path):
        fail("constitution/" + lang, "файла нет")
        continue
    text = open(path, encoding="utf-8").read()
    sets[lang] = set(ph_re.findall(text))
    for key in sets[lang]:
        if key.startswith("page:"):
            if key[5:] not in {p["key"] for p in schema["pages"]}:
                fail("constitution/" + lang, "плейсхолдер на несуществующую страницу %r" % key)
        elif key not in by_key:
            fail("constitution/" + lang, "плейсхолдер на несуществующую базу %r" % key)
    for line in text.splitlines():
        if not line.startswith("|") or "[ID:" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = ph_re.search(line)
        key = m.group(1)
        if key.startswith("page:") or len(cells) < 4:
            continue
        declared = cells[-1].strip("` ")
        if declared in ("—", "-", ""):
            continue
        actual = title_field(by_key[key], lang)
        if declared != actual:
            fail("constitution/" + lang,
                 "в маршрутизации у %s поле-заголовок %r, в схеме %r" % (key, declared, actual))
if len(set(map(frozenset, sets.values()))) > 1:
    fail("constitution", "наборы плейсхолдеров различаются по языкам")

# 7. Версии согласованы.
if schema["template_version"] != version["version"]:
    fail("version", "schema.json %s против version.json %s"
         % (schema["template_version"], version["version"]))
if set(version["languages"]) != set(LANGS):
    fail("version", "список языков расходится со schema.json")
for lang in LANGS:
    rel = version["spec"]["constitution"][lang]
    if not os.path.exists(os.path.join(ROOT, "docs", rel)):
        fail("version", "нет файла %s" % rel)
chain = [(m["from"], m["to"]) for m in migrations["migrations"]]
for m in migrations["migrations"]:
    for block in ("schema", "constitution", "pages"):
        if set(m[block]) != set(LANGS):
            fail("migrations %s→%s" % (m["from"], m["to"]),
                 "в блоке %s нет ветки на каждый язык" % block)
if chain and chain[-1][1] != version["version"]:
    fail("migrations", "цепочка кончается на %s, а версия %s" % (chain[-1][1], version["version"]))

# 8. Последняя миграция должна совпадать с тем, что реально лежит в конституциях.
for mig in migrations["migrations"]:
    if mig["to"] != version["version"]:
        continue
    for lang in LANGS:
        path = os.path.join(SPEC, "constitution.%s.txt" % lang)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        for item in mig["constitution"][lang]:
            # Правка может быть дописыванием, и тогда old — часть new;
            # значимая проверка одна: результат уже лежит в файле.
            if item["new"] not in text:
                fail("migrations %s→%s/%s" % (mig["from"], mig["to"], lang),
                     "результат правки %s не найден в конституции — файл и миграция разошлись"
                     % item.get("section", "?"))

print("баз: %d · языков: %d · связей: %d · вычисляемых полей: %d · строк полномочий: %d"
      % (len(schema["databases"]), len(LANGS),
         sum(len(r["statements"][LANGS[0]]) for r in schema["relations"]),
         sum(len(c["statements"][LANGS[0]]) for c in schema["computed"]),
         len(schema["seed"]["permissions"])))
if problems:
    print("\nПРОБЛЕМЫ (%d):" % len(problems))
    for p in problems:
        print(" ·", p)
    sys.exit(1)
print("проблем нет")
