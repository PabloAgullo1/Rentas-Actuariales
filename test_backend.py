from backend import tabla_gen, hojas, renta, tabla_gen  # Importa la función y el diccionario de tablas

def mostrar_tabla_mortalidad():  
    # Pedir al usuario que seleccione una tabla
    nombre = "PERF2000P"   
    año_nacimiento = 1955
    resultado = tabla_gen(año_nacimiento, nombre)
    print(f"\nTabla generacional para nacidos en {año_nacimiento}:")
    print(resultado)

""" tipo_renta (str): Tipo de renta ("prepagable" o "pospagable").
        edad_renta (int): Edad al momento de contratación.
        capital (float): Capital a asegurar.
        temporalidad (int or None): Duración de la renta (None si es vitalicia).
        diferimiento (int or None): Período de diferimiento (None si es inmediata).
        interes (float): Tasa de interés (en decimal, ej. 0.03 para 3%).
        tabla_generacion (pd.DataFrame): Tabla generacional con columnas 'x+t', 'lx'. """

def test_renta():
    # Datos de prueba
    tipo_renta = "pospagable"
    edad_renta = 50
    capital = 20000
    temporalidad = None
    diferimiento = None
    interes = 0.03
    tabla_cargada = mostrar_tabla_mortalidad()

    # Llamar a la función renta y obtener el resultado
    sumatorio, valor_renta = renta(tipo_renta, edad_renta, capital, temporalidad,
                                   diferimiento, interes, tabla_generacion=tabla_gen(1955,"PERF2000P"))

test_renta()