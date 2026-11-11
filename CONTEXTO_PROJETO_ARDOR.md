# Contexto do Projeto ARDOR (para continuar em outro chat)

> Documento de transferência de contexto. Resume tudo o que foi decidido, construído e verificado até 08/11/2026.

## 1. A tarefa

- **Disciplina:** Inteligência Artificial, Prof. Dr. Elton Alves, Faculdade de Engenharia da Computação, Universidade Federal do Sul e Sudeste do Pará (Unifesspa), Marabá-PA.
- **Equipe:** João Vitor Barros e Luiz Antônio Machado.
- **Objetivo do enunciado:** desenvolver uma aplicação de sistema fuzzy para resolver um problema real.
- **Entrega e apresentação:** 11/11/2026. Vale 4 pontos.
- **O professor usa Turnitin** para checar plágio e também texto gerado por IA.
- **Critérios de avaliação:**
  - Relevância e inovação do problema: 0,5
  - Fundamentação teórica e metodologia: 0,5
  - Modelagem e implementação do sistema fuzzy: 1,0
  - Resultados, análise e discussão: 0,75
  - Escrita científica e artigo IEEE: 0,5
  - Interface gráfica interativa: 0,25
  - Apresentação e domínio: 0,5
- **Obrigatório:** o artigo precisa ter uma declaração de uso de IA generativa (quais ferramentas, para quê e em quais etapas).
- **Pedidos do usuário:**
  - Slides no Canva via MCP, intuitivos e sem excesso de texto.
  - Página web com interface interativa.
  - Pesquisa de artigos correlatos para achar um problema original e relevante.

## 2. Como chegamos ao tema

- **Primeira ideia: enchentes em Marabá.** Descartada como foco principal porque já existe um artigo fuzzy sobre vulnerabilidade a inundação em Marabá (Bezerra, Pessoa e Ferreira Filho, Rev. Geoaraguaia, 2023).
- **Lacuna encontrada:**
  - Já existem índices fuzzy de qualidade do ar, mas eles combinam só poluentes (Hájek e Olej, 2009).
  - A epidemiologia mostra que calor e fumaça juntos fazem mais mal do que a soma dos dois. Em 482 cidades, a poluição aumentou o efeito do calor sobre a mortalidade (Rai et al., 2023). Na Califórnia, cerca de 8% das internações respiratórias foram atribuídas à interação (Jones-Ngo et al., 2025).
  - Não encontramos nenhum sistema fuzzy que una calor e fumaça num risco à saúde personalizado.
- **Relevância local:**
  - Em agosto de 2024, a Defesa Civil de Marabá emitiu alerta de qualidade do ar.
  - O Pará liderou os focos de incêndio do país.
  - A apresentação cai em novembro, que foi o pior mês de fumaça em 2024.

## 3. O sistema: ARDOR

**Nome:** ARDOR, de **A**valiação de **R**isco **D**ifuso para **O**ndas de calor e fuma**ç**a.

**Pergunta que o sistema responde:** "Esta pessoa pode fazer esta atividade ao ar livre agora em Marabá?"

### Arquitetura

O sistema é um Mamdani hierárquico com 3 estágios e 77 regras. Uma base única com as mesmas entradas exigiria 540 regras.

| Estágio | Entradas | Saída | Regras |
|---|---|---|---|
| FIS-1 | Temperatura (15–45 °C), Umidade relativa (10–100 %) | Estresse térmico (0–10) | 12 |
| FIS-2 | PM2.5 média 24 h (0–200 µg/m³), Estresse térmico | Carga ambiental (0–100) | 20 |
| FIS-3 | Carga, Vulnerabilidade (0–10), Esforço (0–10) | Risco pessoal (0–100) | 45 |

**Operadores:** E = mínimo, implicação = mínimo, agregação = máximo, defuzzificação por centroide. Os universos são discretizados em 501 pontos.

### Termos linguísticos

- **Temperatura:** amena (15,15,25,29), quente (26,30.5,34), muito quente (32,35.5,39), extrema (37,40,45,45).
- **Umidade:** seca (10,10,30,45), moderada (35,55,75), úmida (65,80,100,100).
- **PM2.5:** boa (0,0,10,20), moderada (10,20,40,58), ruim (42,62,82), muito ruim (68,100,132), péssima (112,138,200,200). Os conjuntos cruzam o grau 0,5 nos limites oficiais do IQAr: 15 / 50 / 75 / 125 µg/m³.
  - **Fonte das faixas:** documento "Orientação técnica IQAr", MMA, jan/2025, e Resolução CONAMA 506/2024. Para MP2,5 em 24 h: Boa 0–15, Moderada >15–50, Ruim >50–75, Muito ruim >75–125, Péssima >125.
- **Estresse térmico:** baixo, moderado, alto, extremo.
- **Carga e risco:** baixa/baixo, moderada/moderado, alta/alto, muito alta/muito alto, crítica/crítico.
- **Vulnerabilidade:**
  - baixa (0,0,2,4): adulto saudável
  - média (2.5,5,7.5): criança, idoso
  - alta (6,8,10,10): asma, cardiopatia
- **Esforço:**
  - leve (0,0,2,4): caminhar
  - moderado (2.5,5,7.5): educação física
  - intenso (6,8,10,10): obra, roça, futebol

### Regras

- **FIS-1:** a umidade alta agrava o calor. Tabela T × UR:
  - amena: baixo, baixo, baixo
  - quente: baixo, moderado, alto
  - muito quente: moderado, alto, extremo
  - extrema: alto, extremo, extremo

- **FIS-2:** é o núcleo da inovação. A sinergia entre fumaça e calor aparece na diagonal da matriz.

| PM2.5 \ calor | baixo | moderado | alto | extremo |
|---|---|---|---|---|
| boa | baixa | baixa | moderada | alta |
| moderada | moderada | moderada | **alta** | muito alta |
| ruim | alta | alta | muito alta | crítica |
| muito ruim | muito alta | muito alta | crítica | crítica |
| péssima | crítica | crítica | crítica | crítica |

- **FIS-3:** gerado por uma regra de deslocamento de níveis:
  - Parte do nível da carga.
  - Vulnerabilidade média ou alta: +1. Esforço leve: −1. Esforço intenso: +1.
  - Vulnerabilidade alta com carga alta ou maior: +1 extra.
  - **Restrições de segurança:** com carga baixa, o risco fica no máximo moderado. Com carga crítica, o risco é no mínimo muito alto.

### Conduta

| Risco | Rótulo no artigo | Frase na página web |
|---|---|---|
| < 25 | Liberado | Pode [atividade] normalmente |
| 25–45 | Atenção | Pode [atividade], com pausas (a cada 20 min, água, sombra) |
| 45–65 | Reduzir | Faça mais curto e mais leve; prefira o começo da manhã |
| 65–82 | Evitar | Melhor não [atividade] ao ar livre; leve para local fechado |
| ≥ 82 | Suspender | Não [atividade] ao ar livre agora; local fechado, máscara PFF2 se sair |

## 4. Dados e resultados (fonte: `dados/estatisticas.json`)

**Dados usados:** API Open-Meteo para Marabá (lat −5,37, lon −49,12), ano de 2024. O PM2.5 vem do CAMS (Copernicus) e a temperatura e a umidade do ERA5. São 8.784 horas válidas.
- **Análise diária:** média de 24 h do PM2.5 e a hora de maior índice de calor entre 10 h e 16 h.

### Resultados de 2024

- **85 dias** com PM2.5 acima de 15 µg/m³ (limite da OMS); **84** deles também com índice de calor ≥ 32 °C (cautela).
- **352 dias** com índice de calor ≥ 32 °C.
- **PM2.5 médio por mês (µg/m³):**

| jan | fev | mar | abr | mai | jun | jul | ago | set | out | nov | dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 8,4 | 8,1 | 5,7 | 6,4 | 7,3 | 5,6 | 5,9 | 9,8 | 15,5 | 21,2 | 31,8 | 17,8 |

- **Sinergia: 40 dias.** Nesses dias, o nível da carga combinada foi maior que o maior nível obtido zerando um fator por vez.
- **83 dias** com carga acima do nível do IQAr. **30 dias** com IQAr "boa" ou "moderada" e carga ARDOR alta.
- **Validação do FIS-1** contra o índice de calor da NOAA: Pearson r = 0,907; Spearman = 0,899 (2.928 horas).
- **Dias por nível** (baixo, moderado, alto, muito alto, crítico):
  - IQAr: 281, 85, 0, 0, 0
  - Carga ARDOR: 230, 106, 30, 0, 0
  - Adulto caminhando (vuln 1, esf 2): 336, 30, 0, 0, 0
  - Criança em educação física (5; 6): 0, 197, 137, 32, 0
  - Sensível em atividade moderada (8,5; 5): 0, 197, 133, 16, 20
- **Pior dia: 24/11/2024.** PM2.5 de 46,2 (IQAr moderada), 33,7 °C, 50 %, índice de calor 37,7 °C, carga 60,7 (alta). Riscos: criança 76,7 ("evitar"), sensível 92,5 ("suspender"), adulto 36,5 ("atenção").
- **Janela segura** para criança em educação física: média de horas por dia, entre 7 h e 17 h, com risco < 45. O PM2.5 usado é a média móvel de 24 h.

| jan | fev | mar | abr | mai | jun | jul | ago | set | out | nov | dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 8,9 | 7,9 | 7,6 | 7,1 | 8,9 | 10,4 | 10,9 | 9,0 | 3,3 | 0,6 | **0,0** | 3,7 |

- **Sensibilidade** (perfil infantil, % de dias com a mesma conduta; o salto máximo foi sempre de 1 nível):

| Perturbação | Dias com a mesma conduta |
|---|---|
| PM2.5 −20 % | 92,9 % |
| PM2.5 +20 % | 89,9 % |
| T −1 °C | 85,8 % |
| T +1 °C | 76,8 % |

### Tabela "lógica clássica × fuzzy" (graus de pertinência da temperatura)

| Temperatura | Clássica (quente se ≥ 35 °C) | Fuzzy |
|---|---|---|
| 27 °C | 0 | amena 0,50; quente 0,22 |
| 31 °C | 0 | quente 0,86 |
| 33 °C | 0 | quente 0,29; muito quente 0,29 |
| 35 °C | 1 | muito quente 0,86 |
| 37 °C | 1 | muito quente 0,57 |

### Tabela "onde está a inovação" (criança em educação física)

| PM2.5 | Tempo | IQAr diz | Índice de calor diz | ARDOR carga | ARDOR criança |
|---|---|---|---|---|---|
| 10 | 27 °C, 65 % | boa | cautela (28,5) | baixa (10) | com pausas (35) |
| 10 | 34 °C, 60 % | boa | perigo (42,2) | moderada (32) | mais curto e leve (57) |
| 35 | 27 °C, 65 % | moderada | cautela | moderada (32) | mais curto e leve (57) |
| **35** | **34 °C, 60 %** | **moderada** | **perigo** | **alta (55)** | **melhor em local fechado (76)** |
| 60 | 27 °C, 65 % | ruim | cautela | alta (55) | melhor em local fechado (76) |
| **60** | **34 °C, 60 %** | **ruim** | **perigo** | **muito alta (75)** | **não fazer ao ar livre (93)** |

## 5. Entregáveis e onde estão

**Pasta do projeto:** `D:\Canal Biblico\Projeto_Fuzzy_ARDOR\`

| Item | Caminho / link | Status |
|---|---|---|
| Motor fuzzy (Python, do zero em NumPy) | `codigo/ardor.py` | Pronto |
| Análise de 2024 + figuras | `codigo/resultados.py` gera `dados/estatisticas.json`, `dados/diario_2024.json`, `figuras/f1..f6` | Pronto |
| Artigo IEEE (PT-BR, 2 colunas, 4 páginas, 6 figuras, 4 tabelas, 18 referências, declaração de IA) | `artigo/ARDOR_artigo_IEEE.docx` e `.pdf` (gerados por `codigo/gerar_artigo.py`; PDF via LibreOffice) | Pronto; ainda não tem as tabelas "clássica × fuzzy" e "inovação" |
| Página web | Local: `web/index.html` (busca previsão ao vivo). Compartilhável: https://claude.ai/artifact/AKSKEaqgsK9G8m2GAXFzD1 (privada; compartilhar pelo menu Share; usa previsão capturada em 08/11 19h) | Pronta (versão 2) |
| Motor em JS | `web/engine.js` (diferença 0 em relação ao Python em 300 casos) | Pronto |
| Build da página | `web/template.html` → `python web/build.py` → `index.html` e `ardor_artifact.html` | – |
| Slides (Canva, 16 slides) | https://canva.link/iz3xiugy1r8a6jv (design `DAHaXrYT3vs`) | Conteúdo conferido; visual das tabelas não conferido |
| Roteiro de fala + perguntas prováveis | `slides/roteiro_apresentacao.md` | Pronto (16 slides) |
| Leia-me | `LEIAME.md` | Pronto |

- **Ambiente Python:** `C:\mcp\temp\fuzzy\.venv` (numpy, matplotlib, python-docx, pypdf, pypdfium2).
- **Decks antigos no Canva** (podem ser apagados): o primeiro, de 12 slides, com analogias (`DAHaXo_FLPs`), e uma tentativa de 16 slides que perdeu os números (`DAHaXvzKA5s`).

### Página web (versão atual)

1. **Fluxo guiado em 5 passos:**
   - Quem vai sair e qual atividade.
   - Quanto calor o corpo sente (temperatura, umidade, sensação térmica e estresse térmico).
   - Quanta fumaça há no ar (PM2.5, nível do IQAr, quantas vezes acima do limite da OMS).
   - Calor e fumaça juntos (carga, com aviso quando há sinergia).
   - Resposta como pergunta e conduta, com o risco "de passar mal durante a atividade" de 0 a 100 numa régua colorida.
2. **Próximas 48 h:** barras coloridas por hora, legenda com a conduta de cada cor e o melhor horário.
3. **Simulador:** controles deslizantes, valores dos 3 estágios, quadro "IQAr diria × ARDOR diz", funções de pertinência com a área agregada e as regras que mais pesaram.
4. **Resultados de 2024:** cartões com os números principais, gráfico diário e horas seguras por mês.
5. **Como funciona:** as 4 etapas de Mamdani, a tabela "onde está a inovação" e a lista de fontes.

### Slides (ordem atual)

1. Capa
2. Contexto
3. O problema
4. Trabalhos correlatos e lacuna (tabela)
5. Objetivo
6. O que é um sistema fuzzy (tabela clássica × fuzzy)
7. Inferência de Mamdani
8. Arquitetura
9. Variáveis e faixas (tabela)
10. Onde está a inovação (tabela)
11. Dados e metodologia
12. Resultados 1 (40 dias / 30 dias / r = 0,91 / pior dia)
13. Resultados 2 (janela segura e robustez)
14. Demonstração
15. Limitações, trabalhos futuros e uso de IA
16. Referências

## 6. Decisões e preferências do usuário

- **Sem analogias**, nem nos slides nem na página. O usuário achou "duas sacolas" e "termostato × mãe" bobas. A explicação deve ser técnica e tradicional.
- **Os slides precisam de:** contexto do problema, fontes de conhecimento citadas (rodapé + slide de referências), conceitos formais de fuzzy e uma "tabela da verdade" que mostre a inovação.
- **A página deve levar o público a uma conclusão intuitiva**, em fluxo. Todo número precisa dizer **o que** mede, e toda conduta precisa dizer **o que** fazer.
- **Divisão sugerida da fala:** João apresenta os slides 1–8 e a demonstração; Luiz, os slides 9–13, 15 e 16.

## 7. Referências usadas (todas verificadas)

1. Debate Carajás, "Defesa Civil alerta para qualidade do ar em Marabá após queimadas", ago. 2024.
2. InfoAmazonia, poluição por fumaça no Pará, mar. 2025.
3. MMA, Orientação técnica: Índice de Qualidade do Ar (IQAr), jan. 2025.
4. L. P. Rothfusz, "The heat index equation", NWS SR 90-23, 1990.
5. M. Rai et al., Environ. Int., v. 174, 107825, 2023. doi:10.1016/j.envint.2023.107825.
6. C. G. Jones-Ngo et al., GeoHealth, v. 9, n. 6, e2024GH001237, 2025. doi:10.1029/2024GH001237.
7. L. A. Zadeh, "Fuzzy sets", Inf. Control, v. 8, n. 3, pp. 338–353, 1965.
8. P. Hájek e V. Olej, "Air pollution assessment using hierarchical fuzzy inference systems", Sci. Papers Univ. Pardubice Ser. D, v. 15, pp. 52–61, 2009.
9. P. E. Bezerra, F. Pessoa e D. Ferreira Filho, Rev. Geoaraguaia, v. 13, n. 2, pp. 1–21, 2023.
10. "Advancing the community health vulnerability index for wildland fire smoke exposure", 2025 (PMC12087597).
11. E. H. Mamdani e S. Assilian, Int. J. Man-Mach. Stud., v. 7, n. 1, pp. 1–13, 1975.
12. G. V. S. Raju, J. Zhou e R. A. Kisner, "Hierarchical fuzzy control", Int. J. Control, v. 54, n. 5, pp. 1201–1216, 1991.
13. Open-Meteo, API de clima e qualidade do ar.
14. A. Inness et al., "The CAMS reanalysis...", Atmos. Chem. Phys., v. 19, pp. 3515–3556, 2019.
15. H. Hersbach et al., "The ERA5 global reanalysis", Q. J. R. Meteorol. Soc., v. 146, pp. 1999–2049, 2020.
16. OMS, WHO Global Air Quality Guidelines, 2021.
17. O Liberal, "Sensores de baixo custo ajudam no monitoramento da qualidade do ar no Pará", s.d.
18. CONAMA, Resolução nº 506, de 5 de julho de 2024.

## 8. Limitações (declaradas no artigo)

- O PM2.5 vem do modelo CAMS, com resolução de ~40 km. Ele suaviza picos locais e provavelmente subestima a exposição real.
- As regras não foram calibradas com dados de saúde locais.
- **Trabalhos futuros:**
  - Sensores de baixo custo do IPAM/UFPA já instalados em Marabá.
  - Dados de internações do DATASUS, com ajuste por ANFIS.
  - Vento e radiação no estresse térmico.

## 9. Declaração de uso de IA (texto que está no artigo)

> Os autores declaram que utilizaram ferramentas de Inteligência Artificial Generativa neste projeto. Foi usado o assistente Claude (modelo Claude Opus 5.5, Anthropic), por meio do aplicativo Claude Code, nas seguintes etapas: (i) definição do problema, com pesquisa e triagem de artigos correlatos e verificação de referências; (ii) modelagem, com sugestões para a arquitetura hierárquica, os termos linguísticos e a base de regras; (iii) implementação, com geração do código Python do motor de inferência, dos scripts de análise e da interface web em HTML/JavaScript; (iv) análise dos resultados e geração das figuras; e (v) redação preliminar deste artigo e do roteiro da apresentação. Todo o conteúdo gerado foi revisado, executado e validado pelos autores, que conferiram as referências, os números e as decisões de modelagem e assumem integral responsabilidade pelo trabalho. Nenhum dado pessoal foi fornecido à ferramenta.

## 10. Pendências e recomendações

1. **Turnitin detecta texto de IA.** A equipe deve reescrever com as próprias palavras pelo menos a introdução, a discussão e a conclusão do artigo.
2. **Conferir no Canva o visual** dos slides de tabela (4, 6, 9, 10 e 13) e apagar os decks antigos.
3. **Opcional:** levar para o artigo as tabelas "lógica clássica × fuzzy" e "onde está a inovação" que estão nos slides e na página.
4. **Compartilhar** o link da página com o Luiz e o professor pelo menu Share.
5. **Na apresentação,** usar `web/index.html` aberto no navegador para mostrar dados ao vivo.
6. Ensaiar as perguntas prováveis do roteiro: por que Mamdani, por que centroide, como validaram e como definiram sinergia.
