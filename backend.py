# backend.py
import pandas as pd
import numpy as np
import math

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

    # Renombrar columnas según el tipo de tabla
    if len(df.columns) == 2:  # Tablas PERM2000/PERF2000
        df.columns = ['qx', 'mejora']
    elif len(df.columns) == 4:  # Tablas PERM_2020/PERF_2020
        # Asumimos que las columnas son: 'qx+t, tabla base', 'qx+t, 1er orden', 'qx+t, 2do orden', 'λx+t'
        # Usamos 'qx+t, 2do orden' como qx y 'λx+t' como mejora
        df = df.iloc[:, [2, 3]]  # Seleccionamos solo las columnas 2 y 3
        df.columns = ['qx', 'mejora']
    else:
        raise ValueError(f"La tabla {nombre_tabla} tiene un número inesperado de columnas: {len(df.columns)}")

    df.index.name = 'edad'

    # Generar la tabla generacional
    x_mas_t_list = list(range(edad_inicio, len(df))) 
    edad_t = list(range(0, len(x_mas_t_list)))

    resultados = pd.DataFrame(columns=['Edad', 'x+t'])
    resultados['x+t'] = x_mas_t_list
    resultados['Edad'] = edad_t

    qx_ajustado = []
    for i in range(edad_inicio, len(df)):
        qx_ajustado.append(q_x(df.loc[i, 'qx'], df.loc[i, 'mejora'], i - edad_inicio))

    resultados.insert(2, 'qx+t ajustado', qx_ajustado)
    resultados.set_index('Edad', inplace=True)

    resultados['lx'] = 0.0
    resultados.loc[0, 'lx'] = 1000000.0  # Suponemos 1,000,000 de asegurados al inicio

    for i in range(1, len(resultados)):
        resultados.loc[i, 'lx'] = resultados.loc[i-1, 'lx'] * (1 - resultados.loc[i-1, 'qx+t ajustado'])

    resultados['dx'] = resultados['lx'] * resultados['qx+t ajustado']
             
    return resultados

def interpolar_lx_mensual(tabla_anual, edad_inicio):
    """
    Interpola los valores de lx mensualmente a partir de la tabla anual.

    Args:
        tabla_anual (pd.DataFrame): Tabla generacional anual con columnas 'x+t', 'lx'.
        edad_inicio (int): Edad base desde la cual queremos interpolar.

    Returns:
        pd.DataFrame: Tabla con columnas k, j, l_{x+k+j/12}
    """
    resultados = []

    for j in range(12):  # j = 0 a 11 (meses)
        edad_entera = edad_inicio
        fraccion = j / 12

        # lx en la edad k y k+1
        lx_k = tabla_anual.loc[tabla_anual['x+t'] == edad_entera, 'lx'].values[0]
        lx_k1 = tabla_anual.loc[tabla_anual['x+t'] == edad_entera + 1, 'lx'].values[0]

        # Interpolación lineal mensual
        lx_interp = lx_k - (lx_k1 - lx_k) * fraccion

        resultados.append({'k': edad_inicio, 'j': j, 'l_{x+k+j/12}': round(lx_interp, 2)})

    return pd.DataFrame(resultados)

def interpolar_lx_fraccionada_completa(tabla_anual, edad_inicio, duracion, fracciones_por_anio=12):
    """
    Interpola los valores de lx en fracciones (mensuales, trimestrales, etc.) para todas las edades necesarias.
    
    Args:
        tabla_anual (pd.DataFrame): Tabla generacional anual con columnas 'x+t', 'lx'.
        edad_inicio (int): Edad base desde la cual queremos interpolar.
        duracion (int): Número de años a interpolar.
        fracciones_por_anio (int): Número de fracciones por año (1 para anual, 12 para mensual, etc.).
    
    Returns:
        pd.DataFrame: Tabla con columnas k, j, l_{x+k+j/fracciones}
    """
    resultados = []
    for k_offset in range(duracion + 1):  # Incluye el último año
        edad = edad_inicio + k_offset
        if edad + 1 not in tabla_anual['x+t'].values:
            break  # Si no hay datos para la siguiente edad, detener
        for j in range(fracciones_por_anio):  # j = 0 a fracciones_por_anio-1
            fraccion = j / fracciones_por_anio
            # lx en la edad k y k+1
            lx_k = tabla_anual.loc[tabla_anual['x+t'] == edad, 'lx'].values[0]
            lx_k1 = tabla_anual.loc[tabla_anual['x+t'] == edad + 1, 'lx'].values[0]
            # Interpolación lineal
            lx_interp = lx_k + (lx_k1 - lx_k) * fraccion
            resultados.append({'k': edad, 'j': j, 'l_{x+k+j/fracciones}': lx_interp})  # Sin redondeo
    return pd.DataFrame(resultados)

def funcion_intereses(intereses, saltos, edad_renta, tabla_generacion, duracion=None):
    """
    Devuelve una lista con los intereses del periodo, introduciendo como parámetros lista de intereses y lista de saltos.
    Ejemplo: funcion_intereses([0.02, 0.04, 0.05], [2, 5, 6], edad_renta, tabla_generacion, duracion=6)
             ---> [0, 0.02, 0.02, 0.04, 0.04, 0.04, 0.05]
    """
    if duracion is None:
        duracion = int(tabla_generacion["x+t"].iloc[-1]) - edad_renta - 1
    
    if saltos[-1] < duracion:
        raise ValueError("Faltan años por determinar")

    total_intereses = []
    inicio = 0
    for i in range(len(intereses)):
        fin = saltos[i]
        interes = intereses[i]
        total_intereses.extend([interes] * (fin - inicio))
        inicio = fin
    total_intereses.insert(0, 0) 

    return total_intereses

def v(lista_intereses, n):
    """
    Calcula el factor de descuento para una lista de tasas de interés y un período n.
    Args:
        lista_intereses (list): Lista de tasas de interés por año (índice 0 es 0, índice 1 es año 1, etc.).
        n (int): Número de años a descontar.
    Returns:
        float: Factor de descuento acumulado.
    """
    if n == 0:
        return 1.0
    producto = 1.0
    for k in range(1, n + 1):
        if k >= len(lista_intereses):
            # Si n excede la longitud de la lista, usar la última tasa
            i_k = lista_intereses[-1]
        else:
            i_k = lista_intereses[k]
        producto *= (1 + i_k) ** (-1)
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
    Calcula el capital ajustado aritméticamente para una renta actuarial.
    
    Args:
        capital (float): Capital inicial.
        tipo_renta (str): Tipo de renta ("prepagable" o "pospagable").
        k (int): Período para el cual se calcula el capital ajustado.
        h (float): Incremento aritmético por período.
        diferimiento (int or None): Período de diferimiento (None si no hay diferimiento).
    
    Returns:
        float: Capital ajustado.
    """
    k = int(k)
    h = float(h)
    capital = float(capital)
    if tipo_renta == "prepagable":
        if diferimiento is None:
            cap = capital + k * h
        else:
            diferimiento = int(diferimiento)
            cap = capital + (k-diferimiento) * h
    elif tipo_renta == "pospagable":
        if diferimiento is None:
            cap = capital + (k-1) * h    
        else: 
            diferimiento = int(diferimiento)
            cap = capital + (k - diferimiento - 1) * h
    return cap

def renta(tipo_renta, edad_renta, capital, temporalidad, diferimiento, lista_intereses=None, interes=None,
          tabla_generacion=None, tipo_ajuste=None, factor_q=None, incremento_h=None, fracciones_por_anio=12):
   
    # Validaciones
    if tabla_generacion is None:
        raise ValueError("Se requiere una tabla generacional.")
    if tipo_renta not in ["prepagable", "pospagable"]:
        raise ValueError("Tipo de renta debe ser 'prepagable' o 'pospagable'.")
    if (interes is None and lista_intereses is None) or (interes is not None and lista_intereses is not None):
        raise ValueError("Debe proporcionarse exactamente uno de interes o lista_intereses.")
    
    if interes is not None:
        duracion_anios = (temporalidad if temporalidad is not None else 100) + 1
        lista_intereses = [0] + [interes] * duracion_anios
    
    if lista_intereses is None or len(lista_intereses) < 2:
        raise ValueError("lista_intereses no puede ser None o demasiado corta.")

    # Determinar la duración máxima en fracciones
    if temporalidad is None:
        w_menosx = int(tabla_generacion["x+t"].iloc[-1]) - edad_renta
        total_fracciones = w_menosx * fracciones_por_anio
    else:
        total_fracciones = int(temporalidad * fracciones_por_anio)

    # Si se proporciona una tasa fija, generar una lista de tasas constantes
    if interes is not None:
        # Calcular la duración en años para generar la lista
        duracion_anios = total_fracciones // fracciones_por_anio + 1
        lista_intereses = [0] + [interes] * duracion_anios  # [0, interes, interes, ...]

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
                    if interes is not None:
                        vk = (1 + interes) ** (-t_anios)  # Tasa fija
                    else:
                        año_entero = f // fracciones_por_anio
                        i_k = lista_intereses[año_entero + 1] if año_entero + 1 < len(lista_intereses) else lista_intereses[-1]
                        vk = (1 + i_k) ** (-t_anios)  # Tasa variable por año
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
                    vk = (1 + interes) ** (-t_anios)
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
                    if interes is not None:
                        vk = (1 + interes) ** (-t_anios)
                    else:
                        año_entero = f // fracciones_por_anio
                        i_k = lista_intereses[año_entero + 1] if año_entero + 1 < len(lista_intereses) else lista_intereses[-1]
                        vk = (1 + i_k) ** (-t_anios)
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
                    if interes is not None:
                        vk = (1 + interes) ** (-t_anios)
                    else:
                        año_entero = f // fracciones_por_anio
                        i_k = lista_intereses[año_entero + 1] if año_entero + 1 < len(lista_intereses) else lista_intereses[-1]
                        vk = (1 + i_k) ** (-t_anios)
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
                for f in range(1, total_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    if interes is not None:
                        vk = (1 + interes) ** (-t_anios)
                    else:
                        año_entero = f // fracciones_por_anio
                        i_k = lista_intereses[año_entero + 1] if año_entero + 1 < len(lista_intereses) else lista_intereses[-1]
                        vk = (1 + i_k) ** (-t_anios)
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
                    if interes is not None:
                        vk = (1 + interes) ** (-t_anios)
                    else:
                        año_entero = f // fracciones_por_anio
                        i_k = lista_intereses[año_entero + 1] if año_entero + 1 < len(lista_intereses) else lista_intereses[-1]
                        vk = (1 + i_k) ** (-t_anios)
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
                    if interes is not None:
                        vk = 교수(1 + interes) ** (-t_anios)
                    else:
                        año_entero = f // fracciones_por_anio
                        i_k = lista_intereses[año_entero + 1] if año_entero + 1 < len(lista_intereses) else lista_intereses[-1]
                        vk = (1 + i_k) ** (-t_anios)
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
                    if interes is not None:
                        vk = (1 + interes) ** (-t_anios)
                    else:
                        año_entero = f // fracciones_por_anio
                        i_k = lista_intereses[año_entero + 1] if año_entero + 1 < len(lista_intereses) else lista_intereses[-1]
                        vk = (1 + i_k) ** (-t_anios)
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q, diferimiento)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h, diferimiento)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f-1] = [t_anios, vk, val_medio, val_medio * vk, flujo]

    # Asegurarse de que 'k' sea float (representa años fraccionarios)
    tabla_flujos['k'] = tabla_flujos['k'].astype(float)
    print("Valores devueltos por renta:", sumatorio, sumatorio * capital, tabla_flujos)
    return sumatorio, sumatorio * capital, tabla_flujos
