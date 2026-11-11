import json, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = open(os.path.join(B, 'web', 'template.html'), encoding='utf8').read()
eng = open(os.path.join(B, 'web', 'engine.js'), encoding='utf8').read()
D = json.load(open(os.path.join(B, 'dados', 'diario_2024.json'), encoding='utf8'))
st = json.load(open(os.path.join(B, 'dados', 'estatisticas.json'), encoding='utf8'))
# pior_dia fica disponível para o botão do simulador
snap = {'quando': '08/11/2026, 22h', 'aq': json.load(open(os.path.join(B, 'dados', 'prev_aq.json'))),
        'wx': json.load(open(os.path.join(B, 'dados', 'prev_wx.json')))}
dia = [[d['data'], d['pm'], d['ic'], d['carga'], d['n_iqar'], d['r_crianca']] for d in D]
t = (t.replace('/*ENGINE*/', eng).replace('/*DIARIO*/', json.dumps(dia, separators=(',', ':')))
      .replace('/*STATS*/', json.dumps(st, ensure_ascii=False)).replace('/*SNAP*/', json.dumps(snap, separators=(',', ':'), ensure_ascii=False)))
open(os.path.join(B, 'web', 'ardor_artifact.html'), 'w', encoding='utf8').write(t)
full = ('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n') + t.replace('</style>', '</style></head><body>', 1) + '</body></html>'
open(os.path.join(B, 'web', 'index.html'), 'w', encoding='utf8').write(full)
print('ok', len(t))
