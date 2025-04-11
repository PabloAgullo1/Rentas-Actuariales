from backend import tabla_gen, hojas, renta, tabla_gen, interpolar_lx_mensual  # Importa la función y el diccionario de tablas

def mostrar_tabla_mortalidad():  
    # Pedir al usuario que seleccione una tabla
    nombre = "PERF2000P"   
    año_nacimiento = 1970
    resultado = tabla_gen(año_nacimiento, nombre)
    print(f"\nTabla generacional para nacidos en {año_nacimiento}:")
    return resultado, año_nacimiento

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
    sumatorio, valor_renta, tabla_FPP = renta(tipo_renta, edad_renta, capital, temporalidad,
                                   diferimiento, interes, tabla_generacion=tabla_gen(1955,"PERF2000P"))
    

def interpolacion():
    tablilla, year = mostrar_tabla_mortalidad()
    tabla_interpolada = interpolar_lx_mensual(tablilla, year)
    return tabla_interpolada

interpolacion()

