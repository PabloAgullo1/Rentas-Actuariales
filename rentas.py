import autom_tablas as at
import pandas as pd

<<<<<<< Updated upstream
interes = int(input("Tipo de interes en porcentaje:"))/100
#n = int(input("Número de años de la renta:")) #Numero de años de duración de la renta

def v(i,n):
=======
#MODO_DEV sirve para hacer pruevas sin tener que meter los datos cada vez. Una vez listo, se eliminará.
MODO_DEV = Trueif MODO_DEV:
    interes = 0.035
    tipo_renta = "pospagable"
    edad_renta = 44
    capital = 25000
    temporalidad = None
    diferimiento = 21
else:
    interes = int(input("Tipo de interes en porcentaje:"))/100
    tipo_renta = input("Introduce el tipo de renta (prepagable / pospagable): ")
    edad_renta = int(input("Edad al momento de contratación de la renta: "))

    capital = float(input("Introduce el capital a asegurar: "))
    temporalidad = int(input("Temporalidad de la renta (en caso de vitalicia pulse enter): ")) or None
    diferimiento = input("Diferimiento en años (True o si no hay pulsa enter): ") or None

def v(i, n):
>>>>>>> Stashed changes
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
        #sum_tpx += tpx(x, i)
        
    return 1/2 + sum_tpx

#def tqx(tpx):
    #return 1 - tpx

#print(tpx(43,22))
#print(tqx(tpx(43,7))) #Ejemplos del libro pagina 49 por comprobación.


""" 
MACROFUNCION!!!
Quedan establecer los posibles errores (ValueError)
Falta hacer comprobacón
"""
tipo_renta = input("Introduce el tipo de renta (prepagable / pospagable): ")
edad_renta = int(input("Edad al momento de contratación de la renta: "))

capital = float(input("Introduce el capital a asegurar: "))
temporalidad = int(input("La renta es vitalicia (0) o temporal (1): "))
if temporalidad == 0:
        temporalidad = None
elif temporalidad == 1:
        temporalidad = input("Duración de la renta: ")
else:
        raise ValueError("El valor debe ser '0' para vitalicia o '1' para temporal")

diferimiento = input("Diferimiento en años (True o si no hay pulsa enter): ") or None


#Creamos la clase renta, de la cual hemos definido sus parámetros previamente

<<<<<<< Updated upstream
class Renta():

    def __init__(self, tipo_renta, edad_renta, capital, temporalidad, diferimiento):
        self.tipo_renta = tipo_renta
        self.edad_renta = edad_renta

        self.capital = capital
        self.temporalidad = temporalidad
        self.diferimiento = diferimiento

    def prepa(self): 
=======
def renta(tipo_renta, edad_renta, capital, temporalidad, diferimiento, interes):
    """
    Calcula el valor actual actuarial y el valor de la renta actuarial.
    
    Args:
        tipo_renta (str): Tipo de renta ("prepagable" o "pospagable").
        edad_renta (int): Edad al momento de contratación.
        capital (float): Capital a asegurar.
        temporalidad (int or None): Duración de la renta (None si es vitalicia).
        diferimiento (int or None): Período de diferimiento (None si es inmediata).
        interes (float): Tasa de interés (en decimal, ej. 0.03 para 3%).
    
    Returns:
        tuple: (sumatorio, valor_renta), donde sumatorio es el valor actual actuarial
               y valor_renta es el valor de la renta actuarial (capital * sumatorio).
    """
    tipo_renta = tipo_renta.lower()
    if tipo_renta not in ["prepagable", "pospagable"]:
        raise ValueError("Tipo de renta no válido. Debe ser 'prepagable' o 'pospagable'.")
    
    #Determminar la edad máxima (omega) de la tabla de mortalidad
    w_menosx = int(at.tabla_generacion["x+t"].iloc[-1]) - edad_renta 

    if tipo_renta == "prepagable": 
>>>>>>> Stashed changes
        if diferimiento == None: #Renta prepagable, anual, inmediata
            sumatorio = 1.0
            if temporalidad == None: #Renta vitalicia
<<<<<<< Updated upstream
                
                w_menosx_menos1 = at.tabla_generacion["x+t"].iloc[-1] - edad_renta - 1

                for i in range(1, w_menosx_menos1):
=======
                for i in range(1, w_menosx):
>>>>>>> Stashed changes
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else: #Renta temporal
<<<<<<< Updated upstream
                for i in range(1, temporalidad - 1):
=======
                for i in range(1, int(temporalidad)):
>>>>>>> Stashed changes
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
        else: #Renta prepagable, anual, diferida
<<<<<<< Updated upstream
            sumatorio = 0
            if temporalidad == None:

                w_menosx_menos1 = at.tabla_generacion["x+t"].iloc[-1] - edad_renta - 1
                
                for i in range(diferimiento, w_menosx_menos1): #Vitalicia
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:
                for i in range(diferimiento, temporalidad - 1): #Temporal
=======
            sumatorio = 0.0
            diferimiento = int(diferimiento)
            if temporalidad is None: #Renta vitalicia
                #w_menosx = int(at.tabla_generacion.iloc[-1]["x+t"] - edad_renta - 1)
                for i in range(diferimiento, w_menosx): #Vitalicia
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else: #Renta temporal
                for i in range(diferimiento, int(temporalidad) + diferimiento): #Temporal
>>>>>>> Stashed changes
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
        return "El valor actual actuarial es " + sumatorio + "\n" "Y el valor de la renta actuarial es " + capital * sumatorio

<<<<<<< Updated upstream
    def pospa(self): 
        if diferimiento == None: #Renta pospagable, anual, inmediata
            sumatorio = 0
            if temporalidad == None:
                
                w_menosx_menos1 = int(at.tabla_generacion.iloc[-1]["x+t"] - edad_renta - 1)

                for i in range(1, w_menosx_menos1):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:
                for i in range(1, temporalidad):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
        else:
            sumatorio = 0
            if temporalidad == None:

                w_menosx_menos1 = int(at.tabla_generacion.iloc[-1]["x+t"] - edad_renta - 1)
                for i in range(diferimiento + 1, w_menosx_menos1):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else:
                for i in range(1, temporalidad):
=======
    if tipo_renta == "pospagable": 
        if diferimiento is None: #Renta pospagable, anual, inmediata
            sumatorio = 0.0
            if temporalidad is None: #Renta vitalicia
                #w_menosx = int(at.tabla_generacion.iloc[-1]["x+t"] - edad_renta - 1)
                for i in range(1, w_menosx):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else: #Renta temporal
                for i in range(1, temporalidad + 1):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
        else: #Renta pospagable, anual, diferida
            sumatorio = 0.0
            diferimiento = int(diferimiento)
            if temporalidad is None: #Renta vitalicia
                #w_menosx = int(at.tabla_generacion.iloc[-1]["x+t"] - edad_renta - 1)
                for i in range(diferimiento + 1, w_menosx):
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
            else: #Renta temporal
                for i in range(diferimiento + 1, int(temporalidad) + diferimiento + 1):
>>>>>>> Stashed changes
                    val_medio = tpx(edad_renta, i)
                    vk = v(interes, i)
                    sumatorio += val_medio * vk
        return float(sumatorio), float(capital * sumatorio)

    
renta = Renta(tipo_renta, edad_renta, capital, temporalidad, diferimiento)
renta_anual = renta.pospa()
print(renta_anual)