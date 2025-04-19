# backend.py
import pandas as pd
import numpy as np
import math

#BLOQUE 1 

# Cargar todas las hojas en un diccionario de DataFrames
excel_tablas = "Tablas PER 2000 y 2020.xlsx"
hojas = pd.read_excel(excel_tablas, sheet_name=None, header=1)

def generacion(g, nombre_tabla):
    """
    Determina el año base según la tabla de mortalidad y la generación.
    
    Args:
        g (int): Año de nacimiento (generación).
        nombre_tabla (str): Nombre de la tabla de mortalidad.
    
    Returns:
        int: Año base para la tabla (2000 o 2012).
    
    Raises:
        ValueError: Si la generación no es válida o la tabla no es reconocida.
    """
    if nombre_tabla in ['PERM2000C', 'PERF2000C', 'PERM2000P', 'PERF2000P']:
        anio_base = 2000
        if g > 2000:
            raise ValueError("La generación no puede ser mayor a 2000.")
    elif nombre_tabla in ['PERM_2020_Indiv_2Orden', 'PERM_2020_Indiv_1Orden',
                          'PERF_2020_Indiv_2Orden', 'PERF_2020_Indiv_1Orden',
                          'PERM_2020_Colectivos_2Orden', 'PERM_2020_Colectivos_1Orden',
                          'PERF_2020_Colectivos_2Orden', 'PERF_2020_Colectivos_1Orden']:
        anio_base = 2012
        if g > 2012:
            raise ValueError("La generación no puede ser mayor a 2012.")
    else:
        raise ValueError(f"Tabla no reconocida: {nombre_tabla}")
    
    return anio_base

def q_x(qx, mejora, t):
    """
    Ajusta la probabilidad de muerte qx según el factor de mejora.
    
    Args:
        qx (float): Probabilidad de muerte base.
        mejora (float): Factor de mejora.
        t (int): Tiempo para el ajuste.
    
    Returns:
        float: Probabilidad de muerte ajustada.
    """
    return qx * math.exp(-mejora * t)

def tabla_gen(g, nombre_tabla):
    """
    Genera la tabla generacional para un asegurado.
    
    Args:
        g (int): Año de nacimiento.
        nombre_tabla (str): Nombre de la tabla de mortalidad.
    
    Returns:
        pd.DataFrame: Tabla generacional con columnas:
            - Anual: 'x+t', 'qx+t ajustado', 'lx', 'dx'.
    """
    # Obtener el año base
    anio_base = generacion(g, nombre_tabla)
    # Calcular la edad inicial (x+t) en el año base
    edad_inicio = anio_base - g
    
    # Leer la tabla de mortalidad
    df = hojas[nombre_tabla].copy()
    
    # Asegurarnos de que el índice sea 'x+t' o similar
    if df.index.name is None or 'x+t' not in df.index.name.lower():
        index_col = None
        for col in df.columns:
            if 'x+t' in col.lower():
                index_col = col
                break
        if index_col:
            df.set_index(index_col, inplace=True)
        else:
            raise ValueError(f"No se encontró una columna de índice 'x+t' en la tabla {nombre_tabla}.")

    # Imprimir las columnas para depurar
    print(f"Columnas de la tabla {nombre_tabla}: {df.columns.tolist()}")
    print("Primeros valores de la tabla de mortalidad:")
    print(df.head(10))

    # Renombrar columnas según el tipo de tabla
    if len(df.columns) == 2:  # Tablas PERM2000/PERF2000 y PER_2020_Indiv_2Orden
        # Verificar si es una tabla PER_2020 de 2do orden
        if '2Orden' in nombre_tabla:
            # Las columnas son 'qx+t, tabla base' y 'λx+t (mejora)'
            df.columns = ['qx', 'mejora']
        else:
            # Tablas PERM2000/PERF2000
            df.columns = ['qx', 'mejora']
    elif len(df.columns) == 4:  # Tablas PER_2020_Indiv_1Orden
        # Las columnas son: 'Rec. técnico base', 'qx+t, tabla base', 'Rec. técnico factor', 'λx+t'
        df = df.iloc[:, [1, 3]]  # Seleccionamos 'qx+t, tabla base' y 'λx+t'
        df.columns = ['qx', 'mejora']
    else:
        raise ValueError(f"La tabla {nombre_tabla} tiene un número inesperado de columnas: {len(df.columns)}")

    df.index.name = 'edad'

    # Generar la tabla generacional hasta ω
    omega = 120
    x_mas_t_list = list(range(edad_inicio, omega + 1))
    edad_t = list(range(0, len(x_mas_t_list)))

    resultados = pd.DataFrame(columns=['Edad', 'x+t'])
    resultados['x+t'] = x_mas_t_list
    resultados['Edad'] = edad_t

    qx_ajustado = []
    for i in range(edad_inicio, omega + 1):
        if i in df.index:
            qx_ajustado.append(q_x(df.loc[i, 'qx'], df.loc[i, 'mejora'], i - edad_inicio))
        else:
            qx_ajustado.append(1.0)  # Forzar qx = 1 para edades fuera de la tabla

    resultados.insert(2, 'qx+t ajustado', qx_ajustado)
    resultados.set_index('Edad', inplace=True)

    resultados['lx'] = 0.0
    resultados.loc[0, 'lx'] = 1000000.0  # Suponemos 1,000,000 de asegurados al inicio

    for i in range(1, len(resultados)):
        resultados.loc[i, 'lx'] = resultados.loc[i-1, 'lx'] * (1 - resultados.loc[i-1, 'qx+t ajustado'])

    resultados['dx'] = resultados['lx'] * resultados['qx+t ajustado']
    
    print("Tabla generacional generada:")
    print(resultados.head(10))
    print(resultados.tail(10))
    
    return resultados

    
def interpolar_lx_fraccionada_completa(tabla_anual, edad_inicio, duracion, fracciones_por_anio=12):
    resultados = []
    max_edad = tabla_anual['x+t'].max()
    for k_offset in range(duracion + 1):
        edad = edad_inicio + k_offset
        if edad > max_edad:
            break
        # Si edad + 1 no está en la tabla, asumir lx = 0 para edad + 1
        if edad + 1 > max_edad:
            lx_k1 = 0
        else:
            lx_k1 = tabla_anual.loc[tabla_anual['x+t'] == edad + 1, 'lx'].values[0]
        for j in range(fracciones_por_anio):
            fraccion = j / fracciones_por_anio
            lx_k = tabla_anual.loc[tabla_anual['x+t'] == edad, 'lx'].values[0]
            lx_interp = lx_k - (lx_k1 - lx_k) * fraccion
            resultados.append({'k': edad, 'j': j, 'l_{x+k+j/fracciones}': lx_interp})
    return pd.DataFrame(resultados)

def funcion_intereses(intereses, saltos=None, edad_renta=None, tabla_generacion=None, duracion=None):
    """
    Devuelve una lista con los intereses del período.
    Args:
        intereses: Lista de tasas de interés (para interés variable) o un solo float (para interés fijo).
        saltos: Lista de años donde cambian las tasas (requerido si intereses es una lista).
        edad_renta: Edad inicial de la renta (para calcular duración si no se proporciona).
        tabla_generacion: Tabla de mortalidad (para calcular duración si no se proporciona).
        duracion: Duración de la renta (opcional, si no se proporciona se calcula).
    Returns:
        Lista de tasas de interés: [0, i_1, i_2, ..., i_duracion]
    Ejemplo:
        funcion_intereses([0.02, 0.04, 0.05], [2, 5, 6], duracion=6) -> [0, 0.02, 0.02, 0.04, 0.04, 0.04, 0.05]
        funcion_intereses(0.0275, duracion=6) -> [0, 0.0275, 0.0275, 0.0275, 0.0275, 0.0275, 0.0275]
    """
    # Calcular duración si no se proporciona
    if duracion is None:
        if edad_renta is None or tabla_generacion is None:
            raise ValueError("Se requiere edad_renta y tabla_generacion si duracion no está definida.")
        duracion = int(tabla_generacion["x+t"].iloc[-1]) - edad_renta - 1

    # Caso de interés fijo
    if isinstance(intereses, (int, float)):
        total_intereses = [intereses] * duracion
        total_intereses.insert(0, 0)
        return total_intereses

    # Caso de interés variable
    if saltos is None:
        raise ValueError("Se requiere la lista de saltos para tasas de interés variables.")
    
    # Validaciones
    if len(intereses) != len(saltos):
        raise ValueError("Las listas intereses y saltos deben tener la misma longitud.")
    if not all(s1 < s2 for s1, s2 in zip(saltos[:-1], saltos[1:])):
        raise ValueError("Los saltos deben estar en orden ascendente.")
    if saltos[-1] < duracion:
        raise ValueError(f"Faltan años por determinar: el último salto ({saltos[-1]}) es menor que la duración ({duracion}).")

    total_intereses = []
    inicio = 0
    for i in range(len(intereses)):
        fin = saltos[i]
        interes = intereses[i]
        total_intereses.extend([interes] * (fin - inicio))
        inicio = fin
    total_intereses.insert(0, 0)

    return total_intereses

def v(lista_intereses, t, fracciones_por_anio=1):
    """
    Calcula el factor de descuento para una lista de tasas de interés y un tiempo t (en años fraccionarios).
    Args:
        lista_intereses (list): Lista de tasas de interés por año (índice 0 es 0, índice 1 es año 1, etc.).
        t (float): Tiempo en años (puede ser fraccionario).
        fracciones_por_anio (int): Número de fracciones por año (default=1).
    Returns:
        float: Factor de descuento acumulado.
    """
    if not isinstance(t, (int, float)) or t < 0:
        raise ValueError("t debe ser un número no negativo.")
    if not lista_intereses:
        raise ValueError("La lista de intereses no puede estar vacía.")
    
    if t == 0:
        return 1.0
    
    # Convertir t a fracciones
    t_fracciones = t * fracciones_por_anio
    producto = 1.0
    
    # Acumular descuentos por cada año completo
    for k in range(1, int(t) + 1):
        if k >= len(lista_intereses):
            i_k = lista_intereses[-1]
        else:
            i_k = lista_intereses[k]
        if i_k < -1:
            raise ValueError(f"Tasa de interés inválida en k={k}: {i_k}. No puede ser menor a -1.")
        producto *= (1 + i_k) ** (-1)
    
    # Ajustar por la fracción del último año
    k_final = int(t)
    fraccion = t - k_final
    if fraccion > 0 and k_final < len(lista_intereses):
        i_k = lista_intereses[k_final + 1] if k_final + 1 < len(lista_intereses) else lista_intereses[-1]
        producto *= (1 + i_k) ** (-fraccion)
    
    return producto

def tpx(x, t=1, tabla_generacion=None, fracciones_por_anio=12):
    if tabla_generacion is None:
        raise ValueError("Se requiere una tabla generacional.")
    t_fracciones = int(t * fracciones_por_anio)
    fraccion_final = t_fracciones % fracciones_por_anio
    edad_final = x + (t_fracciones // fracciones_por_anio)
    l_x = None
    l_x_mas_t = None
    for i in tabla_generacion.index:
        if tabla_generacion.loc[i, 'k'] == x and tabla_generacion.loc[i, 'j'] == 0:
            l_x = tabla_generacion.loc[i, 'l_{x+k+j/fracciones}']
            break
    for i in tabla_generacion.index:
        if tabla_generacion.loc[i, 'k'] == edad_final and tabla_generacion.loc[i, 'j'] == fraccion_final:
            l_x_mas_t = tabla_generacion.loc[i, 'l_{x+k+j/fracciones}']
            break
    if l_x is None or l_x_mas_t is None:
        raise ValueError(f"Edad x={x} o x+t={x+t} no encontrada en la tabla de mortalidad")
    return l_x_mas_t / l_x

def geometrica(tipo_renta, k, q, diferimiento=None):
    """
    Calcula el factor de ajuste geométrico para el capital en una renta actuarial.
    
    Args:
        tipo_renta (str): Tipo de renta ("prepagable" o "pospagable").
        k (int): Período para el cual se calcula el factor de ajuste.
        q (float): Factor de crecimiento geométrico (q = 1 + g, donde g es la tasa de crecimiento).
        diferimiento (int or None): Período de diferimiento (None si no hay diferimiento).
    
    Returns:
        float: Factor de ajuste geométrico.
    """
    if q is None:
        return 1
    
    k = int(k)
    q = float(q)
    if tipo_renta == "prepagable":
        if diferimiento is None:
            cap = (q**k)
        else:
            diferimiento = int(diferimiento)
            cap = q**(k-diferimiento)
    elif tipo_renta == "pospagable":
        if diferimiento is None:
            cap = q**(k - 1)
        else:
            diferimiento = int(diferimiento)
            cap = q**(k-diferimiento - 1)
    return cap

def aritmetica(capital, tipo_renta, k, h, diferimiento=None):
    """
    Versión corregida pero con la misma estructura original
    """
    if diferimiento is None:
        diferimiento = 0
    
    # Cálculo del período ajustado
    if tipo_renta == "prepagable":
        periodo_ajustado = k - diferimiento
    else:  # pospagable
        periodo_ajustado = k - diferimiento - 1
    
    # Asegurarnos que no aplicamos incrementos antes del primer pago
    if periodo_ajustado < 0:
        return 0.0
    
    return capital + periodo_ajustado * h

def renta(tipo_renta, edad_renta, capital, temporalidad, diferimiento, lista_intereses=None, interes=None,
          tabla_generacion=None, tipo_ajuste=None, factor_q=None, incremento_h=None, fracciones_por_anio=12):
   
    # Validaciones
    if tabla_generacion is None:
        raise ValueError("Se requiere una tabla generacional.")
    if tipo_renta not in ["prepagable", "pospagable"]:
        raise ValueError("Tipo de renta debe ser 'prepagable' o 'pospagable'.")
    if (interes is None and lista_intereses is None) or (interes is not None and lista_intereses is not None):
        raise ValueError("Debe proporcionarse exactamente uno de interes o lista_intereses.")
    
    # Determinar la duración máxima en fracciones
    if temporalidad is None:
        w_menosx = int(tabla_generacion["x+t"].iloc[-1]) - edad_renta
        total_fracciones = w_menosx * fracciones_por_anio
    else:
        total_fracciones = int(temporalidad * fracciones_por_anio)

    # Si se proporciona una tasa fija, generar una lista de tasas constantes
    if interes is not None:
        duracion_anios = total_fracciones // fracciones_por_anio + 1
        lista_intereses = [0] + [interes] * duracion_anios

    if lista_intereses is None or len(lista_intereses) < 2:
        raise ValueError("lista_intereses no puede ser None o demasiado corta.")

    # Interpolar la tabla generacional para todas las fracciones necesarias
    tabla_fraccionada = interpolar_lx_fraccionada_completa(tabla_generacion, edad_renta, w_menosx if temporalidad is None else temporalidad, fracciones_por_anio)

    # Preparar la tabla de flujos
    tabla_flujos = pd.DataFrame(columns=['k', 'v^k', 'k p_x', 'v^k * k p_x', 'C * k p_x'])

    sumatorio = 0.0
    if tipo_renta == "prepagable":
        if diferimiento is None:  # Renta prepagable, inmediata
            if temporalidad is None:  # Vitalicia
                for f in range(total_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f] = [t_anios, vk, val_medio, val_medio * vk, flujo]
            else:  # Temporal
                for f in range(total_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f] = [t_anios, vk, val_medio, val_medio * vk, flujo]
        else:  # Renta prepagable, diferida
            diferimiento_fracciones = int(diferimiento * fracciones_por_anio)
            if temporalidad is None:  # Vitalicia
                for f in range(diferimiento_fracciones, total_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q, diferimiento)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h, diferimiento)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f] = [t_anios, vk, val_medio, val_medio * vk, flujo]
            else:  # Temporal
                for f in range(diferimiento_fracciones, total_fracciones + diferimiento_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q, diferimiento)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h, diferimiento)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f] = [t_anios, vk, val_medio, val_medio * vk, flujo]
    
    elif tipo_renta == "pospagable":
        if diferimiento is None:  # Renta pospagable, inmediata
            if temporalidad is None:  # Vitalicia
                for f in range(1, total_fracciones):  # Pospagable comienza en f=1
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f-1] = [t_anios, vk, val_medio, val_medio * vk, flujo]
            else:  # Temporal
                for f in range(1, total_fracciones + 1):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f-1] = [t_anios, vk, val_medio, val_medio * vk, flujo]
        else:  # Renta pospagable, diferida
            diferimiento_fracciones = int(diferimiento * fracciones_por_anio)
            if temporalidad is None:  # Vitalicia
                for f in range(diferimiento_fracciones + 1, total_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q, diferimiento)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h, diferimiento)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f-1] = [t_anios, vk, val_medio, val_medio * vk, flujo]
            else:  # Temporal
                for f in range(diferimiento_fracciones + 1, total_fracciones + diferimiento_fracciones + 1):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q, diferimiento)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h, diferimiento)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f-1] = [t_anios, vk, val_medio, val_medio * vk, flujo]

    # Ajuste para rentas prepagables
    if tipo_renta.lower() == "prepagable":
        ajuste_prepagable = (1 + lista_intereses[1]) ** (1 / fracciones_por_anio) if len(lista_intereses) > 1 else (1 + interes) ** (1 / fracciones_por_anio)
        sumatorio = sumatorio * ajuste_prepagable

    # Asegurarse de que 'k' sea float (representa años fraccionarios)
    tabla_flujos['k'] = tabla_flujos['k'].astype(float)
    print("Valores devueltos por renta:", sumatorio, sumatorio * capital, tabla_flujos)
    return sumatorio, sumatorio * capital, tabla_flujos

#NUEVAS FUNCIONES PARA MANEJAR LOS INCREMENTOS ARITMETICOS Y GEOMETRICOS VARIABLES 

def funcion_incrementos_aritmeticos_variables(incrementos, saltos_incrementos, temporalidad=None, diferimiento=0):
    """
    Genera una lista de incrementos aritméticos (h_t) para cada año t.
    - incrementos: Lista de cantidades a sumar (ej. [1000, 500] €).
    - saltos_incrementos: Años donde cambian los incrementos (ej. [5]).
    - temporalidad: Duración de la renta en años (None para vitalicia).
    - diferimiento: Años antes de que comience la renta.
    Retorna: Lista de h_t desde t=0.
    """
    lista_ht = [0.0] * diferimiento  # h_t = 0 durante diferimiento
    t_actual = diferimiento
    max_anios = temporalidad + diferimiento if temporalidad is not None else 100 + diferimiento
    max_anios = int(max_anios) + 1

    for i, salto in enumerate(saltos_incrementos):
        if i >= len(incrementos):
            raise ValueError("Faltan incrementos para los saltos proporcionados.")
        salto_absoluto = salto + diferimiento
        for t in range(t_actual, min(salto_absoluto, max_anios)):
            lista_ht.append(incrementos[i])  # h_t = incremento en €
        t_actual = salto_absoluto
        if t_actual >= max_anios:
            break

    # Completar con el último incremento
    if t_actual < max_anios:
        if not incrementos:
            raise ValueError("No hay incrementos para completar los años restantes.")
        for t in range(t_actual, max_anios):
            lista_ht.append(incrementos[-1])

    return lista_ht

def funcion_incrementos_variables(incrementos, saltos_incrementos, temporalidad=None, diferimiento=0):
    lista_qt = [1.0] * diferimiento
    t_actual = diferimiento
    max_anios = temporalidad + diferimiento if temporalidad is not None else 100 + diferimiento
    max_anios = int(max_anios) + 1

    for i, salto in enumerate(saltos_incrementos):
        if i >= len(incrementos):
            raise ValueError("Faltan incrementos para los saltos proporcionados.")
        salto_absoluto = salto + diferimiento
        for t in range(t_actual, min(salto_absoluto, max_anios)):
            lista_qt.append(1 + incrementos[i])
        t_actual = salto_absoluto
        if t_actual >= max_anios:
            break

    if t_actual < max_anios:
        if not incrementos:
            raise ValueError("No hay incrementos para completar los años restantes.")
        for t in range(t_actual, max_anios):
            lista_qt.append(1 + incrementos[-1])

    return lista_qt

def interpolar_lx_general(tabla_anual, edad_renta, diferimiento, duracion, fracciones_por_anio=1):
    """
    Interpola lx para fracciones de año y calcula k p_x para rentas con o sin diferimiento.
    
    Args:
        tabla_anual (pd.DataFrame): Tabla generacional con columnas 'x+t', 'lx'.
        edad_renta (int): Edad inicial para calcular k p_x.
        diferimiento (int): Años de diferimiento (0 si renta inmediata).
        duracion (int): Número de años a interpolar.
        fracciones_por_anio (int): Fracciones por año (1, 4, 12, etc.).
    
    Returns:
        pd.DataFrame: Tabla con columnas k (edad absoluta), t (tiempo desde edad_renta), k p_x.
    """
    resultados = []
    max_edad = tabla_anual['x+t'].max()
    
    # Edad donde comienzan los pagos
    edad_inicio = edad_renta + diferimiento
    
    # Obtener lx inicial para edad_renta
    if edad_renta not in tabla_anual['x+t'].values:
        raise ValueError(f"La edad inicial {edad_renta} no está en la tabla generacional.")
    lx_inicial = tabla_anual.loc[tabla_anual['x+t'] == edad_renta, 'lx'].iloc[0]
    
    # Generar tabla para cada año y fracción
    for k_offset in range(duracion + 1):
        edad = edad_inicio + k_offset
        t = edad - edad_renta  # Tiempo transcurrido desde edad_renta
        
        # Obtener lx para la edad actual
        if edad > max_edad:
            lx = 0
        else:
            lx = tabla_anual.loc[tabla_anual['x+t'] == edad, 'lx'].values[0]
        
        # Obtener lx para la siguiente edad
        if edad + 1 > max_edad:
            lx_next = 0
        else:
            lx_next = tabla_anual.loc[tabla_anual['x+t'] == edad + 1, 'lx'].values[0]
        
        # Interpolación para cada fracción
        for j in range(fracciones_por_anio):
            fraccion = j / fracciones_por_anio
            lx_interp = lx + (lx_next - lx) * fraccion
            k_p_x = lx_interp / lx_inicial if lx_inicial != 0 else 0
            
            resultados.append({
                'k': edad + fraccion,  # Edad absoluta
                't': t + fraccion,     # Tiempo desde edad_renta
                'k p_x': k_p_x
            })
    
    tabla = pd.DataFrame(resultados)
    print("Valores de tabla interpolada:")
    print(tabla.head(10))
    print(tabla.tail(10))
    return tabla
#Se crea una función que:
#Calcule k p_x directamente desde lx de la tabla generacional. Ajuste k según el tipo de renta (pospagable/prepagable, con/sin diferimiento).
#Mantenga el cálculo de C_t con incrementos variables.
    
# En backend.py
def generar_tabla_flujos(tabla_anual, edad_renta, diferimiento, tipo_renta, duracion=None, fracciones_por_anio=1):
    """Versión corregida que genera exactamente N fracciones completas"""
    # Validaciones iniciales
    if not isinstance(tabla_anual, pd.DataFrame):
        raise ValueError("tabla_anual debe ser un DataFrame")
    if 'x+t' not in tabla_anual.columns or 'lx' not in tabla_anual.columns:
        raise ValueError("tabla_anual debe contener columnas 'x+t' y 'lx'")
    
    resultados = []
    lx_dict = {int(edad): lx for edad, lx in zip(tabla_anual['x+t'], tabla_anual['lx'])}
    lx_inicial = lx_dict.get(edad_renta, 0)
    
    if lx_inicial == 0:
        raise ValueError(f"Edad inicial {edad_renta} no encontrada en tabla generacional")
    
    max_edad = max(lx_dict.keys())
    max_k = (diferimiento + duracion) if duracion else (max_edad - edad_renta)
    
    # Configuración de fracciones
    es_pospagable = tipo_renta.lower() == 'pospagable'
    
    for k_entero in range(diferimiento, max_k):
        edad_base = edad_renta + k_entero
        
        if fracciones_por_anio == 1:
            # Caso anual
            lx_k = lx_dict.get(edad_base, 0)
            resultados.append({
                'k': k_entero,
                't': k_entero,
                'k p_x': lx_k / lx_inicial,
                'edad': edad_base,
                'k_entero': k_entero,
                'j_fraccion': 0,
                'lx': lx_k
            })
        else:
            # Caso fraccionado - CORRECCIÓN DEFINITIVA
            for j in range(fracciones_por_anio):
                # Ajuste clave para pospagable
                j_ajustado = j + 1 if es_pospagable else j
                fraccion = j_ajustado / fracciones_por_anio
                
                edad_fracc = edad_base + fraccion
                edad_floor = math.floor(edad_fracc)
                edad_ceil = math.ceil(edad_fracc)
                
                lx_interp = lx_dict.get(edad_floor, 0) + (lx_dict.get(edad_ceil, 0) - lx_dict.get(edad_floor, 0)) * (edad_fracc - edad_floor)
                
                resultados.append({
                    'k': round(k_entero + fraccion, 8),
                    't': round(k_entero + fraccion, 8),
                    'k p_x': lx_interp / lx_inicial,
                    'edad': edad_fracc,
                    'k_entero': k_entero,
                    'j_fraccion': j_ajustado,  # Usamos el j ajustado
                    'lx': lx_interp
                })
    
    return pd.DataFrame(resultados).dropna()

def calcular_factor_descuento(k, tipo_renta, interes, lista_intereses=None, t=None, fracciones_por_anio=1):
    """
    Calcula EXACTAMENTE v^k según el tipo de renta y la columna k o t.
    
    Args:
        k: Valor de k (período).
        tipo_renta: 'prepagable' o 'pospagable'.
        interes: Tasa de interés anual fija (si no hay lista_intereses).
        lista_intereses: Lista de tasas variables (opcional).
        t: Tiempo desde el inicio (para tasas variables).
        fracciones_por_anio: Número de fracciones por año (default=1).
    
    Returns:
        Factor de descuento v^k
    """
    if t is None:
        t = k
    
    # Calcular v^k usando la función v
    if lista_intereses is not None:
        vk = v(lista_intereses, t, fracciones_por_anio)
    else:
        vk = (1 + interes) ** (-t)
    
    return vk

def renta_geometrica(tipo_renta, edad_renta, capital, temporalidad, diferimiento, 
                    interes=None, lista_intereses=None, tabla_generacion=None, 
                    lista_factores=None, saltos_factores=None, fracciones_por_anio=1):
    """
    Calcula rentas con progresión geométrica (porcentual)
    
    Args:
        lista_factores: Lista de factores de crecimiento (1 + tasa)
        saltos_factores: Años donde cambian los factores (para tasas variables)
    """
    # Validaciones iniciales
    if lista_intereses is None and interes is None:
        raise ValueError("Debe proporcionar una tasa de interés fija o variable.")
    if tabla_generacion is None:
        raise ValueError("Debe proporcionar una tabla generacional.")
    
    # Configuración básica
    omega = 120
    diferimiento = 0 if diferimiento is None else int(diferimiento)
    max_anios = temporalidad if temporalidad is not None else (omega - edad_renta - diferimiento)
    max_anios = int(max_anios)
    
    # Si se proporciona una tasa fija, generar una lista de tasas constantes
    if interes is not None:
        lista_intereses = [0] + [interes] * (max_anios + 1)

    # Generar tabla de flujos base
    tabla = generar_tabla_flujos(tabla_generacion, edad_renta, diferimiento, tipo_renta, max_anios, fracciones_por_anio)
    tabla_flujos = tabla.copy()
    
    # 1. Cálculo de C_k (capitales con incremento geométrico)
    C_k = []
    factores_completos = [1.0] * (max_anios * fracciones_por_anio)
    
    if lista_factores and saltos_factores:
        t_actual = 0
        for i, salto in enumerate(saltos_factores):
            if i >= len(lista_factores):
                break
            fin = salto * fracciones_por_anio
            factores_completos[t_actual:fin] = [lista_factores[i]] * (fin - t_actual)
            t_actual = fin
        factores_completos[t_actual:] = [lista_factores[-1]] * (len(factores_completos) - t_actual)
    
    for idx, row in tabla.iterrows():
        t = row['t']
        k = row['k']
        
        if tipo_renta.lower() == 'pospagable':
            en_periodo_pago = t >= (diferimiento + 1/fracciones_por_anio)
            periodo_efectivo = int((t - diferimiento - 1) * fracciones_por_anio)
        else:  # prepagable
            en_periodo_pago = t >= diferimiento
            periodo_efectivo = int((t - diferimiento) * fracciones_por_anio)
        
        if not en_periodo_pago:
            C_k.append(0.0)
            continue
            
        if lista_factores:
            if saltos_factores:
                factor = math.prod(factores_completos[:max(0, periodo_efectivo)])
            else:
                factor = lista_factores[0] ** periodo_efectivo
            C_k.append(capital * factor)
        else:
            C_k.append(capital)
    
    tabla_flujos['C_k'] = C_k

    # 2. Cálculo de v^k
    tabla_flujos['v^k'] = [
        calcular_factor_descuento(
            k=row['k'],
            tipo_renta=tipo_renta,
            interes=interes,
            lista_intereses=lista_intereses,
            t=row['t'],
            fracciones_por_anio=fracciones_por_anio
        )
        for _, row in tabla_flujos.iterrows()
    ]
    
    # 3. Cálculo de flujos descontados
    tabla_flujos['k p_x * C_k * v^k'] = tabla_flujos['k p_x'] * tabla_flujos['C_k'] * tabla_flujos['v^k']
    
    # 4. Sumatorio final
    sumatorio = tabla_flujos['k p_x * C_k * v^k'].sum()
    if fracciones_por_anio > 1:
        sumatorio /= fracciones_por_anio
    
    # Ajuste para rentas prepagables
    if tipo_renta.lower() == "prepagable":
        ajuste_prepagable = (1 + lista_intereses[1]) ** (1 / fracciones_por_anio) if len(lista_intereses) > 1 else (1 + interes) ** (1 / fracciones_por_anio)
        sumatorio = sumatorio * ajuste_prepagable

    valor_renta = sumatorio

    return sumatorio, valor_renta, tabla_flujos[['k', 'k p_x', 'C_k', 'v^k', 'k p_x * C_k * v^k']]

#OTRA NUEVA FUNCION,ESTAMOS LLENO DE FUNCIONES 
def renta_aritmetica(tipo_renta, edad_renta, capital, temporalidad, diferimiento,
                    interes=None, lista_intereses=None, tabla_generacion=None,
                    incremento_fijo=None, lista_incrementos=None, saltos_incrementos=None,
                    fracciones_por_anio=1):
    """
    Calcula rentas con progresión aritmética (fija o variable)
    
    Args:
        incremento_fijo: Cantidad fija de incremento por período (para progresión fija)
        lista_incrementos: Lista de incrementos variables
        saltos_incrementos: Años donde cambian los incrementos (para progresión variable)
    """
    
    # Validaciones iniciales
    if lista_intereses is None and interes is None:
        raise ValueError("Debe proporcionar una tasa de interés fija o variable.")
    if tabla_generacion is None:
        raise ValueError("Debe proporcionar una tabla generacional.")
    if incremento_fijo is not None and lista_incrementos is not None:
        raise ValueError("Use sólo incremento_fijo o lista_incrementos, no ambos.")

    # Configuración básica
    omega = 120
    diferimiento = 0 if diferimiento is None else int(diferimiento)
    max_anios = temporalidad if temporalidad is not None else (omega - edad_renta - diferimiento)
    max_anios = int(max_anios)
    
    # Si se proporciona una tasa fija, generar una lista de tasas constantes
    if interes is not None:
        lista_intereses = [0] + [interes] * (max_anios + 1)

    # Generar tabla de flujos base
    tabla = generar_tabla_flujos(tabla_generacion, edad_renta, diferimiento, tipo_renta, max_anios, fracciones_por_anio)
    
    # Preparar tabla de resultados
    tabla_flujos = tabla.copy()
    
    # 1. Cálculo de C_k (capitales con incremento aritmético)
    C_k = []
    
    # Progresión aritmética fija
    if incremento_fijo is not None:
        for t in tabla['t']:
            if tipo_renta.lower() == 'pospagable':
                if t < (diferimiento + 1):
                    C_k.append(0.0)
                else:
                    num_pagos = int((t - diferimiento - 1) * fracciones_por_anio) + 1
                    C_k.append(capital + (num_pagos - 1) * incremento_fijo)
            else:  # prepagable
                if t < diferimiento:
                    C_k.append(0.0)
                else:
                    num_pagos = int((t - diferimiento) * fracciones_por_anio) + 1
                    C_k.append(capital + (num_pagos - 1) * incremento_fijo)
    
    # Progresión aritmética variable
    elif lista_incrementos is not None:
        if saltos_incrementos is None:
            saltos_incrementos = []
        
        lista_ht = []
        t_actual = 0
        for i, salto in enumerate(saltos_incrementos):
            if i >= len(lista_incrementos):
                break
            lista_ht += [lista_incrementos[i]] * (salto - t_actual)
            t_actual = salto
        lista_ht += [lista_incrementos[-1]] * (max_anios - t_actual)
        
        acumulado = 0
        for t in tabla['t']:
            if tipo_renta.lower() == 'pospagable':
                if t < (diferimiento + 1):
                    C_k.append(0.0)
                else:
                    periodo = int((t - diferimiento - 1) * fracciones_por_anio)
                    if periodo < 0:
                        C_k.append(0.0)
                    else:
                        if periodo == 0:
                            C_k.append(capital)
                        else:
                            idx = min(periodo - 1, len(lista_ht) - 1)
                            acumulado = sum(lista_ht[:idx + 1])
                            C_k.append(capital + acumulado)
            else:  # prepagable
                if t < diferimiento:
                    C_k.append(0.0)
                else:
                    periodo = int((t - diferimiento) * fracciones_por_anio)
                    if periodo == 0:
                        C_k.append(capital)
                    else:
                        idx = min(periodo - 1, len(lista_ht) - 1)
                        acumulado = sum(lista_ht[:idx + 1])
                        C_k.append(capital + acumulado)
    
    tabla_flujos['C_k'] = C_k

    # 2. Cálculo de factores de descuento (v^k)
    tabla_flujos['v^k'] = [
        calcular_factor_descuento(
            k=row['k'],
            tipo_renta=tipo_renta,
            interes=interes,
            lista_intereses=lista_intereses,
            t=row['t'],
            fracciones_por_anio=fracciones_por_anio
        )
        for _, row in tabla_flujos.iterrows()
    ]
    
    # 3. Cálculo de flujos descontados
    tabla_flujos['k p_x * C_k * v^k'] = tabla_flujos['k p_x'] * tabla_flujos['C_k'] * tabla_flujos['v^k']
    
    # 4. Sumatorio final
    sumatorio = tabla_flujos['k p_x * C_k * v^k'].sum()
    if fracciones_por_anio > 1:
        sumatorio /= fracciones_por_anio
    
    # Ajuste para rentas prepagables
    if tipo_renta.lower() == "prepagable":
        ajuste_prepagable = (1 + lista_intereses[1]) ** (1 / fracciones_por_anio) if len(lista_intereses) > 1 else (1 + interes) ** (1 / fracciones_por_anio)
        sumatorio = sumatorio * ajuste_prepagable

    return sumatorio, tabla_flujos['k p_x * C_k * v^k'].sum(), tabla_flujos[['k', 'k p_x', 'C_k', 'v^k', 'k p_x * C_k * v^k']]

def calcular_renta_fraccionada(tabla_flujos, tipo_renta, capital, factores, fracciones_por_anio):
    """Versión con validación de tipos y soporte para incrementos variables"""
    if None in [capital, fracciones_por_anio]:
        raise ValueError("Parámetros inválidos: capital o fracciones no pueden ser None")
    if 'interes' not in factores and 'lista_intereses' not in factores:
        raise ValueError("Debe proporcionarse una tasa de interés fija o variable")

    # Generar lista_intereses a partir de factores['interes'] si es fijo
    lista_intereses = factores.get('lista_intereses')
    if lista_intereses is None:
        max_t = int(tabla_flujos['t'].max()) + 1
        lista_intereses = [0] + [factores['interes']] * max_t

    tabla = tabla_flujos.copy()
    
    # 1. Cálculo de C_k con validación
    try:
        if factores['tipo'] == 'geometrico':
            if 'q' in factores:
                # Caso de incremento geométrico fijo
                tabla['C_k'] = capital * (factores['q'] ** tabla['t'])
            elif 'lista_factores' in factores and 'saltos_factores' in factores:
                # Caso de incremento geométrico variable
                C_k = []
                lista_factores = factores['lista_factores']
                saltos_factores = factores['saltos_factores']
                
                # Generar lista completa de factores por año
                factores_completos = []
                t_actual = 0
                for i, salto in enumerate(saltos_factores):
                    if i >= len(lista_factores):
                        break
                    factores_completos.extend([lista_factores[i]] * (salto - t_actual))
                    t_actual = salto
                factores_completos.extend([lista_factores[-1]] * (int(tabla['t'].max()) + 1 - t_actual))
                
                # Calcular C_k acumulando los factores
                for t in tabla['t']:
                    k_entero = int(t)
                    if k_entero == 0:
                        C_k.append(capital)
                    else:
                        factor_acumulado = math.prod(factores_completos[:k_entero])
                        C_k.append(capital * factor_acumulado)
                tabla['C_k'] = C_k
            else:
                raise ValueError("Para tipo 'geometrico', se requiere 'q' o 'lista_factores' con 'saltos_factores'")
        elif factores['tipo'] == 'aritmetico':
            if 'h' in factores:
                # Caso de incremento aritmético fijo
                tabla['C_k'] = capital + (tabla['t'] * factores['h'])
            elif 'lista_incrementos' in factores and 'saltos_incrementos' in factores:
                # Caso de incremento aritmético variable
                lista_incrementos = factores['lista_incrementos']
                saltos_incrementos = factores['saltos_incrementos']
                
                # Generar lista completa de incrementos por año
                incrementos_completos = []
                t_actual = 0
                for i, salto in enumerate(saltos_incrementos):
                    if i >= len(lista_incrementos):
                        break
                    incrementos_completos.extend([lista_incrementos[i]] * (salto - t_actual))
                    t_actual = salto
                incrementos_completos.extend([lista_incrementos[-1]] * (int(tabla['t'].max()) + 1 - t_actual))
                
                # Calcular C_k acumulando los incrementos
                C_k = []
                for t in tabla['t']:
                    k_entero = int(t)
                    if k_entero == 0:
                        C_k.append(capital)
                    else:
                        incremento_acumulado = sum(incrementos_completos[:k_entero])
                        C_k.append(capital + incremento_acumulado)
                tabla['C_k'] = C_k
            else:
                raise ValueError("Para tipo 'aritmetico', se requiere 'h' o 'lista_incrementos' con 'saltos_incrementos'")
        else:
            tabla['C_k'] = capital  # Sin incrementos
    except TypeError as e:
        raise ValueError(f"Error en factores de incremento: {str(e)}")

    # 2. Validar que k p_x no contenga None
    if tabla['k p_x'].isnull().any():
        raise ValueError("La tabla contiene valores None en 'k p_x'")

    # 3. Calcular v^k
    tabla['v^k'] = tabla['t'].apply(lambda t: v(lista_intereses, t, fracciones_por_anio))
    
    # 4. Calcular valor actual
    tabla['valor_actual'] = (tabla['C_k'] / fracciones_por_anio) * tabla['k p_x'] * tabla['v^k']
    
    # 5. Ajuste para rentas prepagables
    sumatorio = tabla['valor_actual'].sum()
    if tipo_renta.lower() == "prepagable":
        ajuste_prepagable = (1 + lista_intereses[1]) ** (1 / fracciones_por_anio) if len(lista_intereses) > 1 else (1 + factores.get('interes', 0)) ** (1 / fracciones_por_anio)
        sumatorio = sumatorio * ajuste_prepagable
    
    tabla['valor_actual'] = tabla['valor_actual'] * ajuste_prepagable if tipo_renta.lower() == "prepagable" else tabla['valor_actual']
    
    return tabla