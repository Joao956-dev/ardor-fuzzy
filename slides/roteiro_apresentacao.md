# ARDOR: roteiro de fala (cerca de 12 min)

**Divisão sugerida:** João apresenta os slides 1 a 8 e a demonstração (14). Luiz apresenta os slides 9 a 13, 15 e 16.

| # | Slide | O que falar | Tempo |
|---|---|---|---|
| 1 | Capa | Apresentar a equipe e o objetivo em uma frase: estimar o risco à saúde de uma atividade ao ar livre considerando calor e fumaça juntos. | 0:20 |
| 2 | Contexto | Entre agosto e dezembro, Marabá tem seca e queimadas ao mesmo tempo. Em 2024: 85 dias acima do limite da OMS, 84 deles também quentes. Citar o alerta da Defesa Civil. | 0:50 |
| 3 | O problema | O IQAr mede só poluentes e o índice de calor mede só calor. Rai et al. (2023): a poluição aumenta o efeito do calor sobre a mortalidade. Jones-Ngo et al. (2025): ~8% das internações respiratórias vieram da interação. Os efeitos não apenas se somam: eles se potencializam. | 1:00 |
| 4 | Correlatos | Hájek e Olej usaram fuzzy só com poluentes; Bezerra et al. usaram fuzzy em Marabá para inundação; o índice de vulnerabilidade comunitária à fumaça (2025) usa médias ponderadas. Lacuna: na nossa revisão, não encontramos nenhum sistema fuzzy que una calor e fumaça num risco à saúde personalizado. | 0:50 |
| 5 | Objetivo | Cinco entradas, uma saída (risco de 0 a 100) e uma conduta. | 0:30 |
| 6 | O que é fuzzy | Ler a tabela: na lógica clássica, 33 °C "não é quente" e 35 °C "é quente", um salto. Na fuzzy, 33 °C é 0,29 quente e 0,29 muito quente, uma transição gradual. | 1:00 |
| 7 | Mamdani | Fuzzificação → regras → inferência (mínimo/máximo) → defuzzificação por centroide. | 0:50 |
| 8 | Arquitetura | Três estágios, 12 + 20 + 45 = 77 regras contra 540 (Raju et al., 1991). Cada estágio produz uma variável com significado físico. | 0:50 |
| 9 | Variáveis | As faixas de PM2.5 cruzam o grau 0,5 nos limites oficiais do IQAr (15/50/75/125). O calor foi calibrado pelo índice da NOAA. | 0:40 |
| 10 | Inovação | Mostrar as três linhas destacadas (todas com 34 °C): com PM2.5 de 10 o IQAr diz "boa" e a carga é moderada; com 35 o IQAr diz "moderada" e a carga é alta (levar a criança para local fechado); com 60 o IQAr diz "ruim" e a carga é muito alta. Nas linhas destacadas o calor sobe a carga em um nível acima do que o IQAr indica. | 1:00 |
| 11 | Metodologia | 8.784 horas de 2024 (CAMS + ERA5); validação, comparação com o IQAr, sinergia e sensibilidade. | 0:40 |
| 12 | Resultados 1 | 40 dias em que calor e fumaça juntos elevaram a carga acima de cada fator isolado, como previsto pelas regras; 30 dias em que o IQAr dizia boa ou moderada e a carga era alta; r = 0,91 é a validação do estágio de calor contra a NOAA. No gráfico, a linha é o IQAr e os pontos são a carga do ARDOR: de setembro a novembro os pontos ficam acima da linha. Pior dia: 24/11/2024. | 1:00 |
| 13 | Resultados 2 | No gráfico dos 12 meses, a janela segura para educação física cai de 10,9 h em julho para 3,3 h em setembro, 0,6 h em outubro e 0 h em novembro. Robustez: com erro de 20% no PM2.5 ou 1 °C, muda no máximo 1 nível. | 0:40 |
| 14 | Demo | Abrir a página e seguir os 5 passos com "Criança + Educação física". Trocar para "Adulto + Caminhar" e mostrar a resposta mudando. No simulador, clicar em "Carregar o pior dia de 2024 (24/11)" e mostrar o quadro IQAr × ARDOR e as regras disparando. | 2:00 |
| 15 | Limitações + IA | Dados de modelo (40 km) e regras sem calibração com dados de saúde. Próximos passos: sensores locais, DATASUS e ANFIS. Declarar o uso do Claude. | 0:40 |
| 16 | Referências | Deixar na tela durante as perguntas. | – |

## Perguntas prováveis do professor

- **Por que Mamdani e não Sugeno?** As saídas são linguísticas e interpretáveis, e o objetivo é explicar a decisão. Sugeno com ANFIS faz sentido para ajustar com dados de saúde, o que está nos trabalhos futuros.
- **Por que centroide?** Ele considera todas as regras ativas proporcionalmente e gera uma saída contínua, sem saltos entre níveis.
- **Como validaram sem dados de saúde?** O estágio 1 foi comparado com o índice da NOAA (r = 0,91). O estágio 2 está ancorado nas faixas oficiais do IQAr e na evidência epidemiológica. O teste de sensibilidade mostrou estabilidade.
- **Como definiram "sinergia"?** São os dias em que o nível da carga combinada é maior que o maior nível obtido zerando um dos fatores: 40 dias.
- **De onde vêm os dados?** API Open-Meteo: PM2.5 do CAMS (Copernicus) e temperatura e umidade do ERA5. São 8.784 horas de 2024 para as coordenadas -5,37 / -49,12.
