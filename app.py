# app.py
"""
Funciones de análisis de apuestas deportivas.
"""
def calcular_probabilidades_desde_cuotas(c_l, c_e, c_v):
    p1, p2, p3 = 1/c_l, 1/c_e, 1/c_v
    s = p1 + p2 + p3
    return p1/s, p2/s, p3/s

def analizar_mas_de_2_5_goles(gl, gv, pct, cuota, bajas=False):
    prob = pct/100
    if (gl + gv)/2 > 1.8:
        prob += 0.05
    if bajas:
        prob -= 0.07
    prob = max(0, min(prob, 1))
    return prob, prob * cuota - 1

def analizar_btts(pl, pv, cuota, baja=False, defensa=False):
    prob = ((pl + pv)/2)/100
    if baja:
        prob -= 0.07
    if defensa:
        prob -= 0.05
    else:
        prob += 0.03
    prob = max(0, min(prob, 1))
    return prob, prob * cuota - 1

def analizar_resultado_1x2(pl, pe, pv, cl, ce, cv):
    resultados = []
    for nombre, prob, cuota in [
        ("Local", pl, cl),
        ("Empate", pe, ce),
        ("Visitante", pv, cv)
    ]:
        ve = prob * cuota - 1
        resultados.append((nombre, prob, cuota, ve))
    return resultados

