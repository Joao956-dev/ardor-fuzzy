# ARDOR: notas do apresentador (para imprimir)

Copiadas de `roteiro_apresentacao.md`. Também estão nas notas do apresentador do Canva.

## Slide 1: Capa
**Quem fala:** João · **Tempo:** 0:20

Apresentar a equipe e o objetivo em uma frase: estimar o risco à saúde de uma atividade ao ar livre considerando calor e fumaça juntos.

## Slide 2: Contexto
**Quem fala:** João · **Tempo:** 0:50

Entre agosto e dezembro, Marabá tem seca e queimadas ao mesmo tempo. Em 2024: 85 dias acima do limite da OMS, 84 deles também quentes. Citar o alerta da Defesa Civil.

## Slide 3: O problema
**Quem fala:** João · **Tempo:** 1:00

O IQAr mede só poluentes e o índice de calor mede só calor. Rai et al. (2023): a poluição aumenta o efeito do calor sobre a mortalidade. Jones-Ngo et al. (2025): ~8% das internações respiratórias vieram da interação. Os efeitos não apenas se somam: eles se potencializam.

## Slide 4: Correlatos
**Quem fala:** João · **Tempo:** 0:50

Hájek e Olej usaram fuzzy só com poluentes; Bezerra et al. usaram fuzzy em Marabá para inundação; o índice de vulnerabilidade comunitária à fumaça (2025) usa médias ponderadas. Lacuna: na nossa revisão, não encontramos nenhum sistema fuzzy que una calor e fumaça num risco à saúde personalizado.

## Slide 5: Objetivo
**Quem fala:** João · **Tempo:** 0:30

Cinco entradas, uma saída (risco de 0 a 100) e uma conduta.

## Slide 6: O que é fuzzy
**Quem fala:** João · **Tempo:** 1:00

Ler a tabela: na lógica clássica, 33 °C "não é quente" e 35 °C "é quente", um salto. Na fuzzy, 33 °C é 0,29 quente e 0,29 muito quente, uma transição gradual.

## Slide 7: Mamdani
**Quem fala:** João · **Tempo:** 0:50

Fuzzificação → regras → inferência (mínimo/máximo) → defuzzificação por centroide.

## Slide 8: Arquitetura
**Quem fala:** João · **Tempo:** 0:50

Três estágios, 12 + 20 + 45 = 77 regras contra 540 (Raju et al., 1991). Cada estágio produz uma variável com significado físico.

## Slide 9: Variáveis
**Quem fala:** Luiz · **Tempo:** 0:40

As faixas de PM2.5 cruzam o grau 0,5 nos limites oficiais do IQAr (15/50/75/125). O calor foi calibrado pelo índice da NOAA.

## Slide 10: Inovação
**Quem fala:** Luiz · **Tempo:** 1:00

Mostrar as três linhas destacadas (todas com 34 °C): com PM2.5 de 10 o IQAr diz "boa" e a carga é moderada; com 35 o IQAr diz "moderada" e a carga é alta (levar a criança para local fechado); com 60 o IQAr diz "ruim" e a carga é muito alta. Nas linhas destacadas o calor sobe a carga em um nível acima do que o IQAr indica.

## Slide 11: Metodologia
**Quem fala:** Luiz · **Tempo:** 0:40

8.784 horas de 2024 (CAMS + ERA5); validação, comparação com o IQAr, sinergia e sensibilidade.

## Slide 12: Resultados 1
**Quem fala:** Luiz · **Tempo:** 1:00

40 dias em que calor e fumaça juntos elevaram a carga acima de cada fator isolado, como previsto pelas regras; 30 dias em que o IQAr dizia boa ou moderada e a carga era alta; r = 0,91 é a validação do estágio de calor contra a NOAA. No gráfico, a linha é o IQAr e os pontos são a carga do ARDOR: de setembro a novembro os pontos ficam acima da linha. Pior dia: 24/11/2024.

## Slide 13: Resultados 2
**Quem fala:** Luiz · **Tempo:** 0:40

No gráfico dos 12 meses, a janela segura para educação física cai de 10,9 h em julho para 3,3 h em setembro, 0,6 h em outubro e 0 h em novembro. Robustez: com erro de 20% no PM2.5 ou 1 °C, muda no máximo 1 nível.

## Slide 14: Demo
**Quem fala:** João · **Tempo:** 2:00

Abrir a página e seguir os 5 passos com "Criança + Educação física". Trocar para "Adulto + Caminhar" e mostrar a resposta mudando. No simulador, clicar em "Carregar o pior dia de 2024 (24/11)" e mostrar o quadro IQAr × ARDOR e as regras disparando.

## Slide 15: Limitações + IA
**Quem fala:** Luiz · **Tempo:** 0:40

Dados de modelo (40 km) e regras sem calibração com dados de saúde. Próximos passos: sensores locais, DATASUS e ANFIS. Declarar o uso do Claude.

## Slide 16: Referências
**Quem fala:** Luiz · **Tempo:** –

Deixar na tela durante as perguntas.
