import autom_tablas as at
import pandas as pd

interes = int(input("Tipo de interes en porcentaje:"))/100
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

#print(tpx(43,22))
#print(tqx(tpx(43,7))) #Ejemplos del libro pagina 49 por comprobación.

 
#MACROFUNCION!!!
#Quedan establecer los posibles errores (ValueError)
#Falta hacer comprobacón

tipo_renta = input("Introduce el tipo de renta (prepagable / pospagable): ")
edad_renta = int(input("Edad al momento de contratación de la renta: "))

capital = float(input("Introduce el capital a asegurar: "))
temporalidad = int(input("La renta es vitalicia (0) o temporal (1): "))
if temporalidad == 0:
        temporalidad = None
elif temporalidad == 1:
        temporalidad = int(input("Duración de la renta: "))
else:
        raise ValueError("El valor debe ser '0' para vitalicia o '1' para temporal")

diferimiento = input("Diferimiento en años (True o si no hay pulsa enter): ") or None


#Creamos la clase renta, de la cual hemos definido sus parámetros previamente

def renta(tipo_renta, edad_renta, capital, temporalidad, diferimiento):
    if tipo_renta == "prepagable": 
        if diferimiento == None: #Renta prepagable, anual, inmediata
            sumatorio = 1
            if temporalidad == None: #Renta vitalicia
                
                w_menosx_menos = int(at.tabla_generacion.iloc[-1]["x+t"] - edad_renta)

                for i in range(1, w_menosx):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else: #Renta temporal
                for i in range(1, temporalidad): #Seria hasta n menos 1 pero Python no coge el ultimo valor
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
        else: #Renta prepagable, anual, diferida
            sumatorio = 0
            if temporalidad == None:

                w_menosx = int(at.tabla_generacion.iloc[-1]["x+t"] - edad_renta - 1)
                
                for i in range(diferimiento, w_menosx): #Vitalicia
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:
                for i in range(diferimiento, temporalidad): #Temporal
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk

    if tipo_renta == "pospagable": 
        if diferimiento == None: #Renta pospagable, anual, inmediata
            sumatorio = 0
            if temporalidad == None:
                
                w_menosx = int(at.tabla_generacion.iloc[-1]["x+t"] - edad_renta - 1)

                for i in range(1, w_menosx):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:
                for i in range(1, temporalidad + 1):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
        else:
            sumatorio = 0
            if temporalidad == None:

                w_menosx = int(at.tabla_generacion.iloc[-1]["x+t"] - edad_renta - 1)
                for i in range(diferimiento + 1, w_menosx):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:
                for i in range(1, temporalidad + 1):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
    return float(sumatorio), float(capital * sumatorio)

    
renta_ejemplo = renta(tipo_renta, edad_renta, capital, temporalidad, diferimiento)
print(renta_ejemplo)
