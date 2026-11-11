// ARDOR - motor fuzzy Mamdani hierarquico (porta fiel de codigo/ardor.py)
const ARDOR = (() => {
  const trap = (x, a, b, c, d) => {
    if (x < a || x > d) return (a === b && x <= b) || (c === d && x >= c) ? 1 : 0;
    if (x >= b && x <= c) return 1;
    if (x < b) return a === b ? 1 : (x - a) / (b - a);
    return c === d ? 1 : (d - x) / (d - c);
  };
  const mk = (nome, lo, hi, termos, rot) => {
    const n = 501, u = Array.from({ length: n }, (_, i) => lo + (hi - lo) * i / (n - 1));
    const mf = (t, x) => { const [tp, p] = termos[t]; x = Math.min(hi, Math.max(lo, x));
      return tp === 'tri' ? trap(x, p[0], p[1], p[1], p[2]) : trap(x, ...p); };
    return { nome, lo, hi, termos, u, mf, rot: rot || {}, fuzz: x => Object.fromEntries(Object.keys(termos).map(t => [t, mf(t, x)])) };
  };
  const mamdani = (entradas, saida, regras) => ({
    entradas, saida, regras,
    inferir(vals) {
      const g = Object.fromEntries(entradas.map(v => [v.nome, v.fuzz(vals[v.nome])]));
      const agg = new Float64Array(saida.u.length); const ativ = [];
      for (const [ant, cons] of regras) {
        const f = Math.min(...Object.entries(ant).map(([v, t]) => g[v][t]));
        if (f > 0) { ativ.push({ f, ant, cons });
          for (let i = 0; i < agg.length; i++) agg[i] = Math.max(agg[i], Math.min(f, saida.mf(cons, saida.u[i]))); }
      }
      let s = 0, sw = 0; for (let i = 0; i < agg.length; i++) { s += agg[i]; sw += agg[i] * saida.u[i]; }
      return { y: s ? sw / s : (saida.lo + saida.hi) / 2, graus: g, ativ: ativ.sort((a, b) => b.f - a.f), agg };
    }
  });

  const T = mk('T', 15, 45, { amena: ['trap', [15, 15, 25, 29]], quente: ['tri', [26, 30.5, 34]], muito_quente: ['tri', [32, 35.5, 39]], extrema: ['trap', [37, 40, 45, 45]] });
  const UR = mk('UR', 10, 100, { seca: ['trap', [10, 10, 30, 45]], moderada: ['tri', [35, 55, 75]], umida: ['trap', [65, 80, 100, 100]] });
  const CAL = { baixo: ['trap', [0, 0, 1.5, 3.5]], moderado: ['tri', [2, 4, 6]], alto: ['tri', [4.5, 6.5, 8.5]], extremo: ['trap', [7, 9, 10, 10]] };
  const CALOR = mk('calor', 0, 10, CAL);
  const m1 = { amena: ['baixo', 'baixo', 'baixo'], quente: ['baixo', 'moderado', 'alto'], muito_quente: ['moderado', 'alto', 'extremo'], extrema: ['alto', 'extremo', 'extremo'] };
  const R1 = []; for (const t in m1) ['seca', 'moderada', 'umida'].forEach((u, j) => R1.push([{ T: t, UR: u }, m1[t][j]]));
  const FIS1 = mamdani([T, UR], CALOR, R1);

  const PM = mk('PM25', 0, 200, { boa: ['trap', [0, 0, 10, 20]], moderada: ['trap', [10, 20, 40, 58]], ruim: ['tri', [42, 62, 82]], muito_ruim: ['tri', [68, 100, 132]], pessima: ['trap', [112, 138, 200, 200]] });
  const CG = { baixa: ['trap', [0, 0, 10, 25]], moderada: ['tri', [15, 32, 50]], alta: ['tri', [40, 55, 70]], muito_alta: ['tri', [60, 75, 90]], critica: ['trap', [80, 92, 100, 100]] };
  const CARGA = mk('carga', 0, 100, CG);
  const m2 = { boa: ['baixa', 'baixa', 'moderada', 'alta'], moderada: ['moderada', 'moderada', 'alta', 'muito_alta'], ruim: ['alta', 'alta', 'muito_alta', 'critica'], muito_ruim: ['muito_alta', 'muito_alta', 'critica', 'critica'], pessima: ['critica', 'critica', 'critica', 'critica'] };
  const R2 = []; for (const p in m2) ['baixo', 'moderado', 'alto', 'extremo'].forEach((c, j) => R2.push([{ PM25: p, calor: c }, m2[p][j]]));
  const FIS2 = mamdani([PM, mk('calor', 0, 10, CAL)], CARGA, R2);

  const VULN = mk('vuln', 0, 10, { baixa: ['trap', [0, 0, 2, 4]], media: ['tri', [2.5, 5, 7.5]], alta: ['trap', [6, 8, 10, 10]] });
  const ESF = mk('esforco', 0, 10, { leve: ['trap', [0, 0, 2, 4]], moderado: ['tri', [2.5, 5, 7.5]], intenso: ['trap', [6, 8, 10, 10]] });
  const RISCO = mk('risco', 0, 100, { baixo: ['trap', [0, 0, 12, 28]], moderado: ['tri', [18, 35, 52]], alto: ['tri', [42, 57, 72]], muito_alto: ['tri', [62, 76, 90]], critico: ['trap', [82, 92, 100, 100]] });
  const NIV = ['baixo', 'moderado', 'alto', 'muito_alto', 'critico'], cargas = ['baixa', 'moderada', 'alta', 'muito_alta', 'critica'];
  const dv = { baixa: 0, media: 1, alta: 1 }, de = { leve: -1, moderado: 0, intenso: 1 }, R3 = [];
  cargas.forEach((cg, i) => { for (const v in dv) for (const e in de) {
    let k = i + dv[v] + de[e]; if (v === 'alta' && i >= 2) k += 1; if (i === 0) k = Math.min(k, 1); if (i === 4) k = Math.max(k, 3);
    R3.push([{ carga: cg, vuln: v, esforco: e }, NIV[Math.max(0, Math.min(4, k))]]); } });
  const FIS3 = mamdani([mk('carga', 0, 100, CG), VULN, ESF], RISCO, R3);

  const REC = [[25, 'Liberado', 'Atividade normal. Mantenha a hidratação.'],
    [45, 'Atenção', 'Liberado com pausas a cada 20 min, água e sombra.'],
    [65, 'Reduzir', 'Diminua duração e intensidade; prefira o início da manhã.'],
    [82, 'Evitar', 'Evite atividade ao ar livre; leve para um ambiente fechado.'],
    [101, 'Suspender', 'Suspenda a atividade; fique em local fechado e use máscara PFF2 se precisar sair.']];
  const nivel = r => r < 25 ? 0 : r < 45 ? 1 : r < 65 ? 2 : r < 82 ? 3 : 4;
  const avaliar = (t, ur, pm, vu, es) => {
    const s1 = FIS1.inferir({ T: t, UR: ur }), s2 = FIS2.inferir({ PM25: pm, calor: s1.y }), s3 = FIS3.inferir({ carga: s2.y, vuln: vu, esforco: es });
    const n = nivel(s3.y);
    return { calor: s1.y, carga: s2.y, risco: s3.y, nivel: n, rot: REC[n][1], txt: REC[n][2], s1, s2, s3 };
  };
  return { avaliar, nivel, FIS1, FIS2, FIS3, vars: { T, UR, PM, CALOR, CARGA, VULN, ESF, RISCO }, R1, R2, R3 };
})();
if (typeof module !== 'undefined') module.exports = ARDOR;
