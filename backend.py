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
    if nombre_tabla in ['PERM2000C', 'PERF2000C', 'PERM2000P', 'PERF2000P', 'PER_2000P_UNISEX']:
        anio_base = 2000
        if g > 2000:
            raise ValueError("La generación no puede ser mayor a 2000.")
    elif nombre_tabla in [
        'PERM_2020_Indiv_2Orden', 'PERM_2020_Indiv_1Orden',
        'PERF_2020_Indiv_2Orden', 'PERF_2020_Indiv_1Orden',
        'PERM_2020_Colectivos_2Orden', 'PERM_2020_Colectivos_1Orden',
        'PERF_2020_Colectivos_2Orden', 'PERF_2020_Colectivos_1Orden',
        'PER_2020_Indiv_1Orden_UNISEX', 'PER_2020_Colec_1Orden_UNISEX'
    ]:
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


def tabla_gen(g, nombre_tabla, w_male=0.5, w_female=0.5):
    """
    Genera la tabla generacional para un asegurado, incluyendo tablas unisex.

    Args:
        g (int): Año de nacimiento.
        nombre_tabla (str): Nombre de la tabla de mortalidad.
        w_male (float): Proporción de hombres (por ejemplo, 0.6 para 60%).
        w_female (float): Proporción de mujeres (por ejemplo, 0.4 para 40%).

    Returns:
        pd.DataFrame: Tabla generacional con columnas:
            - Anual: 'x+t', 'qx+t ajustado', 'lx', 'dx'.
    """
    # Validar que las proporciones sumen 1
    if abs(w_male + w_female - 1.0) > 1e-6:
        raise ValueError(f"Las proporciones deben sumar 1. w_male={w_male}, w_female={w_female}")

    # Obtener el año base
    anio_base = generacion(g, nombre_tabla)
    # Calcular la edad inicial (x+t) en el año base
    edad_inicio = anio_base - g

    # Función auxiliar para cargar y procesar una tabla base
    def procesar_tabla_base(tabla_nombre):
        # Leer la tabla de mortalidad
        df = hojas[tabla_nombre].copy()

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
                raise ValueError(f"No se encontró una columna de índice 'x+t' en la tabla {tabla_nombre}.")

        # Imprimir las columnas para depurar
        print(f"Columnas de la tabla {tabla_nombre}: {df.columns.tolist()}")
        print(f"Primeros valores de la tabla de mortalidad {tabla_nombre}:")
        print(df.head(10))

        # Renombrar columnas según el tipo de tabla
        if len(df.columns) == 2:  # Tablas PERM2000/PERF2000 y PER_2020_Indiv_2Orden
            if '2Orden' in tabla_nombre:
                df.columns = ['qx', 'mejora']
            else:
                df.columns = ['qx', 'mejora']
        elif len(df.columns) == 4:  # Tablas PER_2020_Indiv_1Orden
            df = df.iloc[:, [1, 3]]  # Seleccionamos 'qx+t, tabla base' y 'λx+t'
            df.columns = ['qx', 'mejora']
        else:
            raise ValueError(f"La tabla {tabla_nombre} tiene un número inesperado de columnas: {len(df.columns)}")

        df.index.name = 'edad'

        # Generar qx+t ajustado
        qx_ajustado = []
        for i in range(edad_inicio, omega + 1):
            if i in df.index:
                qx_ajustado.append(q_x(df.loc[i, 'qx'], df.loc[i, 'mejora'], i - edad_inicio))
            else:
                qx_ajustado.append(1.0)  # Forzar qx = 1 para edades fuera de la tabla

        return qx_ajustado

    # Parámetros
    omega = 120
    x_mas_t_list = list(range(edad_inicio, omega + 1))
    edad_t = list(range(0, len(x_mas_t_list)))

    # Procesar tabla según el nombre
    if nombre_tabla in [
        "PERM2000C", "PERF2000C", "PERM2000P", "PERF2000P",
        "PERM_2020_Indiv_2Orden", "PERM_2020_Indiv_1Orden",
        "PERF_2020_Indiv_2Orden", "PERF_2020_Indiv_1Orden",
        "PERM_2020_Colectivos_2Orden", "PERM_2020_Colectivos_1Orden",
        "PERF_2020_Colectivos_2Orden", "PERF_2020_Colectivos_1Orden"
    ]:
        # Tablas estándar
        qx_ajustado = procesar_tabla_base(nombre_tabla)
    elif nombre_tabla == "PER_2020_Indiv_1Orden_UNISEX":
        # Combinar PERM_2020_Indiv_1Orden y PERF_2020_Indiv_1Orden
        qx_male = procesar_tabla_base("PERM_2020_Indiv_1Orden")
        qx_female = procesar_tabla_base("PERF_2020_Indiv_1Orden") 
        # Promedio ponderado
        qx_ajustado = [w_male * qm + w_female * qf for qm, qf in zip(qx_male, qx_female)] #qx_male = [0.01, 0.02, 0.0] qx_female = [0.05, 0.02, 0.0] qx_ = [0.01, 0.05] 
    elif nombre_tabla == "PER_2020_Colec_1Orden_UNISEX":
        # Combinar PERM_2020_Colectivos_1Orden y PERF_2020_Colectivos_1Orden
        qx_male = procesar_tabla_base("PERM_2020_Colectivos_1Orden")
        qx_female = procesar_tabla_base("PERF_2020_Colectivos_1Orden")
        qx_ajustado = [w_male * qm + w_female * qf for qm, qf in zip(qx_male, qx_female)]
    elif nombre_tabla == "PER_2000P_UNISEX":
        # Combinar PERM2000P y PERF2000P
        qx_male = procesar_tabla_base("PERM2000P")
        qx_female = procesar_tabla_base("PERF2000P")
        qx_ajustado = [w_male * qm + w_female * qf for qm, qf in zip(qx_male, qx_female)]
    else:
        raise ValueError(f"Tabla {nombre_tabla} no encontrada.")

    # Crear el DataFrame de resultados
    resultados = pd.DataFrame(columns=['Edad', 'x+t'])
    resultados['x+t'] = x_mas_t_list
    resultados['Edad'] = edad_t

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

def v(lista_intereses, t, fracciones_por_anio, tipo_renta="pospagable"):
    if lista_intereses is None:
        interes = factores.get('interes', 0)
        interes_subperiodo = (1 + interes) ** (1 / fracciones_por_anio) - 1
        num_subperiodos = t * fracciones_por_anio
        # Ajuste para prepagable: los pagos ocurren al inicio del subperíodo
        if tipo_renta.lower() == "prepagable":
            num_subperiodos -= 1 / fracciones_por_anio  # Descontar un subperíodo menos
        return (1 + interes_subperiodo) ** (-num_subperiodos)
    else:
        t_int = int(t * fracciones_por_anio)
        fraccion = t * fracciones_por_anio - t_int
        v_total = 1.0
        for i in range(t_int + 1):
            if i < len(lista_intereses):
                interes = lista_intereses[i]
            else:
                interes = lista_intereses[-1]
            interes_subperiodo = (1 + interes) ** (1 / fracciones_por_anio) - 1
            # Ajuste para prepagable
            if tipo_renta.lower() == "prepagable" and i == 0:
                continue  # No descontar el primer subperíodo
            v_total *= (1 + interes_subperiodo) ** (-1)
        if fraccion > 0 and t_int < len(lista_intereses):
            interes = lista_intereses[t_int]
            interes_subperiodo = (1 + interes) ** (1 / fracciones_por_anio) - 1
            v_total *= (1 + interes_subperiodo) ** (-fraccion)
        return v_total

def tpx(x, t=1, tabla_generacion=None, fracciones_por_anio=1):
    """
    Calcula la probabilidad de supervivencia desde la edad x hasta x+t.
    
    Args:
        x (int): Edad inicial.
        t (float): Tiempo en años (puede ser fraccionario).
        tabla_generacion (pd.DataFrame): Tabla generacional con columnas 'x+t' y 'lx'.
        fracciones_por_anio (int): Fracciones por año (1 para anual, 4 para trimestral, etc.).
    
    Returns:
        float: Probabilidad de supervivencia k p_x.
    """
    if tabla_generacion is None:
        raise ValueError("Se requiere una tabla generacional.")
    
    # Edad inicial absoluta
    edad_inicio = x
    # Edad final absoluta (con fracciones)
    edad_final = x + t
    
    # Si t = 0, la probabilidad es 1
    if t == 0:
        return 1.0
    
    # Redondear edades para obtener los años completos
    k_inicio = int(edad_inicio)
    k_final = int(edad_final)
    fraccion_final = edad_final - k_final
    
    # Obtener lx para la edad inicial
    if k_inicio not in tabla_generacion['x+t'].values:
        raise ValueError(f"La edad inicial {k_inicio} no está en la tabla generacional.")
    lx = tabla_generacion.loc[tabla_generacion['x+t'] == k_inicio, 'lx'].iloc[0]
    
    # Obtener lx para el año completo de la edad final
    if k_final not in tabla_generacion['x+t'].values:
        # Si la edad final está fuera del rango, asumimos lx = 0
        if k_final > tabla_generacion['x+t'].max():
            return 0.0
        raise ValueError(f"La edad {k_final} no está en la tabla generacional.")
    lx_final = tabla_generacion.loc[tabla_generacion['x+t'] == k_final, 'lx'].iloc[0]
    
    # Si hay una fracción, interpolar linealmente
    if fraccion_final > 0:
        k_final_siguiente = k_final + 1
        if k_final_siguiente not in tabla_generacion['x+t'].values:
            if k_final_siguiente > tabla_generacion['x+t'].max():
                lx_final_siguiente = 0
            else:
                raise ValueError(f"La edad {k_final_siguiente} no está en la tabla generacional.")
        else:
            lx_final_siguiente = tabla_generacion.loc[tabla_generacion['x+t'] == k_final_siguiente, 'lx'].iloc[0]
        # Interpolación lineal
        lx_final = lx_final + (lx_final_siguiente - lx_final) * fraccion_final
    
    # Calcular k p_x
    if lx == 0:
        return 0.0
    return lx_final / lx

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
    tabla_flujos = pd.DataFrame(columns=['k', 't', 'v^k', 'k p_x', 'v^k * k p_x', 'C * k p_x'])

    sumatorio = 0.0
    if tipo_renta == "prepagable":
        if diferimiento is None:  # Renta prepagable, inmediata
            if temporalidad is None:  # Vitalicia
                for f in range(total_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    k_absoluto = edad_renta + t_anios
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f] = [k_absoluto, t_anios, vk, val_medio, val_medio * vk, flujo]
            else:  # Temporal
                for f in range(total_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    k_absoluto = edad_renta + t_anios
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f] = [k_absoluto, t_anios, vk, val_medio, val_medio * vk, flujo]
        else:  # Renta prepagable, diferida
            diferimiento_fracciones = int(diferimiento * fracciones_por_anio)
            if temporalidad is None:  # Vitalicia
                for f in range(diferimiento_fracciones, total_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    k_absoluto = edad_renta + t_anios
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q, diferimiento)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h, diferimiento)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f] = [k_absoluto, t_anios, vk, val_medio, val_medio * vk, flujo]
            else:  # Temporal
                for f in range(diferimiento_fracciones, total_fracciones + diferimiento_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    k_absoluto = edad_renta + t_anios
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q, diferimiento)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h, diferimiento)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f] = [k_absoluto, t_anios, vk, val_medio, val_medio * vk, flujo]
    
    elif tipo_renta == "pospagable":
        if diferimiento is None:  # Renta pospagable, inmediata
            if temporalidad is None:  # Vitalicia
                for f in range(1, total_fracciones):  # Pospagable comienza en f=1
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    k_absoluto = edad_renta + t_anios
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f-1] = [k_absoluto, t_anios, vk, val_medio, val_medio * vk, flujo]
            else:  # Temporal
                for f in range(1, total_fracciones + 1):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    k_absoluto = edad_renta + t_anios
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f-1] = [k_absoluto, t_anios, vk, val_medio, val_medio * vk, flujo]
        else:  # Renta pospagable, diferida
            diferimiento_fracciones = int(diferimiento * fracciones_por_anio)
            if temporalidad is None:  # Vitalicia
                for f in range(diferimiento_fracciones + 1, total_fracciones):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    k_absoluto = edad_renta + t_anios
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q, diferimiento)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h, diferimiento)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f-1] = [k_absoluto, t_anios, vk, val_medio, val_medio * vk, flujo]
            else:  # Temporal
                for f in range(diferimiento_fracciones + 1, total_fracciones + diferimiento_fracciones + 1):
                    t_anios = f / fracciones_por_anio
                    val_medio = tpx(edad_renta, t_anios, tabla_fraccionada, fracciones_por_anio)
                    vk = v(lista_intereses, t_anios, fracciones_por_anio)
                    k_absoluto = edad_renta + t_anios
                    if tipo_ajuste == "geometrica":
                        cap_ajustado = capital * geometrica(tipo_renta, f // fracciones_por_anio, factor_q, diferimiento)
                    elif tipo_ajuste == "aritmetica":
                        cap_ajustado = aritmetica(capital, tipo_renta, f // fracciones_por_anio, incremento_h, diferimiento)
                    else:
                        cap_ajustado = capital
                    flujo = val_medio * cap_ajustado
                    sumatorio += (val_medio * vk * cap_ajustado) / capital
                    tabla_flujos.loc[f-1] = [k_absoluto, t_anios, vk, val_medio, val_medio * vk, flujo]

    # Ajuste para rentas prepagables
    if tipo_renta.lower() == "prepagable":
        ajuste_prepagable = (1 + lista_intereses[1]) ** (1 / fracciones_por_anio) if len(lista_intereses) > 1 else (1 + interes) ** (1 / fracciones_por_anio)
        sumatorio = sumatorio * ajuste_prepagable

    # Añadir t_relativo
    if 't_relativo' not in tabla_flujos.columns:
        tabla_flujos['t_relativo'] = tabla_flujos['t'] - (diferimiento or 0)

    # Renombrar columnas si es necesario
    column_rename = {
        'edad': 'k',
        'x+t': 'k',
        'l_{x+k+j/fracciones}': 'k p_x',
        'qx+t ajustado': 'qx',
        'valor_actual': 'k p_x * C_k * v^k',
        'C * k p_x': 'C_k'  # Renombrar para consistencia
    }
    for old, new in column_rename.items():
        if old in tabla_flujos.columns and new not in tabla_flujos.columns:
            tabla_flujos.rename(columns={old: new}, inplace=True)

    print("Valores devueltos por renta:", sumatorio, sumatorio * capital, tabla_flujos)
    return sumatorio, sumatorio * capital, tabla_flujos

#NUEVAS FUNCIONES PARA MANEJAR LOS INCREMENTOS ARITMETICOS Y GEOMETRICOS VARIABLES 

def funcion_incrementos_aritmeticos_variables(incrementos, saltos_incrementos, temporalidad=None, diferimiento=0):
    """
    Genera una lista de incrementos aritméticos (h_t) para cada año t.
    - incrementos: Lista de cantidades a sumar (ej. [1000, 500] €). Cada valor representa cuánto se incrementa la renta.
    - saltos_incrementos: Años donde cambian los incrementos (ej. [5]). Indica en qué año cambia el valor del incremento.
    - temporalidad: Duración de la renta en años (None para vitalicia). Limita la duración total si no es vitalicia.
    - diferimiento: Años antes de que comience la renta. Durante este período, los incrementos son 0.
    Retorna: Lista de h_t desde t=0, donde cada h_t es el incremento aritmético aplicable en ese año.
    """
    # Durante el período de diferimiento, no hay renta, por lo que los incrementos son 0.
    # Creamos una lista con 'diferimiento' elementos, todos 0.0.
    lista_ht = [0.0] * diferimiento  # Ejemplo: si diferimiento=2, lista_ht = [0.0, 0.0]

    # t_actual representa el año en el que estamos procesando.
    # Comienza después del diferimiento, ya que los años anteriores ya los llenamos con 0.
    t_actual = diferimiento  # Ejemplo: si diferimiento=2, t_actual comienza en 2 (año 3).

    # Calculamos el número máximo de años que necesitamos procesar.
    # Si la renta es temporal (temporalidad no es None), sumamos el diferimiento a la duración.
    # Si es vitalicia (temporalidad=None), asumimos un máximo de 100 años después del diferimiento.
    max_anios = temporalidad + diferimiento if temporalidad is not None else 100 + diferimiento
    max_anios = int(max_anios) + 1  # +1 para incluir el último año (rango inclusivo).

    # Ejemplo: temporalidad=10, diferimiento=2 → max_anios = 10 + 2 + 1 = 13 (años 0 a 12).
    # Ejemplo: temporalidad=None, diferimiento=2 → max_anios = 100 + 2 + 1 = 103 (años 0 a 102).

    # Iteramos sobre los años de cambio (saltos_incrementos) para asignar los incrementos correspondientes.
    for i, salto in enumerate(saltos_incrementos):
        # Validamos que haya suficientes incrementos para los saltos proporcionados.
        if i >= len(incrementos):
            raise ValueError("Faltan incrementos para los saltos proporcionados.")

        # Ajustamos el año de cambio considerando el diferimiento.
        # Ejemplo: si salto=5 y diferimiento=2, el cambio ocurre en el año absoluto 5+2=7.
        salto_absoluto = salto + diferimiento

        # Llenamos la lista desde t_actual hasta el año del cambio (salto_absoluto) o hasta max_anios, lo que sea menor.
        for t in range(t_actual, min(salto_absoluto, max_anios)):
            # Agregamos el incremento correspondiente al período actual (incrementos[i]).
            # Ejemplo: incrementos=[1000, 500], i=0 → agrega 1000 para cada año en este rango.
            lista_ht.append(incrementos[i])  # h_t = incremento en €.

        # Actualizamos t_actual al año del cambio, para continuar desde ahí en la próxima iteración.
        t_actual = salto_absoluto

        # Si ya llegamos al máximo de años, terminamos el bucle.
        if t_actual >= max_anios:
            break

    # Si aún no hemos llenado todos los años hasta max_anios, completamos con el último incremento.
    if t_actual < max_anios:
        # Validamos que haya al menos un incremento para usar.
        if not incrementos:
            raise ValueError("No hay incrementos para completar los años restantes.")
        # Llenamos los años restantes con el último incremento disponible.
        for t in range(t_actual, max_anios):
            # Ejemplo: incrementos=[1000, 500] → usa 500 (el último) para los años restantes.
            lista_ht.append(incrementos[-1])

    # Retornamos la lista completa de incrementos h_t para cada año t.
    return lista_ht

def funcion_incrementos_variables(incrementos, saltos_incrementos, temporalidad=None, diferimiento=0):
    """
    Genera una lista de factores de incremento geométricos (q_t) para cada año t.
    - incrementos: Lista de tasas de incremento en % (ej. [0.02, 0.01] → 2%, 1%).
    - saltos_incrementos: Años donde cambian los incrementos (ej. [5]).
    - temporalidad: Duración de la renta en años (None para vitalicia).
    - diferimiento: Años antes de que comience la renta.
    Retorna: Lista de q_t desde t=0, donde q_t = 1 + tasa de incremento.
    """
    # Durante el período de diferimiento, no hay renta, por lo que los factores de incremento son 1.0 (sin cambio).
    # Creamos una lista con 'diferimiento' elementos, todos 1.0.
    lista_qt = [1.0] * diferimiento  # Ejemplo: si diferimiento=2, lista_qt = [1.0, 1.0]

    # t_actual representa el año en el que estamos procesando.
    # Comienza después del diferimiento.
    t_actual = diferimiento  # Ejemplo: si diferimiento=2, t_actual comienza en 2 (año 3).

    # Calculamos el número máximo de años que necesitamos procesar.
    # Si la renta es temporal, sumamos el diferimiento a la duración.
    # Si es vitalicia, asumimos un máximo de 100 años después del diferimiento.
    max_anios = temporalidad + diferimiento if temporalidad is not None else 100 + diferimiento
    max_anios = int(max_anios) + 1  # +1 para incluir el último año.

    # Ejemplo: temporalidad=10, diferimiento=2 → max_anios = 13.
    # Ejemplo: temporalidad=None, diferimiento=2 → max_anios = 103.

    # Iteramos sobre los años de cambio (saltos_incrementos) para asignar los factores de incremento.
    for i, salto in enumerate(saltos_incrementos):
        # Validamos que haya suficientes incrementos para los saltos proporcionados.
        if i >= len(incrementos):
            raise ValueError("Faltan incrementos para los saltos proporcionados.")

        # Ajustamos el año de cambio considerando el diferimiento.
        salto_absoluto = salto + diferimiento

        # Llenamos la lista desde t_actual hasta el año del cambio o hasta max_anios.
        for t in range(t_actual, min(salto_absoluto, max_anios)):
            # Calculamos el factor de incremento: q_t = 1 + tasa de incremento.
            # Ejemplo: incrementos=[0.02, 0.01], i=0 → q_t = 1 + 0.02 = 1.02.
            lista_qt.append(1 + incrementos[i])

        # Actualizamos t_actual al año del cambio.
        t_actual = salto_absoluto

        # Si ya llegamos al máximo de años, terminamos el bucle.
        if t_actual >= max_anios:
            break

    # Si aún no hemos llenado todos los años hasta max_anios, completamos con el último factor.
    if t_actual < max_anios:
        # Validamos que haya al menos un incremento para usar.
        if not incrementos:
            raise ValueError("No hay incrementos para completar los años restantes.")
        # Llenamos los años restantes con el último factor disponible.
        for t in range(t_actual, max_anios):
            # Ejemplo: incrementos=[0.02, 0.01] → usa 1 + 0.01 = 1.01.
            lista_qt.append(1 + incrementos[-1])

    # Retornamos la lista completa de factores q_t para cada año t.
    return lista_qt

def interpolar_lx_general(tabla_anual, edad_renta, diferimiento, duracion, fracciones_por_anio=1):
    """
    Interpola lx para fracciones de año y calcula k p_x para rentas con o sin diferimiento.
    
    Args:
        tabla_anual (pd.DataFrame): Tabla generacional con columnas 'x+t', 'lx'.
            # 'x+t': Edad absoluta (edad inicial + tiempo transcurrido).
            # 'lx': Número de sobrevivientes a esa edad (de una población inicial).
        edad_renta (int): Edad inicial para calcular k p_x.
            # Ejemplo: Si edad_renta=50, calculamos la probabilidad de que alguien de 50 años sobreviva a edades futuras.
        diferimiento (int): Años de diferimiento (0 si renta inmediata).
            # Ejemplo: Si diferimiento=2, los pagos comienzan 2 años después de edad_renta.
        duracion (int): Número de años a interpolar.
            # Ejemplo: Si duracion=10, generamos datos para 10 años (de k=0 a k=10).
        fracciones_por_anio (int): Fracciones por año (1, 4, 12, etc.).
            # Ejemplo: Si fracciones_por_anio=12, calculamos valores mensuales (12 fracciones por año).
    
    Returns:
        pd.DataFrame: Tabla con columnas k (edad absoluta), t (tiempo desde edad_renta), k p_x.
            # 'k': Edad absoluta, incluyendo fracciones (ej. 50.5 para medio año).
            # 't': Tiempo transcurrido desde edad_renta, incluyendo fracciones.
            # 'k p_x': Probabilidad de que alguien de edad_renta sobreviva hasta el tiempo t.
    """
    # Lista para almacenar los resultados de cada fracción de cada año.
    resultados = []

    # Obtenemos la edad máxima disponible en la tabla generacional.
    # Esto nos ayuda a saber hasta dónde podemos interpolar sin exceder los datos.
    max_edad = tabla_anual['x+t'].max()
    # Ejemplo: Si tabla_anual tiene datos hasta x+t=110, max_edad=110.

    # Calculamos la edad en la que comienzan los pagos.
    # Si hay diferimiento, los pagos empiezan después de esos años.
    edad_inicio = edad_renta + diferimiento
    # Ejemplo: edad_renta=50, diferimiento=2 → edad_inicio=52 (los pagos comienzan a los 52 años).

    # Obtenemos el valor de lx inicial (número de sobrevivientes a la edad_renta).
    # Esto será el denominador para calcular k p_x.
    if edad_renta not in tabla_anual['x+t'].values:
        # Validamos que la edad inicial esté en la tabla, si no, lanzamos un error.
        raise ValueError(f"La edad inicial {edad_renta} no está en la tabla generacional.")
    lx_inicial = tabla_anual.loc[tabla_anual['x+t'] == edad_renta, 'lx'].iloc[0]
    # Ejemplo: Si edad_renta=50 y tabla_anual tiene lx=95000 para x+t=50, entonces lx_inicial=95000.

    # Iteramos sobre cada año del período de duración (de k=0 a k=duracion).
    for k_offset in range(duracion + 1):
        # k_offset representa el desplazamiento en años desde edad_inicio.
        # Calculamos la edad actual sumando el desplazamiento a edad_inicio.
        edad = edad_inicio + k_offset
        # Ejemplo: edad_inicio=52, k_offset=0 → edad=52; k_offset=1 → edad=53.

        # Calculamos el tiempo transcurrido desde edad_renta (t).
        # Esto incluye el diferimiento.
        t = edad - edad_renta  # Tiempo transcurrido desde edad_renta.
        # Ejemplo: edad=52, edad_renta=50 → t=52-50=2.

        # Obtenemos lx para la edad actual (número de sobrevivientes a esa edad).
        if edad > max_edad:
            # Si la edad excede la máxima disponible en la tabla, asumimos que no hay sobrevivientes.
            lx = 0
        else:
            # Si la edad está dentro del rango, obtenemos lx directamente de la tabla.
            lx = tabla_anual.loc[tabla_anual['x+t'] == edad, 'lx'].values[0]
        # Ejemplo: edad=52, tabla_anual tiene lx=94000 para x+t=52 → lx=94000.

        # Obtenemos lx para la siguiente edad (para interpolar entre años).
        if edad + 1 > max_edad:
            # Si la siguiente edad excede la máxima, asumimos que no hay sobrevivientes.
            lx_next = 0
        else:
            # Si está dentro del rango, obtenemos lx de la siguiente edad.
            lx_next = tabla_anual.loc[tabla_anual['x+t'] == edad + 1, 'lx'].values[0]
        # Ejemplo: edad=52, tabla_anual tiene lx=93000 para x+t=53 → lx_next=93000.

        # Iteramos sobre cada fracción del año (por ejemplo, 12 fracciones si es mensual).
        for j in range(fracciones_por_anio):
            # Calculamos la fracción del año.
            # Ejemplo: fracciones_por_anio=12, j=0 → fraccion=0/12=0; j=6 → fraccion=6/12=0.5.
            fraccion = j / fracciones_por_anio

            # Interpolamos lx entre lx (inicio del año) y lx_next (fin del año) usando una interpolación lineal.
            # Fórmula: lx_interp = lx + (lx_next - lx) * fraccion.
            lx_interp = lx - (lx_next - lx) * fraccion
            # Ejemplo: lx=94000, lx_next=93000, fraccion=0.5 → lx_interp = 94000 + (93000-94000)*0.5 = 93500.

            # Calculamos k p_x: probabilidad de supervivencia desde edad_renta hasta el tiempo t+fraccion.
            # Fórmula: k p_x = lx_interp / lx_inicial (si lx_inicial != 0).
            k_p_x = lx_interp / lx_inicial if lx_inicial != 0 else 0
            # Ejemplo: lx_interp=93500, lx_inicial=95000 → k_p_x = 93500/95000 ≈ 0.9842.

            # Agregamos los datos a los resultados.
            resultados.append({
                'k': edad + fraccion,  # Edad absoluta, incluyendo fracciones.
                't': t + fraccion,     # Tiempo desde edad_renta, incluyendo fracciones.
                'k p_x': k_p_x         # Probabilidad de supervivencia.
            })
            # Ejemplo: edad=52, fraccion=0.5 → k=52.5, t=2.5, k_p_x=0.9842.

    # Convertimos los resultados a un DataFrame para facilitar su uso.
    tabla = pd.DataFrame(resultados)

    # Imprimimos las primeras y últimas 10 filas para depuración.
    print("Valores de tabla interpolada:")
    print(tabla.head(10))  # Primeras 10 filas.
    print(tabla.tail(10))  # Últimas 10 filas.

    # Retornamos la tabla con las columnas 'k', 't', y 'k p_x'.
    return tabla
    
def generar_tabla_flujos(tabla_generacion, edad_renta, diferimiento, tipo_renta, temporalidad, fracciones_por_anio=1):
    """
    Genera tabla de flujos para cálculos actuariales.
    - k representa el año actuarial (inicia en diferimiento, e.g., 17).
    - t y t_relativo reflejan los subperíodos fraccionados.
    - j representa el subperíodo dentro del año (0 a 11 para prepagable, 1 a 12 para pospagable).
    
    Args:
        tabla_generacion (pd.DataFrame): Tabla generacional con datos de mortalidad.
            # Contiene columnas como 'x+t' (edad absoluta) y 'lx' (número de sobrevivientes).
            # Usada para calcular la probabilidad de supervivencia k p_x.
        edad_renta (int): Edad inicial del beneficiario para calcular k p_x.
            # Ejemplo: Si edad_renta=50, calculamos probabilidades de supervivencia desde los 50 años.
        diferimiento (int): Años antes de que comience la renta (0 si es inmediata).
            # Ejemplo: Si diferimiento=2, la renta comienza 2 años después de edad_renta.
        tipo_renta (str): Tipo de renta ('prepagable' o 'pospagable').
            # Prepagable: Pagos al inicio de cada subperíodo (t=17.0, 17.0833, ...).
            # Pospagable: Pagos al final de cada subperíodo (t=17.0833, 17.1667, ...).
        temporalidad (int or None): Duración de la renta en años (None para vitalicia).
            # Ejemplo: temporalidad=10 → renta por 10 años; None → renta vitalicia.
        fracciones_por_anio (int): Número de pagos por año (1, 2, 4, 12, etc.).
            # Ejemplo: fracciones_por_anio=12 → pagos mensuales (12 fracciones por año).
    
    Returns:
        pd.DataFrame: Tabla con columnas k, t, t_relativo, j, k p_x.
            # 'k': Año actuarial (entero, comienza en diferimiento).
            # 't': Tiempo absoluto (incluye fracciones, ej. 17.0833).
            # 't_relativo': Tiempo relativo al inicio de la renta (t - diferimiento).
            # 'j': Subperíodo dentro del año (0 a 11 para prepagable, 1 a 12 para pospagable).
            # 'k p_x': Probabilidad de supervivencia desde edad_renta hasta el tiempo t.
    """
    # Definimos omega como la edad máxima teórica (límite de vida).
    # En tablas de mortalidad, suele ser 120 años, lo que representa el máximo de edad que consideramos.
    omega = 120

    # Determinamos el número máximo de años para los que generaremos flujos.
    if temporalidad is None:
        # Si la renta es vitalicia (temporalidad=None), calculamos hasta omega - edad_renta - 1.
        # Restamos 1 para no exceder la edad máxima (omega).
        # Ejemplo: edad_renta=50, omega=120 → max_anios = 120 - 50 - 1 = 69 años.
        max_anios = omega - edad_renta - 1
    else:
        # Si la renta es temporal, usamos la duración especificada en temporalidad.
        # Ejemplo: temporalidad=10 → max_anios = 10 años.
        max_anios = temporalidad

    # Creamos un DataFrame vacío con las columnas necesarias para almacenar los flujos.
    # Las columnas representan:
    # - k: Año actuarial (entero).
    # - t: Tiempo absoluto (puede incluir fracciones).
    # - t_relativo: Tiempo relativo al inicio de la renta.
    # - j: Subperíodo dentro del año.
    # - k p_x: Probabilidad de supervivencia.
    tabla = pd.DataFrame(columns=['k', 't', 't_relativo', 'j', 'k p_x'])

    # Índice para llenar las filas del DataFrame de forma incremental.
    idx = 0

    # Iteramos sobre cada año de la duración de la renta (de 0 a max_anios-1).
    for anio in range(max_anios):
        # Calculamos k, el año actuarial, que comienza en el año de diferimiento.
        # 'anio' es el desplazamiento desde el inicio de la renta.
        # Ejemplo: Si diferimiento=2, entonces anio=0 → k=2, anio=1 → k=3.
        k = (diferimiento or 0) + anio  # k inicia en diferimiento (ej. 17).
        # Nota: Usamos 'diferimiento or 0' para manejar el caso en que diferimiento=None (lo tratamos como 0).

        # Iteramos sobre cada fracción dentro del año (según fracciones_por_anio).
        # Ejemplo: Si fracciones_por_anio=12, iteramos sobre f=0, 1, ..., 11 (para pagos mensuales).
        for f in range(fracciones_por_anio):
            # Determinamos el tiempo t y el subperíodo j según el tipo de renta.
            if tipo_renta.lower() == 'prepagable':
                # Para rentas prepagables, los pagos ocurren al inicio de cada subperíodo.
                # t se calcula sumando la fracción del año al año actuarial k.
                # Ejemplo: k=17, fracciones_por_anio=12, f=0 → t=17.0; f=1 → t=17.0833.
                t = k + f / fracciones_por_anio  # 17.0000, 17.0833, ..., 17.9167.
                # j es simplemente el número de la fracción (subperíodo).
                j = f  # 0, 1, ..., 11.
            else:  # pospagable
                # Para rentas pospagables, los pagos ocurren al final de cada subperíodo.
                # t se calcula sumando (f+1)/fracciones_por_anio para que el pago sea al final del período.
                # Ejemplo: k=17, fracciones_por_anio=12, f=0 → t=17.0833; f=11 → t=18.0.
                t = k + (f + 1) / fracciones_por_anio  # 17.0833, 17.1667, ..., 18.0000.
                # j es el subperíodo, ajustado para que vaya de 1 a fracciones_por_anio.
                j = f + 1  # 1, 2, ..., 12.

            # Filtramos los períodos que ocurren antes del inicio de la renta.
            # Esto asegura que no generemos flujos para tiempos antes de que comience la renta.
            if tipo_renta.lower() == 'prepagable':
                # Para prepagable, excluimos tiempos estrictamente menores al diferimiento.
                # Ejemplo: Si diferimiento=2, no queremos t<2 (antes de que comience la renta).
                # Un pago en t=2.0 (inicio del período) es válido.
                if t < (diferimiento or 0):
                    continue
            else:
                # Para pospagable, excluimos tiempos menores o iguales al diferimiento.
                # Ejemplo: Si diferimiento=2, no queremos t<=2.
                # El primer pago sería en t=2.0833 (para fracciones_por_anio=12).
                if t <= (diferimiento or 0):
                    continue

            # Calculamos t_relativo: el tiempo relativo al inicio de la renta.
            # Restamos el diferimiento a t para obtener el tiempo transcurrido desde el inicio de los pagos.
            # Ejemplo: t=17.0833, diferimiento=2 → t_relativo = 17.0833 - 2 = 15.0833.
            t_relativo = t - (diferimiento or 0)

            # Calculamos k p_x: probabilidad de que una persona de edad_renta sobreviva hasta el tiempo t.
            # La función tpx (no definida aquí) calcula esta probabilidad usando la tabla generacional.
            # tpx interpola lx si es necesario para fracciones de año.
            val_medio = tpx(edad_renta, t, tabla_generacion, fracciones_por_anio)
            # Ejemplo: edad_renta=50, t=17.0833 → val_medio = probabilidad de sobrevivir de 50 a 67.0833 años.

            # Agregamos la fila al DataFrame con los valores calculados.
            # Cada fila representa un momento de pago y su probabilidad de supervivencia asociada.
            tabla.loc[idx] = [k, t, t_relativo, j, val_medio]
            # Ejemplo: [17, 17.0833, 15.0833, 1, 0.95].
            idx += 1  # Incrementamos el índice para la siguiente fila.

    # Ordenamos la tabla por las columnas 'k' y 't' para asegurar que los datos estén en orden cronológico.
    # Esto es importante para cálculos posteriores que dependan del orden de los flujos.
    tabla = tabla.sort_values(by=['k', 't']).reset_index(drop=True)

    # Retornamos la tabla completa con los flujos actuariales.
    return tabla

def calcular_ck(t_relativo, k, tipo_renta, capital, factores, fracciones_por_anio):
    """
    Calcula el valor de C_k para un tiempo relativo dado.
    Soporta todas: prepagable/pospagable, aritmético/geométrico.
    
    Args:
        t_relativo (float): Tiempo relativo al inicio de la renta (t - diferimiento).
            # Ejemplo: Si t=17.0833 y diferimiento=2, t_relativo=15.0833.
        k (float or int): Año actuarial (entero, comienza en diferimiento).
            # Ejemplo: k=17 para el año 17.
        tipo_renta (str): Tipo de renta ('prepagable' o 'pospagable').
            # Prepagable: Pagos al inicio de cada subperíodo.
            # Pospagable: Pagos al final de cada subperíodo.
        capital (float): Cuantía inicial de la renta.
            # Ejemplo: capital=15000 → cuantía inicial de 15,000 €.
        factores (dict): Diccionario con parámetros de incremento.
            # 'tipo': 'geometrico', 'aritmetico', o None (sin incremento).
            # 'q': Factor geométrico fijo (ej. q=1.02 para 2% de incremento).
            # 'h': Incremento aritmético fijo (ej. h=500 para 500 €).
            # 'lista_factores': Lista de factores geométricos variables.
            # 'saltos_factores': Años donde cambian los factores.
            # 'lista_incrementos': Lista de incrementos aritméticos variables.
            # 'saltos_incrementos': Años donde cambian los incrementos.
            # 'diferimiento': Años de diferimiento (para pospagable).
        fracciones_por_anio (int): Número de pagos por año (1, 2, 4, 12, etc.).
            # Ejemplo: fracciones_por_anio=12 → pagos mensuales.
    
    Returns:
        float: Valor de C_k ajustado por incrementos y fracciones por año.
            # Ejemplo: Si capital=15000 y fracciones_por_anio=12, cada pago es 15000/12=1250 € (sin incremento).
    """
    # Aseguramos que k y t_relativo sean tratados como valores numéricos.
    # k debe ser entero (año actuarial), mientras que t_relativo puede incluir fracciones.
    k = int(float(k))  # Convertir k a entero.
    # Ejemplo: k=17.0 → k=17.
    t_relativo = float(t_relativo)  # Asegurar que t_relativo sea float.
    # Ejemplo: t_relativo="15.0833" → t_relativo=15.0833.

    # Determinamos el año actuarial relativo al inicio de los pagos.
    # Esto nos ayuda a aplicar los incrementos en el momento correcto.
    if tipo_renta.lower() == 'pospagable':
        # Para rentas pospagables, ajustamos k restando el diferimiento.
        # El diferimiento está en el diccionario factores.
        diferimiento = int(float(factores.get('diferimiento', 0)))  # 17.
        # Ejemplo: Si k=17 y diferimiento=2, anio_actuarial=17-2=15.
        anio_actuarial = k - diferimiento  # Ajuste: quitar el -1.
    else:
        # Para rentas prepagables, usamos t_relativo directamente.
        # Como t_relativo ya está ajustado por el diferimiento, lo convertimos a entero.
        anio_actuarial = int(t_relativo)
        # Ejemplo: t_relativo=15.0833 → anio_actuarial=15.

    # Comprobamos el tipo de incremento especificado en factores.
    if factores['tipo'] == 'geometrico':
        # Incremento geométrico: C_k se multiplica por un factor acumulativo (q^t).
        if 'q' in factores:
            # Caso 1: Incremento geométrico fijo (q es constante).
            # Ejemplo: q=1.02 → 2% de incremento anual.
            if tipo_renta.lower() == 'pospagable':
                # Para pospagable, aplicamos el factor q elevado al año actuarial.
                # Usamos max(0, anio_actuarial) para evitar exponentes negativos.
                # Ejemplo: capital=15000, q=1.02, anio_actuarial=1 → C_k = 15000 * (1.02)^1.
                return (capital * (factores['q'] ** max(0, anio_actuarial))) / fracciones_por_anio
            else:
                # Para prepagable, usamos t_relativo directamente.
                # Ejemplo: t_relativo=1.25, q=1.02 → C_k = 15000 * (1.02)^1.25.
                return (capital * (factores['q'] ** t_relativo)) / fracciones_por_anio
        elif 'lista_factores' in factores and 'saltos_factores' in factores:
            # Caso 2: Incremento geométrico variable (lista de factores).
            lista_factores = factores['lista_factores']
            # Ejemplo: lista_factores=[1.02, 1.01] → 2% y luego 1%.
            # Convertimos saltos_factores a enteros para asegurar consistencia.
            saltos_factores = [int(float(s)) for s in factores['saltos_factores']]
            # Ejemplo: saltos_factores=[5] → el factor cambia en el año 5.

            # Generamos una lista de factores hasta anio_actuarial.
            factores_completos = []
            t_actual = 0
            max_t = max(0, anio_actuarial)  # Número de años con incremento.
            # Ejemplo: anio_actuarial=6 → max_t=6.
            
            # Iteramos sobre los saltos para construir la lista de factores.
            for i, salto in enumerate(saltos_factores):
                # Si no hay más factores, salimos del bucle.
                if i >= len(lista_factores):
                    break
                # Si ya llegamos al máximo tiempo, salimos.
                if t_actual >= max_t:
                    break
                # Calculamos cuántos años aplica el factor actual.
                num_repeticiones = max(0, int(salto - t_actual))
                # Si el salto excede max_t, ajustamos el número de repeticiones.
                if salto > max_t:
                    num_repeticiones = max(0, int(max_t - t_actual))
                # Agregamos el factor correspondiente el número de veces necesario.
                factores_completos.extend([lista_factores[i]] * num_repeticiones)
                # Ejemplo: salto=5, t_actual=0, num_repeticiones=5 → [1.02, 1.02, 1.02, 1.02, 1.02].
                t_actual = salto

            # Calculamos C_k según anio_actuarial.
            if anio_actuarial <= 0:
                # Si anio_actuarial <= 0, no hay incremento (primer año).
                # Ejemplo: capital=15000, fracciones_por_anio=12 → C_k = 15000/12 = 1250.
                return capital / fracciones_por_anio  # Primer año sin incremento.
            else:
                # Multiplicamos todos los factores para obtener el factor acumulado.
                factor_acumulado = math.prod(factores_completos)
                # Ejemplo: factores_completos=[1.02, 1.02, ..., 1.01] → factor_acumulado = 1.02^5 * 1.01.
                # C_k = capital * factor_acumulado / fracciones_por_anio.
                return (capital * factor_acumulado) / fracciones_por_anio
        else:
            # Si no se proporcionan los parámetros necesarios, lanzamos un error.
            raise ValueError("Para tipo 'geometrico', se requiere 'q' o 'lista_factores' con 'saltos_factores'")
    elif factores['tipo'] == 'aritmetico':
        # Incremento aritmético: C_k se incrementa sumando una cantidad (h).
        if 'h' in factores:
            # Caso 1: Incremento aritmético fijo (h es constante).
            # Ejemplo: h=500 → se suman 500 € por año.
            if tipo_renta.lower() == 'pospagable':
                # Para pospagable, aplicamos h según el año actuarial.
                # Ejemplo: capital=15000, h=500, anio_actuarial=1 → C_k = (15000 + 1*500).
                return (capital + (max(0, anio_actuarial) * factores['h'])) / fracciones_por_anio
            else:
                # Para prepagable, usamos t_relativo directamente.
                # Ejemplo: t_relativo=1.25, h=500 → C_k = (15000 + 1.25*500).
                return (capital + (t_relativo * factores['h'])) / fracciones_por_anio
        elif 'lista_incrementos' in factores and 'saltos_incrementos' in factores:
            # Caso 2: Incremento aritmético variable (lista de incrementos).
            lista_incrementos = factores['lista_incrementos']
            # Ejemplo: lista_incrementos=[500, 300] → 500 € y luego 300 €.
            # Convertimos saltos_incrementos a enteros.
            saltos_incrementos = [int(float(s)) for s in factores['saltos_incrementos']]
            # Ejemplo: saltos_incrementos=[5] → el incremento cambia en el año 5.

            # Generamos una lista de incrementos hasta anio_actuarial.
            incrementos_completos = []
            t_actual = 0
            max_t = max(0, anio_actuarial)
            # Ejemplo: anio_actuarial=6 → max_t=6.
            
            # Iteramos sobre los saltos para construir la lista de incrementos.
            for i, salto in enumerate(saltos_incrementos):
                if i >= len(lista_incrementos):
                    break
                if t_actual >= max_t:
                    break
                num_repeticiones = max(0, int(salto - t_actual))
                if salto > max_t:
                    num_repeticiones = max(0, int(max_t - t_actual))
                incrementos_completos.extend([lista_incrementos[i]] * num_repeticiones)
                # Ejemplo: salto=5, t_actual=0 → [500, 500, 500, 500, 500].
                t_actual = salto

            # Calculamos C_k según anio_actuarial.
            if anio_actuarial <= 0:
                # Si anio_actuarial <= 0, no hay incremento.
                return capital / fracciones_por_anio  # Primer año sin incremento.
            else:
                # Sumamos todos los incrementos para obtener el incremento acumulado.
                incremento_acumulado = sum(incrementos_completos)
                # Ejemplo: incrementos_completos=[500, 500, ..., 300] → incremento_acumulado = 500*5 + 300.
                # C_k = (capital + incremento_acumulado) / fracciones_por_anio.
                return (capital + incremento_acumulado) / fracciones_por_anio
        else:
            # Si no se proporcionan los parámetros necesarios, lanzamos un error.
            raise ValueError("Para tipo 'aritmetico', se requiere 'h' o 'lista_incrementos' con 'saltos_incrementos'")
    else:
        # Si no hay incremento (factores['tipo'] es None), devolvemos el capital dividido por las fracciones.
        # Ejemplo: capital=15000, fracciones_por_anio=12 → C_k = 15000/12 = 1250.
        return capital / fracciones_por_anio  # Sin incremento, capital dividido por fracciones por año.

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

def renta_geometrica(tipo_renta, edad_renta, capital, temporalidad, diferimiento=None,
                     interes=None, lista_intereses=None, tabla_generacion=None,
                     lista_factores=None, saltos_factores=None, fracciones_por_anio=1):
    # Determinar duración máxima
    omega = 120
    if temporalidad is None:
        max_anios = omega - edad_renta  # Corrección previa: no restar diferimiento
    else:
        max_anios = temporalidad
    
    # Generar tabla base con tiempos
    tabla = pd.DataFrame(columns=['k', 't', 't_relativo', 'k p_x'])
    idx = 0
    
    if tipo_renta.lower() == 'prepagable':
        for k in range(max_anios + 1):
            t = k
            if t < (diferimiento or 0):
                continue
            t_relativo = t - (diferimiento or 0)
            k_absoluto = t
            val_medio = tpx(edad_renta, t, tabla_generacion, fracciones_por_anio)
            tabla.loc[idx] = [k_absoluto, t, t_relativo, val_medio]
            idx += 1
    else:  # pospagable
        for k in range(max_anios + 1):
            t = k + 1
            if t <= (diferimiento or 0):
                continue
            t_relativo = t - (diferimiento or 0)
            k_absoluto = t
            val_medio = tpx(edad_renta, t, tabla_generacion, fracciones_por_anio)
            tabla.loc[idx] = [k_absoluto, t, t_relativo, val_medio]
            idx += 1
    
    # Generar lista_intereses si no está proporcionada
    if lista_intereses is None:
        max_t = int(tabla['t'].max()) + 1
        lista_intereses = [0] + [interes] * max_t

    # Calcular C_k
    if lista_factores and saltos_factores:
        # Incremento geométrico variable
        factores_completos = []
        t_actual = 0
        for i, salto in enumerate(saltos_factores):
            if i >= len(lista_factores):
                break
            factores_completos.extend([lista_factores[i]] * (salto - t_actual))
            t_actual = salto
        factores_completos.extend([lista_factores[-1]] * (int(tabla['t_relativo'].max()) + 1 - t_actual))
        
        C_k = []
        for t in tabla['t_relativo']:
            k_entero = int(t) - 1 if tipo_renta.lower() == 'pospagable' else int(t)
            if k_entero < 0:
                C_k.append(capital)
            else:
                factor_acumulado = math.prod(factores_completos[:k_entero])
                C_k.append(capital * factor_acumulado)
        tabla['C_k'] = C_k
    else:
        # Incremento geométrico fijo (corrección previa)
        q = lista_factores[0] if lista_factores else 1.0
        if tipo_renta.lower() == 'pospagable':
            tabla['C_k'] = capital * (q ** (tabla['t_relativo'] - 1))
        else:
            tabla['C_k'] = capital * (q ** tabla['t_relativo'])

    # Calcular v^k
    tabla['v^k'] = tabla['t'].apply(lambda t: v(lista_intereses, t, fracciones_por_anio))
    
    # Calcular valor actual
    tabla['k p_x * C_k * v^k'] = tabla['k p_x'] * tabla['C_k'] * tabla['v^k']
    
    # Sumatorio y ajuste para prepagable
    sumatorio = tabla['k p_x * C_k * v^k'].sum()
    if tipo_renta.lower() == "prepagable":
        ajuste_prepagable = (1 + lista_intereses[1]) if len(lista_intereses) > 1 else (1 + interes)
        sumatorio = sumatorio * ajuste_prepagable
    
    valor_renta = sumatorio * capital / capital  # Normalización (si aplica)
    
    return sumatorio, valor_renta, tabla

#OTRA NUEVA FUNCION,ESTAMOS LLENO DE FUNCIONES 
def renta_aritmetica(tipo_renta, edad_renta, capital, temporalidad, diferimiento=None,
                     interes=None, lista_intereses=None, tabla_generacion=None,
                     incremento_fijo=0, lista_incrementos=None, saltos_incrementos=None,
                     fracciones_por_anio=1):
    # Determinar duración máxima
    omega = 120
    if temporalidad is None:
        max_anios = omega - edad_renta  # Corrección previa
    else:
        max_anios = temporalidad
    
    # Generar tabla base con tiempos
    tabla = pd.DataFrame(columns=['k', 't', 't_relativo', 'k p_x'])
    idx = 0
    
    if tipo_renta.lower() == 'prepagable':
        for k in range(max_anios + 1):
            t = k
            if t < (diferimiento or 0):
                continue
            t_relativo = t - (diferimiento or 0)
            k_absoluto = t
            val_medio = tpx(edad_renta, t, tabla_generacion, fracciones_por_anio)
            tabla.loc[idx] = [k_absoluto, t, t_relativo, val_medio]
            idx += 1
    else:  # pospagable
        for k in range(max_anios + 1):
            t = k + 1
            if t <= (diferimiento or 0):
                continue
            t_relativo = t - (diferimiento or 0)
            k_absoluto = t
            val_medio = tpx(edad_renta, t, tabla_generacion, fracciones_por_anio)
            tabla.loc[idx] = [k_absoluto, t, t_relativo, val_medio]
            idx += 1
    
    # Generar lista_intereses si no está proporcionada
    if lista_intereses is None:
        max_t = int(tabla['t'].max()) + 1
        lista_intereses = [0] + [interes] * max_t

    # Calcular C_k
    if lista_incrementos and saltos_incrementos:
        # Incremento aritmético variable
        incrementos_completos = []
        t_actual = 0
        for i, salto in enumerate(saltos_incrementos):
            if i >= len(lista_incrementos):
                break
            incrementos_completos.extend([lista_incrementos[i]] * (salto - t_actual))
            t_actual = salto
        incrementos_completos.extend([lista_incrementos[-1]] * (int(tabla['t_relativo'].max()) + 1 - t_actual))
        
        C_k = []
        for t in tabla['t_relativo']:
            k_entero = int(t) - 1 if tipo_renta.lower() == 'pospagable' else int(t)
            if k_entero < 0:
                C_k.append(capital)
            else:
                suma_incrementos = sum(incrementos_completos[:k_entero])
                C_k.append(capital + suma_incrementos)
        tabla['C_k'] = C_k
    else:
        # Incremento aritmético fijo (corrección previa)
        if tipo_renta.lower() == 'pospagable':
            tabla['C_k'] = capital + incremento_fijo * (tabla['t_relativo'] - 1)
        else:
            tabla['C_k'] = capital + incremento_fijo * tabla['t_relativo']
    
    # Calcular v^k
    tabla['v^k'] = tabla['t'].apply(lambda t: v(lista_intereses, t, fracciones_por_anio))
    
    # Calcular valor actual
    tabla['k p_x * C_k * v^k'] = tabla['k p_x'] * tabla['C_k'] * tabla['v^k']
    
    # Sumatorio y ajuste para prepagable
    sumatorio = tabla['k p_x * C_k * v^k'].sum()
    if tipo_renta.lower() == "prepagable":
        ajuste_prepagable = (1 + lista_intereses[1]) if len(lista_intereses) > 1 else (1 + interes)
        sumatorio = sumatorio * ajuste_prepagable
    
    valor_renta = sumatorio * capital / capital  # Normalización (si aplica)
    
    return sumatorio, valor_renta, tabla

def calcular_renta_fraccionada(tabla_flujos, tipo_renta, capital, factores, fracciones_por_anio):
    """
    Calcula la renta fraccionada para todas las combinaciones posibles.
    Retorna la tabla y el valor actuarial (sumatorio).
    """
    if None in [capital, fracciones_por_anio]:
        raise ValueError("Parámetros inválidos: capital o fracciones no pueden ser None")
    if 'interes' not in factores and 'lista_intereses' not in factores:
        raise ValueError("Debe proporcionarse una tasa de interés fija o variable")

    lista_intereses = factores.get('lista_intereses')
    if lista_intereses is None:
        max_t = int(tabla_flujos['t'].max()) + 1
        lista_intereses = [0] + [factores['interes']] * max_t

    tabla = tabla_flujos.copy()
    
    if 'diferimiento' not in factores:
        diferimiento = tabla_flujos['t'].min() - tabla_flujos['t_relativo'].min()
        factores['diferimiento'] = int(diferimiento)
    
    tabla['C_k'] = [calcular_ck(row['t_relativo'], row['k'], tipo_renta, capital, factores, fracciones_por_anio) 
                    for _, row in tabla.iterrows()]

    if tabla['k p_x'].isnull().any():
        raise ValueError("La tabla contiene valores None en 'k p_x'")

    # Pasar tipo_renta a la función v()
    tabla['v^k'] = tabla['t'].apply(lambda t: v(lista_intereses, t, fracciones_por_anio, tipo_renta))
    tabla['valor_actual'] = tabla['C_k'] * tabla['k p_x'] * tabla['v^k']
    
    sumatorio = tabla['valor_actual'].sum()
    
    return tabla, sumatorio