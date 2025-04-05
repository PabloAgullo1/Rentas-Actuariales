import pandas as pd
import numpy as np
import math

# Cargar todas las hojas en un diccionario de DataFrames
excel_tablas = "Tablas PER 2000 y 2020.xlsx" 
hojas = pd.read_excel(excel_tablas, sheet_name=None, header=1)  # Cargar todas las pestañas
xlsx = pd.ExcelFile(excel_tablas) # Cargar el archivo Excel y sirve para obtener los nombres de las pestañas

# Obtener los nombres de todas las pestañas
nombres_pestañas = xlsx.sheet_names

nombre_tabla = input("¿Qué Tabla de Mortalidad quieres usar? Elige entre:\n"
    "'PERM2000C', 'PERF2000C', 'PERM2000P', 'PERF2000P',\n"
    "'PERM_2020_Indiv_2Orden', 'PERM_2020_Indiv_1Orden',\n"
    "'PERF_2020_Indiv_2Orden', 'PERF_2020_Indiv_1Orden',\n"
    "'PERM_2020_Colectivos_2Orden', 'PERM_2020_Colectivos_1Orden',\n"
    "'PERF_2020_Colectivos_2Orden', 'PERF_2020_Colectivos_1Orden': ")

g = int(input("Introduce el año de nacimiento del asegurado/a: "))



def generacion(g, nombre_tabla):
    '''
    La función recibe el año de nacimiento del asegurado/a y el nombre de la tabla de mortalidad.
    Devuelve la edad x+t del asegurado/a en función de la tabla de mortalidad seleccionada.
    '''
         
    if nombre_tabla in ['PERM2000C',
                            'PERF2000C',
                            'PERM2000P',
                            'PERF2000P',]:
        x_mas_t = 2000 - g

        if g > 2000:
            raise ValueError("La generación no puede ser mayor a 2000.")

        
    
    elif nombre_tabla in ['PERM_2020_Indiv_2Orden',
                            'PERM_2020_Indiv_1Orden',
                            'PERF_2020_Indiv_2Orden',
                            'PERF_2020_Indiv_1Orden',
                            'PERM_2020_Colectivos_2Orden',
                            'PERM_2020_Colectivos_1Orden',
                            'PERF_2020_Colectivos_2Orden',
                            'PERF_2020_Colectivos_1Orden']:
        x_mas_t = 2012 - g

        if g > 2012:
            raise ValueError("La generación no puede ser mayor a 2012.")
 
    return x_mas_t



def q_x(qx, mejora, t):
    '''
    La función q_x recibe la probabilidad de muerte qx de la tabla de mortalidad y el factor de mejora de ésta
    Devuelve la probabilidad de muerte qx ajustada por el factor de mejora.
    '''
    return qx*math.exp(-mejora*t)

#Variable que se corresponde con la edad del individuo en el año base (primera edad x+t)
edad_inicio = generacion(g, nombre_tabla)


def tabla_gen():
    x_mas_t_list = list(range(edad_inicio, len(hojas[nombre_tabla]))) #Lista de edades x+t
    edad_t = list(range(0, len(x_mas_t_list))) #Lista de edades t

    # Crear un DataFrame vacío para almacenar los resultados
    resultados = pd.DataFrame(columns=['Edad', 'x+t'])
    resultados['x+t'] = x_mas_t_list # Asignar la lista de edades x+t al DataFrame
    resultados['Edad'] = edad_t  # Asignar la lista de edades al DataFrame


    qx_ajustado = [] # Lista para almacenar los valores de qx ajustados

    if hojas[nombre_tabla].shape[1] == 3:   # Comprobar si el número de columnas en el DataFrame es 3
        for i in range(edad_inicio, len(hojas[nombre_tabla])):
            qx_ajustado.append(q_x(hojas[nombre_tabla].iloc[i, 1], #Coge de la tabla original las qx+t tabla base
                                    hojas[nombre_tabla].iloc[i, 2], #Coge de la tabla original las mejoras
                                    i - edad_inicio)) # i - edad_inicio es el tiempo t
    elif hojas[nombre_tabla].shape[1] == 5: # Comprobar si el número de columnas en el DataFrame es 5 (Tablas 1er orden)
        for i in range(edad_inicio, len(hojas[nombre_tabla])):
            qx_ajustado.append(q_x(hojas[nombre_tabla].iloc[i, 2],
                                    hojas[nombre_tabla].iloc[i, 4],
                                    i - edad_inicio)) # i - edad_inicio es el tiempo t

    # Asignar la lista de qx ajustados al DataFrame
    resultados.insert(2, 'qx+t ajustado', qx_ajustado)

    resultados.set_index('Edad', inplace=True)  # Establecer la columna 'Edad' como índice (Hay que hacerlo aqui, si se hace antes da error)


    resultados['lx'] = 0
    resultados.loc[0, 'lx'] = 1000000  #Suponemos 1.000.000 de asegurados al inicio
    resultados['lx'] = resultados['lx'].astype(float)

    # Calculamos lx y dx fila por fila
    for i in range(1, len(resultados)):
        resultados.loc[i, 'lx'] = resultados.loc[i-1, 'lx'] * (1 - resultados.loc[i-1, 'qx+t ajustado'])

    resultados['dx'] = resultados['lx'] * resultados['qx+t ajustado']

    return resultados
print(tabla_gen())