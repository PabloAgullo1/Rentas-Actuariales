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
    
def generar_tabla_flujos(tabla_generacion, edad_renta, diferimiento, tipo_renta, temporalidad, fracciones_por_anio=1):
    """
    Genera tabla de flujos para cálculos actuariales.
    - k representa el año actuarial (inicia en diferimiento, e.g., 17).
    - t y t_relativo reflejan los subperíodos fraccionados.
    - j representa el subperíodo dentro del año (0 a 11 para prepagable, 1 a 12 para pospagable).
    """
    omega = 120
    if temporalidad is None:
        max_anios = omega - edad_renta - 1
    else:
        max_anios = temporalidad
    
    tabla = pd.DataFrame(columns=['k', 't', 't_relativo', 'j', 'k p_x'])
    idx = 0
    
    for anio in range(max_anios):
        k = (diferimiento or 0) + anio  # k inicia en 17
        for f in range(fracciones_por_anio):
            if tipo_renta.lower() == 'prepagable':
                t = k + f / fracciones_por_anio  # 17.0000, 17.0833, ..., 17.9167
                j = f  # 0, 1, ..., 11
            else:  # pospagable
                t = k + (f + 1) / fracciones_por_anio  # 17.0833, 17.1667, ..., 18.0000
                j = f + 1  # 1, 2, ..., 12
            
            # Ajustar el filtro para prepagable
            if tipo_renta.lower() == 'prepagable':
                if t < (diferimiento or 0):
                    continue
            else:
                if t <= (diferimiento or 0):
                    continue
            
            t_relativo = t - (diferimiento or 0)
            val_medio = tpx(edad_renta, t, tabla_generacion, fracciones_por_anio)
            tabla.loc[idx] = [k, t, t_relativo, j, val_medio]
            idx += 1
    
    # Ordenar la tabla por k, t para asegurar el orden correcto
    tabla = tabla.sort_values(by=['k', 't']).reset_index(drop=True)
    return tabla

def calcular_ck(t_relativo, k, tipo_renta, capital, factores, fracciones_por_anio):
    """
    Calcula el valor de C_k para un tiempo relativo dado.
    Soporta todas: prepagable/pospagable, aritmético/geométrico.
    """
    # Asegurar que k y t_relativo sean tratados como valores numéricos
    k = int(float(k))  # Convertir k a entero
    t_relativo = float(t_relativo)  # Asegurar que t_relativo sea float
    
    # Determinar el año actuarial relativo al inicio de los pagos
    if tipo_renta.lower() == 'pospagable':
        diferimiento = int(float(factores.get('diferimiento', 0)))  # 17
        anio_actuarial = k - diferimiento  # Ajuste: quitar el -1
    else:
        anio_actuarial = int(t_relativo)
    
    if factores['tipo'] == 'geometrico':
        if 'q' in factores:
            if tipo_renta.lower() == 'pospagable':
                return (capital * (factores['q'] ** max(0, anio_actuarial))) / fracciones_por_anio
            else:
                return (capital * (factores['q'] ** t_relativo)) / fracciones_por_anio
        elif 'lista_factores' in factores and 'saltos_factores' in factores:
            lista_factores = factores['lista_factores']
            # Convertir saltos_factores a enteros
            saltos_factores = [int(float(s)) for s in factores['saltos_factores']]
            
            # Generar lista de factores hasta anio_actuarial
            factores_completos = []
            t_actual = 0
            max_t = max(0, anio_actuarial)  # Número de años con incremento
            for i, salto in enumerate(saltos_factores):
                if i >= len(lista_factores):
                    break
                if t_actual >= max_t:
                    break
                num_repeticiones = max(0, int(salto - t_actual))
                if salto > max_t:
                    num_repeticiones = max(0, int(max_t - t_actual))
                factores_completos.extend([lista_factores[i]] * num_repeticiones)
                t_actual = salto
            
            # No añadir más factores después de max_t
            if anio_actuarial <= 0:
                return capital / fracciones_por_anio  # Primer año sin incremento
            else:
                factor_acumulado = math.prod(factores_completos)
                return (capital * factor_acumulado) / fracciones_por_anio
        else:
            raise ValueError("Para tipo 'geometrico', se requiere 'q' o 'lista_factores' con 'saltos_factores'")
    elif factores['tipo'] == 'aritmetico':
        if 'h' in factores:
            if tipo_renta.lower() == 'pospagable':
                return (capital + (max(0, anio_actuarial) * factores['h'])) / fracciones_por_anio
            else:
                return (capital + (t_relativo * factores['h'])) / fracciones_por_anio
        elif 'lista_incrementos' in factores and 'saltos_incrementos' in factores:
            lista_incrementos = factores['lista_incrementos']
            # Convertir saltos_incrementos a enteros
            saltos_incrementos = [int(float(s)) for s in factores['saltos_incrementos']]
            
            incrementos_completos = []
            t_actual = 0
            max_t = max(0, anio_actuarial)
            for i, salto in enumerate(saltos_incrementos):
                if i >= len(lista_incrementos):
                    break
                if t_actual >= max_t:
                    break
                num_repeticiones = max(0, int(salto - t_actual))
                if salto > max_t:
                    num_repeticiones = max(0, int(max_t - t_actual))
                incrementos_completos.extend([lista_incrementos[i]] * num_repeticiones)
                t_actual = salto
            
            if anio_actuarial <= 0:
                return capital / fracciones_por_anio  # Primer año sin incremento
            else:
                incremento_acumulado = sum(incrementos_completos)
                return (capital + incremento_acumulado) / fracciones_por_anio
        else:
            raise ValueError("Para tipo 'aritmetico', se requiere 'h' o 'lista_incrementos' con 'saltos_incrementos'")
    else:
        return capital / fracciones_por_anio  # Sin incremento, capital dividido por fracciones por año

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