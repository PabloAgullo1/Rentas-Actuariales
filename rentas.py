import autom_tablas as at
import pandas as pd

#i = int(input("Tipo de interes en porcentaje:"))/100
#n = int(input("Número de años de la renta:")) #Numero de años de duración de la renta

def v(i,n):
    return (1+ i)**(-n)

def tpx(x, t = 1):
    '''
    La función tpx(x+t, t) recibe la edad x y el año t.
    Devuelve la probabilidad de que un individuo con x años recien cumplidos
    sobreviva x + t años más.
    
    Si no se especifica el año t, se asume que es 1.
    '''
    l_x = None
    l_x_mas_t = None
    
    for i in range(0, len(at.tabla_generacion["x+t"])):
        if at.tabla_generacion["x+t"][i] == x:
            l_x = at.tabla_generacion["lx"][i]
    
    for i in range(0, len(at.tabla_generacion["x+t"])):
        if at.tabla_generacion["x+t"][i] == x + t:
            l_x_mas_t = at.tabla_generacion["lx"][i]
    
    if l_x is None or l_x_mas_t is None:
        raise ValueError("Edad x o x+t no encontrada en la tabla de mortalidad")
    
    return l_x_mas_t / l_x

def tqx(tpx):
    return 1 - tpx

#def esperanza_vida(x):
    '''
    La función esperanza_vida(x) recibe la edad x.
    Devuelve la esperanza de vida completa de un individuo con x años recien cumplidos
    en el año t.
    
    '''
    sum_tpx = 0
    for i in range(x, len(at.tabla_generacion["x+t"]-x-1)): #Hasta la edad omega - x - 1
        sum_tpx += tpx(x, i)
        
    return 1/2 + sum_tpx

def tqx(tpx):
    return 1 - tpx

print(tpx(43,22))
print(tqx(tpx(43,7))) #Ejemplos del libro pagina 49 por comprobación.
