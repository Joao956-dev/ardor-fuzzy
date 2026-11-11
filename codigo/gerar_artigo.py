"""Gera o artigo no formato IEEE (duas colunas) em .docx."""
import json, os, sys, math
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(B, "codigo"))
import ardor as A
ST = json.load(open(os.path.join(B, "dados", "estatisticas.json"), encoding="utf8"))
F = lambda n: os.path.join(B, "figuras", n)
br = lambda x, d=1: f"{x:.{d}f}".replace(".", ",")

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.space_after = Pt(0); st.paragraph_format.line_spacing = 1.0

s0 = doc.sections[0]
s0.page_width, s0.page_height = Inches(8.27), Inches(11.69)
s0.top_margin, s0.bottom_margin = Inches(0.75), Inches(1.0)
s0.left_margin = s0.right_margin = Inches(0.63)


def par(texto="", tam=10, neg=False, ital=False, alin=WD_ALIGN_PARAGRAPH.JUSTIFY, recuo=True, antes=0, depois=0):
    p = doc.add_paragraph(); p.alignment = alin
    pf = p.paragraph_format; pf.space_before = Pt(antes); pf.space_after = Pt(depois)
    if recuo: pf.first_line_indent = Inches(0.14)
    if texto:
        r = p.add_run(texto); r.font.size = Pt(tam); r.bold = neg; r.italic = ital
    return p


def rich(partes, recuo=True):
    """partes: lista de (texto, 'b'|'i'|'')"""
    p = par(recuo=recuo)
    for t, f in partes:
        r = p.add_run(t); r.bold = "b" in f; r.italic = "i" in f
    return p


ROM = iter(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"])
def secao(titulo):
    p = par(alin=WD_ALIGN_PARAGRAPH.CENTER, recuo=False, antes=8, depois=4)
    r = p.add_run(f"{next(ROM)}. {titulo.upper()}"); r.font.size = Pt(10); r.font.small_caps = True


def sub(letra, titulo):
    p = par(alin=WD_ALIGN_PARAGRAPH.LEFT, recuo=False, antes=4, depois=2)
    r = p.add_run(f"{letra}. {titulo}"); r.italic = True


nfig = iter(range(1, 20)); ntab = iter(["I", "II", "III", "IV", "V", "VI", "VII"])
def figura(arq, legenda, larg=3.4):
    p = par(alin=WD_ALIGN_PARAGRAPH.CENTER, recuo=False, antes=4)
    p.add_run().add_picture(F(arq), width=Inches(larg))
    c = par(alin=WD_ALIGN_PARAGRAPH.JUSTIFY, recuo=False, depois=6)
    r = c.add_run(f"Fig. {next(nfig)}. "); r.font.size = Pt(8)
    r = c.add_run(legenda); r.font.size = Pt(8)


def tabela(titulo, linhas, larg=None, fonte=7.5):
    p = par(alin=WD_ALIGN_PARAGRAPH.CENTER, recuo=False, antes=6)
    r = p.add_run(f"TABELA {next(ntab)}"); r.font.size = Pt(8); p.paragraph_format.keep_with_next = True
    p = par(alin=WD_ALIGN_PARAGRAPH.CENTER, recuo=False, depois=2)
    r = p.add_run(titulo.upper()); r.font.size = Pt(8); r.font.small_caps = True; p.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=len(linhas), cols=len(linhas[0])); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, lin in enumerate(linhas):
        for j, v in enumerate(lin):
            cel = t.cell(i, j); cel.text = ""
            pp = cel.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rr = pp.add_run(str(v)); rr.font.size = Pt(fonte); rr.bold = i == 0
            pp.paragraph_format.keep_with_next = i < len(linhas) - 1  # tabela não se divide entre colunas/páginas
    if larg:
        t.autofit = False
        tblPr = t._tbl.tblPr
        lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
        tw = OxmlElement("w:tblW"); tw.set(qn("w:w"), str(int(sum(larg) * 1440))); tw.set(qn("w:type"), "dxa")
        for old in tblPr.findall(qn("w:tblW")): tblPr.remove(old)
        tblPr.append(tw)
        grid = t._tbl.tblGrid
        for j, gc in enumerate(grid.findall(qn("w:gridCol"))):
            gc.set(qn("w:w"), str(int(larg[j] * 1440)))
        for row in t.rows:
            for j, w in enumerate(larg):
                row.cells[j].width = Inches(w)
    par(recuo=False, depois=4)


# ------------------------------------------------------------------ titulo (1 coluna)
p = par(alin=WD_ALIGN_PARAGRAPH.CENTER, recuo=False, depois=8)
r = p.add_run("ARDOR: Sistema Fuzzy Hierárquico para Avaliação do Risco Composto de Calor e Fumaça de Queimadas em Marabá-PA")
r.font.size = Pt(22)
p = par(alin=WD_ALIGN_PARAGRAPH.CENTER, recuo=False)
p.add_run("João Vitor Barros e Luiz Antônio Machado").font.size = Pt(11)
p = par(alin=WD_ALIGN_PARAGRAPH.CENTER, recuo=False, depois=12)
r = p.add_run("Faculdade de Engenharia da Computação, Universidade Federal do Sul e Sudeste do Pará (Unifesspa), Marabá-PA, Brasil")
r.font.size = Pt(9); r.italic = True

# ------------------------------------------------------------------ corpo (2 colunas)
sec = doc.add_section(WD_SECTION.CONTINUOUS)
cols = sec._sectPr.xpath("./w:cols")
c = cols[0] if cols else OxmlElement("w:cols")
c.set(qn("w:num"), "2"); c.set(qn("w:space"), "360")
if not cols: sec._sectPr.append(c)

rich([("Resumo—", "bi"), (
    "Os índices oficiais tratam a poluição do ar e o calor separadamente, embora estudos epidemiológicos recentes mostrem que os dois "
    "agravos, quando simultâneos, produzem efeitos sobre a saúde maiores do que cada um isolado. Este trabalho apresenta o ARDOR, "
    "um sistema de inferência fuzzy hierárquico do tipo Mamdani que estima o risco à saúde de uma atividade ao ar livre a partir de "
    "temperatura, umidade relativa, concentração de material particulado fino (PM2.5), vulnerabilidade do indivíduo e esforço físico. "
    "A arquitetura em três estágios usa 77 regras, contra 540 de uma base plana equivalente, e tem os conjuntos de PM2.5 ancorados nas faixas do IQAr "
    "da Resolução CONAMA 506/2024. Aplicado aos 366 dias de 2024 em Marabá-PA, o sistema identificou "
    f"{ST['sinergia']} dias em que a combinação de calor e fumaça elevou o nível de alerta acima do que cada fator indicaria sozinho, e "
    f"{ST['iqar_boa_mod_mas_carga_alta']} dias classificados como \"boa\" ou \"moderada\" pelo IQAr nos quais a carga ambiental foi alta. "
    "O primeiro estágio reproduziu o índice de calor da NOAA com correlação de Pearson de "
    f"{br(ST['r_pearson_fis1_hi'], 2)}, e a saída mostrou-se estável a erros de sensor típicos. Uma interface web interativa consome "
    "previsões horárias e indica janelas seguras para atividades ao ar livre.", "")], recuo=False)
rich([("Palavras-chave—", "bi"), ("lógica fuzzy, sistema Mamdani hierárquico, qualidade do ar, estresse térmico, queimadas, Amazônia, saúde pública.", "i")], recuo=False)

secao("Introdução")
par("Entre agosto e dezembro, o sudeste do Pará convive com duas ameaças que chegam juntas: o calor da estação seca e a fumaça das "
    "queimadas. Em agosto de 2024, a Defesa Civil de Marabá alertou para a piora da qualidade do ar e recomendou que crianças, idosos e "
    "pessoas com doenças respiratórias evitassem sair de casa [1]. No mesmo ano, estimativas por satélite apontaram médias diárias de "
    "PM2.5 dezenas de vezes acima do guia da Organização Mundial da Saúde (OMS) em comunidades paraenses [2].")
par("O problema é que a orientação à população se apoia em índices que olham um fator por vez. O Índice de Qualidade do Ar (IQAr) "
    "classifica apenas a concentração de poluentes [3], enquanto o índice de calor classifica apenas a sensação térmica [4]. "
    "Estudos recentes, no entanto, mostram interação entre os dois: em 482 cidades de 24 países, a poluição aumentou o efeito do "
    "calor sobre a mortalidade cardiorrespiratória [5], e na Califórnia cerca de 8% das internações respiratórias associadas à "
    "fumaça e ao calor extremo foram atribuídas à interação entre ambos [6]. Uma professora que decide se a aula de educação física "
    "acontece na quadra às 14 h precisa de uma resposta que combine essas informações e considere quem está exposto.")
par("Esse tipo de decisão é naturalmente vago. Não existe um limite exato em que um dia \"quente\" passa a ser \"muito quente\", "
    "e especialistas raciocinam com termos linguísticos. A lógica fuzzy [7] foi criada para esse cenário. Este artigo propõe o ARDOR "
    "(Avaliação de Risco Difuso para Ondas de calor e fumaça), com três contribuições: (i) um sistema fuzzy hierárquico que modela "
    "explicitamente a sinergia entre calor e fumaça; (ii) a personalização do risco por vulnerabilidade e esforço físico, com "
    "recomendações de conduta; e (iii) uma avaliação com um ano completo de dados horários de Marabá e uma interface web que usa previsões em tempo real.")

secao("Trabalhos Correlatos")
par("A lógica fuzzy já foi aplicada à qualidade do ar. Hájek e Olej [8] propuseram sistemas Mamdani hierárquicos como alternativa "
    "aos índices tradicionais, argumentando que limites rígidos ignoram condições locais; o trabalho, porém, combina apenas "
    "poluentes, sem considerar variáveis meteorológicas ou o perfil do exposto. Na direção oposta, sistemas fuzzy de risco de "
    "incêndio florestal usam temperatura, umidade e vento para estimar a probabilidade de fogo, e não o efeito da fumaça sobre as pessoas.")
par("No contexto local, Bezerra, Pessoa e Ferreira Filho [9] usaram lógica fuzzy e geoprocessamento para mapear a vulnerabilidade "
    "de Marabá a inundações, o que mostra a aceitação do método para riscos ambientais no município. Na saúde pública, índices de "
    "vulnerabilidade à fumaça combinam exposição, sensibilidade e capacidade adaptativa por médias ponderadas, sem tratar "
    "incerteza nem interação entre agravos [10]. Na revisão realizada, não encontramos um sistema fuzzy que una calor e fumaça num "
    "único risco à saúde, personalizado e operacional. Essa é a lacuna que o ARDOR ocupa.")

secao("Fundamentação Teórica")
sub("A", "Conjuntos fuzzy e variáveis linguísticas")
par("Um conjunto fuzzy A em um universo X é definido por uma função de pertinência μA: X → [0, 1], que atribui a cada elemento um "
    "grau de pertencimento [7]. Uma variável linguística, como \"temperatura\", assume termos (\"amena\", \"quente\", \"muito quente\") "
    "representados por conjuntos fuzzy. Neste trabalho usamos funções triangulares e trapezoidais, que são simples de interpretar e de "
    "ajustar a limites normativos. A Tabela I compara as duas abordagens para a temperatura: com um limite rígido em 35 °C, "
    "33 °C e 35 °C recebem respostas opostas, enquanto os graus fuzzy mudam de forma gradual.")
_rot = {"amena": "amena", "quente": "quente", "muito_quente": "muito quente", "extrema": "extrema"}
_lin = [["Temperatura", "Clássica (quente se ≥ 35 °C)", "Fuzzy (graus de pertinência)"]]
for _t in [27, 31, 33, 35, 37]:
    _g = A.T.fuzzificar(_t)
    _lin.append([f"{_t} °C", "1" if _t >= 35 else "0", "; ".join(f"{_rot[k]} {br(v, 2)}" for k, v in _g.items() if v > 0)])
tabela("Lógica clássica × fuzzy para a temperatura", _lin, [0.75, 1.05, 1.6])
sub("B", "Inferência de Mamdani")
par("No modelo de Mamdani [11], cada regra tem a forma SE x1 é A1 E x2 é A2 ENTÃO y é C. A força de disparo é o mínimo dos graus "
    "dos antecedentes (operador E); o consequente é cortado por essa força (implicação por mínimo); as saídas de todas as regras são "
    "agregadas pelo máximo; e a saída numérica é obtida pelo centroide y* = ∫ y μ(y) dy / ∫ μ(y) dy.")
sub("C", "Sistemas fuzzy hierárquicos")
par("Em uma base de regras completa, o número de regras cresce exponencialmente com o número de entradas. Sistemas hierárquicos "
    "encadeiam subsistemas menores, em que a saída de um alimenta o seguinte, e o número de regras cresce aproximadamente de forma "
    "linear [12]. Além de reduzir a base, essa estrutura produz variáveis intermediárias com significado físico, o que facilita a explicação ao usuário.")

secao("Metodologia")
sub("A", "Área de estudo e dados")
par("Marabá (5,37° S; 49,12° O) fica na confluência dos rios Tocantins e Itacaiúnas, numa região de intensa atividade agropecuária "
    "e mineral. Foram usados dados horários de 2024 obtidos pela API Open-Meteo [13]: PM2.5 da reanálise/previsão do Copernicus "
    "Atmosphere Monitoring Service (CAMS) [14] e temperatura e umidade relativa a 2 m da reanálise ERA5 [15], num total de 8.784 "
    "horas sem falhas. Para a análise diária, usou-se a média de 24 h do PM2.5, como no IQAr, e a condição térmica da hora de maior índice de calor entre 10 h e 16 h.")
sub("B", "Arquitetura")
par("O ARDOR encadeia três sistemas Mamdani (Fig. 1). O FIS-1 converte temperatura e umidade em estresse térmico (0–10). O FIS-2 "
    "combina o estresse térmico com o PM2.5 numa carga ambiental (0–100), que descreve o ambiente independentemente de quem está "
    "nele. O FIS-3 cruza a carga com a vulnerabilidade do indivíduo e o esforço da atividade, gerando o risco pessoal (0–100) e uma conduta recomendada.")
figura("f1_arquitetura.png", "Arquitetura hierárquica do ARDOR. As 77 regras se distribuem em três estágios; uma base plana com as mesmas cinco entradas e os mesmos termos exigiria 4×3×5×3×3 = 540 regras.")
sub("C", "Variáveis e funções de pertinência")
par("A Tabela II resume as variáveis. Os conjuntos de PM2.5 foram posicionados para que os pontos de cruzamento (grau 0,5) coincidam "
    "com os limites do IQAr para MP2,5 em 24 h: 15, 50, 75 e 125 µg/m³ [3], [18]. O limite de 15 µg/m³ é o guia da OMS de 2021 [16]. Os termos "
    "de temperatura e umidade foram calibrados de modo que o FIS-1 acompanhe as faixas do índice de calor da NOAA [4]. A Fig. 2 mostra as funções resultantes.")
tabela("Variáveis linguísticas do ARDOR", [
    ["Variável", "Universo", "Termos"],
    ["Temperatura", "15–45 °C", "amena, quente, muito quente, extrema"],
    ["Umidade relativa", "10–100 %", "seca, moderada, úmida"],
    ["PM2.5 (24 h)", "0–200 µg/m³", "boa, moderada, ruim, muito ruim, péssima"],
    ["Estresse térmico", "0–10", "baixo, moderado, alto, extremo"],
    ["Carga ambiental", "0–100", "baixa, moderada, alta, muito alta, crítica"],
    ["Vulnerabilidade", "0–10", "baixa, média, alta"],
    ["Esforço", "0–10", "leve, moderado, intenso"],
    ["Risco pessoal", "0–100", "baixo, moderado, alto, muito alto, crítico"]], [0.95, 0.75, 1.7])
figura("f2_pertinencia.png", "Funções de pertinência das entradas e saídas. No painel de PM2.5, as linhas pontilhadas marcam os limites oficiais do IQAr.")
sub("D", "Base de regras")
par("As 12 regras do FIS-1 seguem a lógica do índice de calor: a umidade alta agrava a temperatura e o ar seco a atenua. O núcleo do "
    "trabalho está nas 20 regras do FIS-2 (Tabela III). Na diagonal da matriz, a combinação de PM2.5 e calor recebe um nível acima do que "
    "cada fator produziria isoladamente. Por exemplo, SE PM2.5 é moderada E calor é alto ENTÃO carga é alta, embora o IQAr, sozinho, "
    "indicasse apenas \"moderada\". Essa escolha traduz a interação relatada em [5] e [6].")
tabela("Regras do FIS-2 (carga ambiental)", [
    ["PM2.5 \\ calor", "baixo", "moderado", "alto", "extremo"],
    ["boa", "baixa", "baixa", "moderada", "alta"],
    ["moderada", "moderada", "moderada", "alta", "muito alta"],
    ["ruim", "alta", "alta", "muito alta", "crítica"],
    ["muito ruim", "muito alta", "muito alta", "crítica", "crítica"],
    ["péssima", "crítica", "crítica", "crítica", "crítica"]], [0.8, 0.6, 0.65, 0.65, 0.7])
par("As 45 regras do FIS-3 seguem um princípio de deslocamento que pode ser auditado: partindo do nível da carga, a vulnerabilidade média ou alta "
    "sobe um nível, o esforço leve desce um e o intenso sobe um. Grupos de alta vulnerabilidade sobem um nível adicional quando a carga "
    "é alta ou maior, refletindo a resposta desproporcional de asmáticos e cardiopatas. Duas restrições de segurança completam a base: ar limpo e sem calor "
    "nunca passa de risco moderado, e carga crítica nunca fica abaixo de risco muito alto. O risco final é traduzido em cinco condutas: "
    "liberado (<25), atenção (25–45), reduzir (45–65), evitar (65–82) e suspender (≥82).")
sub("E", "Implementação e protocolo de avaliação")
par("O motor de inferência foi implementado do zero em Python/NumPy, sem bibliotecas fuzzy prontas, com universos discretizados em 501 "
    "pontos. Uma versão em JavaScript alimenta a interface web; em 300 casos aleatórios a diferença máxima entre as duas implementações "
    "foi da ordem de 10⁻¹², ou seja, apenas arredondamento de ponto flutuante. A avaliação teve quatro partes: (a) validação do FIS-1 contra o índice de calor da NOAA; (b) comparação diária entre o "
    "ARDOR e o IQAr; (c) quantificação da sinergia, comparando a carga combinada com as cargas obtidas zerando um fator por vez; e "
    "(d) análise de sensibilidade a erros de medição de ±20% no PM2.5, típicos de sensores de baixo custo, e de ±1 °C na temperatura.")

secao("Resultados e Discussão")
sub("A", "Comportamento do sistema")
par("A Fig. 3 mostra as superfícies de controle. No FIS-2, a carga cresce com o PM2.5 em qualquer nível de calor, mas a superfície se "
    "inclina mais rápido quando os dois aumentam juntos, que é o efeito desejado. A validação do FIS-1 com 2.928 horas resultou em "
    f"correlação de Pearson de {br(ST['r_pearson_fis1_hi'], 3)} e de Spearman de {br(ST['r_spearman_fis1_hi'], 3)} com o índice de "
    "calor da NOAA, o que mostra que 12 regras linguísticas reproduzem bem uma fórmula empírica de nove termos.")
figura("f3_superficies.png", "Superfícies de controle do FIS-1 (esquerda) e do FIS-2 (direita).")
par("A Tabela IV mostra o efeito da interação em seis combinações de condições, para uma criança em educação física "
    "(vulnerabilidade 5 e esforço 5,5). Nas linhas com 34 °C e PM2.5 de 35 ou 60 µg/m³, o IQAr continua \"moderada\" ou \"ruim\", "
    "mas o calor eleva a carga ambiental em um nível acima do que o IQAr indica, e a conduta passa a ser levar a atividade para local fechado ou não realizá-la ao ar livre.")
_niq = ["boa", "moderada", "ruim", "muito ruim", "péssima"]
_nic = ["normal", "cautela", "cautela extrema", "perigo", "perigo extremo"]
_ncg = ["baixa", "moderada", "alta", "muito alta", "crítica"]
_rd = lambda x: int(math.floor(x + 0.5))
_lin = [["PM2.5 (µg/m³)", "T, UR", "IQAr", "Índice de calor (°C)", "Carga", "Risco (conduta)"]]
for _pm in [10, 35, 60]:
    for _T, _U in [(27, 65), (34, 60)]:
        _hi = A.indice_calor_noaa(_T, _U); _r = A.avaliar(_T, _U, _pm, 5, 5.5); _c = A.nivel_risco(_r["carga"])
        _lin.append([str(_pm), f"{_T} °C, {_U} %", _niq[A.nivel_iqar(_pm)], f"{_nic[A.nivel_calor_noaa(_hi)]} ({br(_hi)})",
                     f"{_ncg[_c]} ({_rd(_r['carga'])})", f"{_rd(_r['risco'])} ({_r['rec'].replace('Atencao', 'atenção').lower()})"])
tabela("Índices separados × ARDOR (criança em educação física)", _lin, [0.4, 0.46, 0.58, 0.6, 0.66, 0.7], fonte=7)
sub("B", "O ano de 2024 em Marabá")
pm = ST["pm_mes"]
par(f"Dos 366 dias, {ST['pm_oms']} tiveram média de PM2.5 acima do guia da OMS, e {ST['ambos']} deles (99%) também tiveram índice "
    f"de calor na faixa de cautela (≥ 32 °C). Em Marabá, portanto, a fumaça praticamente não chega sem o calor. A concentração média subiu de "
    f"{br(pm['8'])} µg/m³ em agosto para {br(pm['9'])} em setembro, {br(pm['10'])} em outubro e {br(pm['11'])} em novembro, o mês mais "
    "crítico (Fig. 4).")
figura("f4_serie_2024.png", "Série diária de 2024: PM2.5 médio, índice de calor máximo da tarde e carga ambiental do ARDOR (pontos coloridos pelo nível), com o nível do IQAr sobreposto.")
dc, di = ST["dist_carga"], ST["dist_iqar"]
par(f"A Tabela V compara as classificações. O IQAr nunca passou de \"moderada\" ({di[1]} dias), enquanto a carga do ARDOR atingiu "
    f"o nível alto em {dc[2]} dias. Em {ST['subestimados_iqar']} dias a carga ficou acima do nível do IQAr, e em {ST['iqar_boa_mod_mas_carga_alta']} "
    f"dias o índice oficial dizia \"boa\" ou \"moderada\" enquanto o ARDOR indicava carga alta. Ao zerar um fator por vez, "
    f"verificou-se que em {ST['sinergia']} dias a carga combinada superou o maior dos níveis isolados. Esses são os dias em que "
    "a sinergia muda a decisão.")
dc_, da, dk, ds = ST["dist_carga"], ST["dist_adulto"], ST["dist_crianca"], ST["dist_sensivel"]
tabela("Dias de 2024 por nível de alerta", [
    ["Classificação", "Baixo", "Mod.", "Alto", "M. alto", "Crít."],
    ["IQAr (só PM2.5)", *di], ["ARDOR carga", *dc_], ["Adulto, leve", *da], ["Criança, ed. física", *dk], ["Sensível, moderada", *ds]],
    [1.1, 0.45, 0.45, 0.45, 0.5, 0.5])
figura("f6_distribuicao.png", "Distribuição dos dias de 2024 por nível: o IQAr comparado à carga ambiental e ao risco pessoal de três perfis.")
par(f"A personalização altera bastante a resposta. Para um adulto saudável caminhando, o risco ficou baixo em {da[0]} dias. Para uma "
    f"criança em educação física, que tem ventilação pulmonar maior por massa corporal e menor capacidade de termorregulação, houve {dk[2]} dias de risco "
    f"alto e {dk[3]} de risco muito alto. Para pessoas com asma ou cardiopatia em atividade moderada, houve {ds[4]} dias críticos. "
    "O dia mais grave do ano, 24/11/2024, ilustra o problema: PM2.5 de 46,2 µg/m³ (IQAr \"moderada\") e índice de calor de 37,7 °C "
    "resultaram em carga alta, recomendação \"evitar\" para crianças e \"suspender\" para o grupo sensível.")
sub("C", "Janelas seguras ao longo do dia")
jn = ST["janela_segura_crianca_h"]
par("Aplicando o sistema hora a hora (Fig. 5), com o PM2.5 em média móvel de 24 h, obteve-se o número médio de horas por dia, entre 7 h e "
    f"17 h, com risco abaixo de 45 para uma criança em educação física. Em julho foram {br(jn['7'])} h por dia; em setembro, {br(jn['9'])} h; "
    f"em outubro, {br(jn['10'])} h; e em novembro, {br(jn['11'])} h. Na prática, durante a temporada de fumaça, atividades físicas "
    "intensas de crianças ao ar livre deveriam ser transferidas para ambientes fechados, e não apenas antecipadas para o início da manhã.")
figura("f5_mapa_hora_mes.png", "Risco médio por mês e hora do dia para uma criança em educação física (2024).")
sub("D", "Sensibilidade")
sv = ST["sensibilidade"]
par("A Tabela VI mostra a fração de dias em que a conduta para o perfil infantil não mudou sob perturbações nas entradas. Em todos os "
    "cenários, a mudança máxima foi de um nível, sem saltos abruptos, o que se deve à sobreposição suave das funções de pertinência. "
    "O sistema é mais sensível à temperatura do que ao PM2.5, porque em Marabá o calor quase sempre está próximo das fronteiras entre termos.")
tabela("Robustez a erros de medição (perfil infantil)", [
    ["Perturbação", "Dias sem mudança", "Maior salto"],
    *[[k.replace("C", " °C") if "T" in k else k, br(v["iguais"]) + " %", f"{v['max_salto']} nível"] for k, v in sv.items()]], [1.1, 1.1, 0.9])
sub("E", "Interface interativa")
par("A interface web (arquivo único em HTML e JavaScript) tem três partes: (i) o veredito atual para o perfil escolhido, com uma faixa "
    "das próximas 48 h colorida por nível e a indicação da próxima janela segura, calculadas a partir das previsões horárias de PM2.5 e "
    "meteorologia; (ii) um simulador com controles deslizantes que mostra, em tempo real, os graus de pertinência, a área agregada usada "
    "pelo centroide e as regras de maior força; e (iii) os resultados de 2024. Ao exibir as regras disparadas, a interface explica por que chegou à recomendação.")

secao("Limitações e Trabalhos Futuros")
par("O PM2.5 do CAMS vem de um modelo com resolução de cerca de 40 km e tende a suavizar picos locais; por isso, os números deste "
    "trabalho provavelmente subestimam a exposição real. As regras foram construídas a partir da literatura e de normas, sem "
    "calibração com dados de saúde locais. Como trabalhos futuros, propomos: integrar os sensores de baixo custo já instalados em "
    "Marabá [17]; ajustar as funções de pertinência com dados de internações do DATASUS, por exemplo com ANFIS; e incluir vento e "
    "radiação solar no estresse térmico.")

secao("Conclusão")
par("O ARDOR mostrou que a lógica fuzzy é uma forma natural de unir dois riscos que os índices oficiais tratam separadamente. Com 77 "
    "regras interpretáveis, o sistema reproduziu o índice de calor, respeitou os limites do IQAr e revelou dezenas de dias de 2024 em "
    "que calor e fumaça se potencializaram em Marabá, tornando a condição mais perigosa do que cada fator sozinho indicaria. Para escolas, empregadores e "
    "serviços de saúde, a principal contribuição é uma pergunta simples com resposta explicável: se é seguro fazer atividade ao ar livre agora e, se não for, quando será.")

p = par(alin=WD_ALIGN_PARAGRAPH.CENTER, recuo=False, antes=8, depois=4)
r = p.add_run("DECLARAÇÃO DE USO DE INTELIGÊNCIA ARTIFICIAL"); r.font.small_caps = True
par("Os autores declaram que utilizaram ferramentas de Inteligência Artificial Generativa neste projeto. Foi usado o assistente "
    "Claude (modelo Claude Opus 5.5, Anthropic), por meio do aplicativo Claude Code, nas seguintes etapas: (i) definição do "
    "problema, com pesquisa e triagem de artigos correlatos e verificação de referências; (ii) modelagem, com sugestões para a "
    "arquitetura hierárquica, os termos linguísticos e a base de regras; (iii) implementação, com geração do código Python do "
    "motor de inferência, dos scripts de análise e da interface web em HTML/JavaScript; (iv) análise dos resultados e geração "
    "das figuras; e (v) redação preliminar deste artigo e do roteiro da apresentação. Todo o conteúdo gerado foi revisado, "
    "executado e validado pelos autores, que conferiram as referências, os números e as decisões de modelagem e assumem integral "
    "responsabilidade pelo trabalho. Nenhum dado pessoal foi fornecido à ferramenta.")

p = par(alin=WD_ALIGN_PARAGRAPH.CENTER, recuo=False, antes=8, depois=4)
r = p.add_run("REFERÊNCIAS"); r.font.small_caps = True
REFS = [
    "Portal Debate Carajás, \"Defesa Civil alerta para qualidade do ar em Marabá após queimadas,\" ago. 2024. [Online]. Disponível: https://debatecarajas.com.br",
    "InfoAmazonia, \"Comunidade do Pará tem a maior concentração diária de poluição por fumaça,\" mar. 2025. [Online]. Disponível: https://infoamazonia.org",
    "Ministério do Meio Ambiente, \"Orientação técnica: Índice de Qualidade do Ar (IQAr),\" Brasília, jan. 2025.",
    "L. P. Rothfusz, \"The heat index equation,\" National Weather Service, Fort Worth, TX, Tech. Attachment SR 90-23, 1990.",
    "M. Rai et al., \"Heat-related cardiorespiratory mortality: Effect modification by air pollution across 482 cities from 24 countries,\" Environ. Int., vol. 174, art. 107825, 2023, doi: 10.1016/j.envint.2023.107825.",
    "C. G. Jones-Ngo et al., \"Joint effects of wildfire smoke and extreme heat on hospitalizations in California, 2011–2020,\" GeoHealth, vol. 9, no. 6, art. e2024GH001237, 2025, doi: 10.1029/2024GH001237.",
    "L. A. Zadeh, \"Fuzzy sets,\" Inf. Control, vol. 8, no. 3, pp. 338–353, 1965.",
    "P. Hájek and V. Olej, \"Air pollution assessment using hierarchical fuzzy inference systems,\" Sci. Papers Univ. Pardubice, Ser. D, vol. 15, pp. 52–61, 2009.",
    "P. E. Bezerra, F. Pessoa, and D. Ferreira Filho, \"Modelagem espacial da vulnerabilidade à inundação no município de Marabá-PA via lógica fuzzy,\" Rev. Geoaraguaia, vol. 13, no. 2, pp. 1–21, 2023.",
    "\"Advancing the community health vulnerability index for wildland fire smoke exposure,\" 2025. [Online]. Disponível: https://pmc.ncbi.nlm.nih.gov/articles/PMC12087597/",
    "E. H. Mamdani and S. Assilian, \"An experiment in linguistic synthesis with a fuzzy logic controller,\" Int. J. Man-Mach. Stud., vol. 7, no. 1, pp. 1–13, 1975.",
    "G. V. S. Raju, J. Zhou, and R. A. Kisner, \"Hierarchical fuzzy control,\" Int. J. Control, vol. 54, no. 5, pp. 1201–1216, 1991, doi: 10.1080/00207179108934205.",
    "Open-Meteo, \"Free weather and air quality API,\" 2026. [Online]. Disponível: https://open-meteo.com",
    "A. Inness et al., \"The CAMS reanalysis of atmospheric composition,\" Atmos. Chem. Phys., vol. 19, pp. 3515–3556, 2019.",
    "H. Hersbach et al., \"The ERA5 global reanalysis,\" Q. J. R. Meteorol. Soc., vol. 146, pp. 1999–2049, 2020.",
    "World Health Organization, WHO Global Air Quality Guidelines: Particulate Matter (PM2.5 and PM10), Ozone, Nitrogen Dioxide, Sulfur Dioxide and Carbon Monoxide. Geneva: WHO, 2021.",
    "O Liberal, \"Sensores de baixo custo ajudam no monitoramento da qualidade do ar no Pará,\" s.d. [Online]. Disponível: https://www.oliberal.com",
    "Conselho Nacional do Meio Ambiente, Resolução CONAMA nº 506, de 5 de julho de 2024, Diário Oficial da União, 2024.",
]
for i, ref in enumerate(REFS, 1):
    p = par(alin=WD_ALIGN_PARAGRAPH.JUSTIFY, recuo=False)
    p.paragraph_format.left_indent = Inches(0.25); p.paragraph_format.first_line_indent = Inches(-0.25)
    r = p.add_run(f"[{i}]\t{ref}"); r.font.size = Pt(8)

out = os.path.join(B, "artigo", "ARDOR_artigo_IEEE.docx")
doc.save(out); print("salvo", out)
