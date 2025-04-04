import autom_tablas

i = int(input("Tipo de interes:"))/100
duracion = int(input("Duración:"))

def v(i,duracion):
    return (1+ i)**(-duracion)

def kpx():
    tabla_autom = autom_tablas.tabla_gen()
    return tabla_autom[tabla_autom["x+t"] == (autom_tablas.edad_inicio + duracion)].lx / \
           tabla_autom[tabla_autom["x+t"] == autom_tablas.edad_inicio].lx
print(kpx())

