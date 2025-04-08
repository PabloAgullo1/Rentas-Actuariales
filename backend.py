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
        pd.DataFrame: Tabla generacional con columnas 'x+t', 'qx+t ajustado', 'lx', 'dx'.
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

def v(i, n):
    """
    Calcula el factor de descuento para una tasa de interés i y un período n.
    """
    return (1 + i) ** (-n)

def tpx(x, t=1, tabla_generacion=None):
    """
    Calcula la probabilidad de que un individuo de edad x sobreviva t años más.
    
    Args:
        x (int): Edad actual del individuo.
        t (int): Número de años a sobrevivir (por defecto 1).
        tabla_generacion (pd.DataFrame): Tabla generacional con columnas 'x+t' y 'lx'.
    
    Returns:
        float: Probabilidad tpx.
    
    Raises:
        ValueError: Si la edad x o x+t no se encuentra en la tabla de mortalidad.
    """
    if tabla_generacion is None:
        raise ValueError("Se requiere una tabla generacional para calcular tpx.")
    
    l_x = None
    l_x_mas_t = None
    
    for i in range(len(tabla_generacion["x+t"])):
        if tabla_generacion["x+t"][i] == x:
            l_x = tabla_generacion["lx"][i]
            break
    
    for i in range(len(tabla_generacion["x+t"])):
        if tabla_generacion["x+t"][i] == x + t:
            l_x_mas_t = tabla_generacion["lx"][i]
            break
    
    if l_x is None or l_x_mas_t is None:
        raise ValueError(f"Edad x={x} o x+t={x+t} no encontrada en la tabla de mortalidad")
    
    return l_x_mas_t / l_x

def tqx(tpx_value):
    """
    Calcula la probabilidad de que un individuo no sobreviva (1 - tpx).
    
    Args:
        tpx_value (float): Probabilidad tpx.
    
    Returns:
        float: Probabilidad tqx.
    """
    return 1 - tpx_value

#funcion progresiones: la idea es icorporarla en la funcion renta y que se itere junto
#  con el tpx y el vx en el range de cada tipo de renta. En caso de duda contactad con el autor  
# Muchas gracias por su tiempo :)
def progresion(tipo_renta, capital,tipo_progresion, k, h, diferimiento = None):
    if tipo_renta == "prepagable":
        if tipo_progresion == "aritmetica":
            if diferimiento is None:
                cap = capital + k * h
            else:
                deferimiento = int(deferimiento)
                cap = capital + (k-diferimiento) * h
        
        elif tipo_progresion == "geometrica":
            if diferimiento is None:
                cap = capital * (h**k)
            else:
                diferimiento = int(diferimiento)
                cap = capital * (h**(k-diferimiento))

    elif tipo_renta == "pospagable":
        if tipo_progresion == "aritmetica":
            if diferimiento is None:
                cap = capital + (k-1) * h    
            else: 
                diferimiento = int(diferimiento)
                cap = capital + (k - diferimiento - 1) * h   
        
        elif tipo_progresion == "geometrica":
            if diferimiento is None:
                cap = capital * (h**(k - 1))
            else:
                diferimiento = int(diferimiento)
                cap = capital * (h**(k-diferimiento - 1))
    return cap




def renta(tipo_renta, edad_renta, capital, temporalidad, diferimiento, interes, tabla_generacion):
    """
    Calcula el valor actual actuarial y el valor de la renta actuarial.
    
    Args:
        tipo_renta (str): Tipo de renta ("prepagable" o "pospagable").
        edad_renta (int): Edad al momento de contratación.
        capital (float): Capital a asegurar.
        temporalidad (int or None): Duración de la renta (None si es vitalicia).
        diferimiento (int or None): Período de diferimiento (None si es inmediata).
        interes (float): Tasa de interés (en decimal, ej. 0.03 para 3%).
        tabla_generacion (pd.DataFrame): Tabla generacional con columnas 'x+t', 'lx'.
    
    Returns:
        tuple: (sumatorio, valor_renta), donde sumatorio es el valor actual actuarial
               y valor_renta es el valor de la renta actuarial (capital * sumatorio).
    """
    tipo_renta = tipo_renta.lower()
    if tipo_renta not in ["prepagable", "pospagable"]:
        raise ValueError("El tipo de renta debe ser 'prepagable' o 'pospagable'")

    # Determinar la edad máxima (omega)
    w_menosx = int(tabla_generacion["x+t"].iloc[-1]) - edad_renta

    if tipo_renta == "prepagable":
        if diferimiento is None:  # Renta prepagable, anual, inmediata
            sumatorio = 1.0  # t=0
            if temporalidad is None:  # Renta vitalicia
                for i in range(1, w_menosx):
                    val_medio = tpx(edad_renta, i, tabla_generacion)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:  # Renta temporal
                for i in range(1, int(temporalidad)):
                    val_medio = tpx(edad_renta, i, tabla_generacion)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
        else:  # Renta prepagable, anual, diferida
            sumatorio = 0.0
            diferimiento = int(diferimiento)
            if temporalidad is None:  # Vitalicia
                for i in range(diferimiento, w_menosx):
                    val_medio = tpx(edad_renta, i, tabla_generacion)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:  # Temporal
                for i in range(diferimiento, int(temporalidad) + diferimiento):
                    val_medio = tpx(edad_renta, i, tabla_generacion)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk

    elif tipo_renta == "pospagable":
        if diferimiento is None:  # Renta pospagable, anual, inmediata
            sumatorio = 0.0  # t=0 no se incluye
            if temporalidad is None:  # Vitalicia
                for i in range(1, w_menosx):
                    val_medio = tpx(edad_renta, i, tabla_generacion)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:  # Temporal
                for i in range(1, int(temporalidad) + 1):
                    val_medio = tpx(edad_renta, i, tabla_generacion)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
        else:  # Renta pospagable, anual, diferida
            sumatorio = 0.0
            diferimiento = int(diferimiento)
            if temporalidad is None:  # Vitalicia
                for i in range(diferimiento + 1, w_menosx):
                    val_medio = tpx(edad_renta, i, tabla_generacion)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:  # Temporal
                for i in range(diferimiento + 1, int(temporalidad) + diferimiento + 1):
                    val_medio = tpx(edad_renta, i, tabla_generacion)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk

    return float(sumatorio), float(capital * sumatorio)