from flask import Flask, request, jsonify, render_template
import math
import itertools

app = Flask(__name__)

coord = {
    'EDO.MEX': (19.2938, -99.6536),
    'QRO': (20.5935, -100.3900),
    'CDMX': (19.4328, -99.1333),
    'SLP': (22.1517, -100.9765),
    'MTY': (25.6731, -100.2974),
    'PUE': (19.0635, -98.3072),
    'GDL': (20.6771, -103.3469),
    'MICH': (19.7026, -101.1922),
    'SON': (29.0752, -110.9596)
}


almacenes = list(coord.keys())


VELOCIDAD_PROMEDIO = 70  # km/h
CAPACIDAD_MAXIMA = 40  


def distancia(coord1, coord2):
    return round(math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2) * 111)  


def mejor_ruta(almacen, destinos):
    rutas_posibles = itertools.permutations(destinos)
    mejor_ruta = None
    menor_distancia = float('inf')

    for ruta in rutas_posibles:
        distancia_total = sum(distancia(coord[ruta[i]], coord[ruta[i+1]]) for i in range(len(ruta)-1))
        distancia_total += distancia(coord[almacen], coord[ruta[0]])  
        if distancia_total < menor_distancia:
            menor_distancia = distancia_total
            mejor_ruta = [almacen] + list(ruta)  

    return mejor_ruta, menor_distancia


def calcular_ruta_optima(origen, almacen, destinos, pedidos):
    if origen not in coord or almacen not in coord or any(destino not in coord for destino in destinos):
        return {"error": "Los nodos ingresados no existen."}

    pedidos_totales = sum(pedidos.values())
    if pedidos_totales > CAPACIDAD_MAXIMA:
        return {"error": f"La carga total ({pedidos_totales}) excede la capacidad máxima de {CAPACIDAD_MAXIMA} unidades."}

    ruta_final = []
    distancia_total = 0

  
    if origen != almacen:
        ruta_final.append(origen)
        distancia_total += distancia(coord[origen], coord[almacen])

 
    destinos_ruta, distancia_ruta = mejor_ruta(almacen, destinos)
    ruta_final.extend(destinos_ruta)
    distancia_total += distancia_ruta

    tiempo_horas = round(distancia_total / VELOCIDAD_PROMEDIO)

    return {
        "ruta": ruta_final,
        "distancia": distancia_total,
        "tiempo": tiempo_horas,
        "pedidos": pedidos  
    }

@app.route('/ruta', methods=['POST'])
def obtener_ruta():
    datos = request.json
    origen = datos.get("origen", "").strip()
    almacen = datos.get("almacen", "").strip()
    destinos = datos.get("destinos", [])
    pedidos = datos.get("pedidos", {})

    resultado = calcular_ruta_optima(origen, almacen, destinos, pedidos)
    return jsonify(resultado)

@app.route('/')
def index():
    return render_template('index.html', coordenadas=list(coord.keys()), almacenes=almacenes)

if __name__ == '__main__':
    app.run(debug=True)

