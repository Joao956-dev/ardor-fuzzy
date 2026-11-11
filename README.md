# ARDOR: sistema fuzzy de risco composto de calor e fumaça (Marabá-PA)

Projeto 1 de Inteligência Artificial (Prof. Dr. Elton Alves, Unifesspa). Equipe: João Vitor Barros e Luiz Antônio Machado. Entrega: 11/11/2026.

| Pasta | Conteúdo |
|---|---|
| `codigo/ardor.py` | Motor fuzzy Mamdani hierárquico (FIS-1, FIS-2, FIS-3, 77 regras), feito do zero em NumPy |
| `codigo/resultados.py` | Roda 2024 inteiro, gera `dados/estatisticas.json`, `dados/diario_2024.json` e as figuras |
| `codigo/gerar_artigo.py` | Gera o artigo IEEE em `.docx` |
| `artigo/` | `ARDOR_artigo_IEEE.docx` (editável) e `.pdf` |
| `web/index.html` | Interface interativa; abra no navegador para ver a previsão ao vivo |
| `web/engine.js` | Mesmo motor em JavaScript (diferença 0 em relação ao Python em 300 casos) |
| `figuras/` | Figuras 1 a 6 do artigo (300 dpi) |
| `slides/roteiro_apresentacao.md` | Roteiro de fala e perguntas prováveis |
| `slides/notas_para_imprimir.md` | Notas do apresentador por slide (as mesmas que estão no Canva) |
| `codigo/figuras_slides.py` | Gera `figuras/f7` (IQAr × ARDOR diário) e `f8` (horas seguras por mês) para os slides 12 e 13 |

## Como rodar

```bash
pip install numpy matplotlib python-docx
python codigo/resultados.py
python codigo/gerar_artigo.py
python web/build.py
```

Dados: Open-Meteo (PM2.5 CAMS, temperatura e umidade ERA5), lat -5,37 lon -49,12, ano de 2024.

## Links

- Página interativa: https://ardor-maraba.vercel.app
- Artigo: `artigo/ARDOR_artigo_IEEE.pdf`
- Prévia dos slides: `slides/previa_canva/`
