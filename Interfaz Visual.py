import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from backend import *
import math

# Función para limpiar la tabla
def limpiar_tabla(tree):
    for item in tree.get_children():
        tree.delete(item)

def mostrar_tabla_con_incrementos(tabla_flujos, tree, fracciones_por_anio=1):
    limpiar_tabla(tree)
    
    if fracciones_por_anio == 1:
        tree["columns"] = ('k', 'k p_x', 'C_k', 'v^k', 'k p_x * C_k * v^k')
        tree.heading('k', text='k')
        tree.heading('k p_x', text='k p_x')
        tree.heading('C_k', text='C_k')
        tree.heading('v^k', text='v^k')
        tree.heading('k p_x * C_k * v^k', text='k p_x * C_k * v^k')
        
        for index, row in tabla_flujos.iterrows():
            tree.insert("", tk.END, values=(
                f"{row['k']:.2f}",
                f"{row['k p_x']:.6f}",
                f"{row['C_k']:.2f}",
                f"{row['v^k']:.6f}",
                f"{row['valor_actual']:.2f}"
            ))
    else:
        tree["columns"] = ('k', 'j', 'C_k_fraccion', 'v^k_fraccion', 'k_px_fraccion', 
                          'v_px_fraccion', 'C_px_vk_fraccion')
        tree.heading('k', text='k (año)')
        tree.heading('j', text=f'j/{fracciones_por_anio}')
        tree.heading('C_k_fraccion', text=f'C_k/{fracciones_por_anio}')
        tree.heading('v^k_fraccion', text=f'v^(k+j/{fracciones_por_anio})')
        tree.heading('k_px_fraccion', text=f'(k+j/{fracciones_por_anio}) p_x')
        tree.heading('v_px_fraccion', text=f'v^(k+j/{fracciones_por_anio}) * (k+j/{fracciones_por_anio}) p_x')
        tree.heading('C_px_vk_fraccion', text=f'C_k/{fracciones_por_anio} * (k+j/{fracciones_por_anio}) p_x * v^(k+j/{fracciones_por_anio})')
        
        for index, row in tabla_flujos.iterrows():
            j = row['j']
            k_entero = row['k']
            
            C_k_fraccion = row['C_k']
            v_px_fraccion = row['v^k'] * row['k p_x']
            C_px_vk_fraccion = row['valor_actual']
            
            print(f"k={k_entero}, j={j}, C_k={C_k_fraccion:.2f}")
            
            tree.insert("", tk.END, values=(
                f"{k_entero}",
                f"{j}",
                f"{C_k_fraccion:.2f}",
                f"{row['v^k']:.6f}",
                f"{row['k p_x']:.6f}",
                f"{v_px_fraccion:.6f}",
                f"{C_px_vk_fraccion:.6f}"
            ))

    for col in tree["columns"]:
        tree.column(col, width=100, anchor='center')

# Funciones para actualizar campos dinámicamente
def actualizar_campos_interes(event=None):
    if combo_tipo_interes.get() == "Fija":
        label_interes_fijo.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_interes_fijo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        label_intereses.grid_remove()
        entry_intereses.grid_remove()
        label_saltos.grid_remove()
        entry_saltos.grid_remove()
    else:
        label_interes_fijo.grid_remove()
        entry_interes_fijo.grid_remove()
        label_intereses.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_intereses.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        label_saltos.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        entry_saltos.grid(row=3, column=1, padx=5, pady=5, sticky="w")

def actualizar_campos_temporalidad(event=None):
    if combo_temporalidad.get() == "Temporal":
        label_duracion.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        entry_duracion.grid(row=3, column=1, padx=5, pady=5, sticky="w")
    else:
        label_duracion.grid_remove()
        entry_duracion.grid_remove()

def actualizar_campos_periodicidad(event=None):
    if combo_periodicidad.get() == "Fraccionada":
        label_fracciones.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        entry_fracciones.grid(row=5, column=1, padx=5, pady=5, sticky="w")
    else:
        label_fracciones.grid_remove()
        entry_fracciones.grid_remove()

def actualizar_campos_incrementos(event=None):
    seleccion = combo_tipo_incremento.get()
    if seleccion == "Sin incremento":
        label_factor_q.grid_remove()
        entry_factor_q.grid_remove()
        label_incremento_h.grid_remove()
        entry_incremento_h.grid_remove()
        label_incrementos.grid_remove()
        entry_incrementos.grid_remove()
        label_saltos_incrementos.grid_remove()
        entry_saltos_incrementos.grid_remove()
    elif seleccion == "Geométrico fijo":
        label_factor_q.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_factor_q.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        label_incremento_h.grid_remove()
        entry_incremento_h.grid_remove()
        label_incrementos.grid_remove()
        entry_incrementos.grid_remove()
        label_saltos_incrementos.grid_remove()
        entry_saltos_incrementos.grid_remove()
    elif seleccion == "Aritmético fijo":
        label_factor_q.grid_remove()
        entry_factor_q.grid_remove()
        label_incremento_h.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_incremento_h.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        label_incrementos.grid_remove()
        entry_incrementos.grid_remove()
        label_saltos_incrementos.grid_remove()
        entry_saltos_incrementos.grid_remove()
    elif seleccion == "Geométrico variable":
        label_factor_q.grid_remove()
        entry_factor_q.grid_remove()
        label_incremento_h.grid_remove()
        entry_incremento_h.grid_remove()
        label_incrementos.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_incrementos.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        label_saltos_incrementos.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        entry_saltos_incrementos.grid(row=3, column=1, padx=5, pady=5, sticky="w")
    elif seleccion == "Aritmético variable":
        label_factor_q.grid_remove()
        entry_factor_q.grid_remove()
        label_incremento_h.grid_remove()
        entry_incremento_h.grid_remove()
        label_incrementos.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_incrementos.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        label_saltos_incrementos.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        entry_saltos_incrementos.grid(row=3, column=1, padx=5, pady=5, sticky="w")

def actualizar_campos_tabla(event=None):
    seleccion = combo_tabla.get()
    if "UNISEX" in seleccion:
        label_prop_hombres.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        entry_prop_hombres.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        label_prop_mujeres.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        entry_prop_mujeres.grid(row=5, column=1, padx=5, pady=5, sticky="w")
    else:
        label_prop_hombres.grid_remove()
        entry_prop_hombres.grid_remove()
        label_prop_mujeres.grid_remove()
        entry_prop_mujeres.grid_remove()

# Función para validar entradas
def validar_entradas():
    try:
        # Validar año de nacimiento
        g = int(entry_anio_nacimiento.get())
        if g < 1900 or g > 2025:
            raise ValueError("Año de nacimiento debe estar entre 1900 y 2025.")

        # Validar edad actuarial
        edad_renta = int(entry_edad_renta.get())
        if edad_renta < 0 or edad_renta > 120:
            raise ValueError("Edad actuarial debe estar entre 0 y 120.")

        # Validar cuantía inicial
        cuantia_inicial = float(entry_cuantia_inicial.get())
        if cuantia_inicial <= 0:
            raise ValueError("Cuantía inicial debe ser mayor a 0.")

        # Validar temporalidad
        if combo_temporalidad.get() == "Temporal":
            temporalidad = int(entry_duracion.get())
            if temporalidad <= 0:
                raise ValueError("Duración debe ser mayor a 0.")
        else:
            temporalidad = None

        # Validar diferimiento
        diferimiento = entry_diferimiento.get()
        if diferimiento:
            diferimiento = int(diferimiento)
            if diferimiento < 0:
                raise ValueError("Diferimiento debe ser no negativo.")
        else:
            diferimiento = None

        # Validar fracciones por año
        if combo_periodicidad.get() == "Fraccionada":
            fracciones_por_anio = int(entry_fracciones.get())
            if fracciones_por_anio not in [1, 2, 4, 12]:
                raise ValueError("Fracciones por año debe ser 1, 2, 4 o 12.")
        else:
            fracciones_por_anio = 1

        # Validar intereses
        if combo_tipo_interes.get() == "Fija":
            interes = float(entry_interes_fijo.get()) / 100
            if interes < 0:
                raise ValueError("Interés fijo no puede ser negativo.")
        else:
            intereses_input = entry_intereses.get().strip()
            saltos_input = entry_saltos.get().strip()
            if not intereses_input or not saltos_input:
                raise ValueError("Debe proporcionar tasas de interés y años de cambio.")
            intereses = [float(i.strip()) / 100 for i in intereses_input.split(",")]
            saltos = [int(s.strip()) for s in saltos_input.split(",")]
            if len(intereses) != len(saltos):
                raise ValueError("El número de tasas de interés y años de cambio debe ser igual.")
            if any(i < 0 for i in intereses):
                raise ValueError("Las tasas de interés no pueden ser negativas.")
            if not all(s1 < s2 for s1, s2 in zip(saltos[:-1], saltos[1:])):
                raise ValueError("Los años de cambio deben estar en orden ascendente.")
            if saltos[0] <= 0:
                raise ValueError("Los años de cambio deben ser mayores a 0.")

        # Validar incrementos
        seleccion_incremento = combo_tipo_incremento.get()
        if seleccion_incremento == "Geométrico fijo":
            factor_q = float(entry_factor_q.get()) / 100
            if factor_q < 0:
                raise ValueError("Incremento geométrico no puede ser negativo.")
        elif seleccion_incremento == "Aritmético fijo":
            incremento_h = float(entry_incremento_h.get())
            if incremento_h < 0:
                raise ValueError("Incremento aritmético no puede ser negativo.")
        elif seleccion_incremento in ["Geométrico variable", "Aritmético variable"]:
            incrementos_input = entry_incrementos.get().strip()
            saltos_inc_input = entry_saltos_incrementos.get().strip()
            if not incrementos_input or not saltos_inc_input:
                raise ValueError("Debe proporcionar incrementos y años de cambio.")
            incrementos = [float(i.strip()) for i in incrementos_input.split(",")]
            saltos_incrementos = [int(s.strip()) for s in saltos_inc_input.split(",")]
            if len(incrementos) != len(saltos_incrementos):
                raise ValueError("El número de incrementos y años de cambio debe ser igual.")
            if any(i < 0 for i in incrementos):
                raise ValueError("Los incrementos no pueden ser negativos.")
            if not all(s1 < s2 for s1, s2 in zip(saltos_incrementos[:-1], saltos_incrementos[1:])):
                raise ValueError("Los años de cambio de incrementos deben estar en orden ascendente.")
            if saltos_incrementos[0] <= 0:
                raise ValueError("Los años de cambio de incrementos deben ser mayores a 0.")

        # Validar proporciones para tablas unisex
        nombre_tabla = combo_tabla.get()
        if "UNISEX" in nombre_tabla:
            prop_hombres = float(entry_prop_hombres.get())
            prop_mujeres = float(entry_prop_mujeres.get())
            if prop_hombres < 0 or prop_mujeres < 0:
                raise ValueError("Los porcentajes de hombres y mujeres no pueden ser negativos.")
            if abs(prop_hombres + prop_mujeres - 100) > 1e-6:
                raise ValueError("Los porcentajes de hombres y mujeres deben sumar 100.")

        return True
    except ValueError as e:
        messagebox.showerror("Error de Validación", str(e))
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Error en la entrada: {str(e)}")
        return False

# Función para calcular
def calcular():
    if not validar_entradas():
        return

    try:
        # [Sección 1: Obtener parámetros básicos]
        g = int(entry_anio_nacimiento.get())
        nombre_tabla = combo_tabla.get()
        edad_renta = int(entry_edad_renta.get())
        temporalidad = combo_temporalidad.get()
        tipo_renta = combo_tipo_renta.get()
        cuantia_inicial = float(entry_cuantia_inicial.get())
        seleccion_incremento = combo_tipo_incremento.get()

        # Obtener proporciones para tablas unisex
        if "UNISEX" in nombre_tabla:
            prop_hombres = float(entry_prop_hombres.get())
            prop_mujeres = float(entry_prop_mujeres.get())
            w_male = prop_hombres / 100
            w_female = prop_mujeres / 100
        else:
            w_male = 0.5  # Valor por defecto (no se usa si no es unisex)
            w_female = 0.5

        # [Sección 2: Procesar temporalidad y diferimiento]
        if temporalidad == "Vitalicia":
            temporalidad = None
        elif temporalidad == "Temporal":
            temporalidad = int(entry_duracion.get())
            
        diferimiento = int(entry_diferimiento.get()) if entry_diferimiento.get() else None

        # [Sección 3: Configurar periodicidad]
        periodicidad = combo_periodicidad.get()
        if periodicidad == "Anual":
            fracciones_por_anio = 1
        else:
            fracciones_por_anio = int(entry_fracciones.get())

        # [Sección 4: Configurar intereses]
        tabla_generacion = tabla_gen(g, nombre_tabla, w_male, w_female)  # Pasar proporciones
        if combo_tipo_interes.get() == "Fija":
            interes = float(entry_interes_fijo.get()) / 100
            lista_intereses = None
        else:
            intereses = [float(i.strip()) / 100 for i in entry_intereses.get().split(",")]
            saltos = [int(s.strip()) for s in entry_saltos.get().split(",")]
            lista_intereses = funcion_intereses(intereses, saltos, edad_renta, tabla_generacion, duracion=temporalidad)
            interes = None

        # Columnas esperadas para tabla_flujos
        required_columns = ['k', 't', 't_relativo', 'k p_x', 'C_k', 'v^k', 'valor_actual']

        # [Sección 5: Lógica de cálculo principal]
        if fracciones_por_anio > 1:
            factores = {
                'tipo': None,
                'interes': interes if lista_intereses is None else None,
                'lista_intereses': lista_intereses
            }

            if seleccion_incremento == "Geométrico fijo":
                factores['tipo'] = 'geometrico'
                factores['q'] = 1 + float(entry_factor_q.get()) / 100
            elif seleccion_incremento == "Aritmético fijo":
                factores['tipo'] = 'aritmetico'
                factores['h'] = float(entry_incremento_h.get())
            elif seleccion_incremento == "Geométrico variable":
                factores['tipo'] = 'geometrico'
                incrementos = [float(i.strip()) / 100 for i in entry_incrementos.get().split(",")]
                saltos_incrementos = [int(s.strip()) for s in entry_saltos_incrementos.get().split(",")]
                factores['lista_factores'] = [1 + i for i in incrementos]
                factores['saltos_factores'] = saltos_incrementos
            elif seleccion_incremento == "Aritmético variable":
                factores['tipo'] = 'aritmetico'
                factores['lista_incrementos'] = [float(i.strip()) for i in entry_incrementos.get().split(",")]
                factores['saltos_incrementos'] = [int(s.strip()) for s in entry_saltos_incrementos.get().split(",")]
            else:
                factores['tipo'] = None

            tabla_flujos = generar_tabla_flujos(
                tabla_generacion, edad_renta, diferimiento or 0,
                tipo_renta, temporalidad, fracciones_por_anio
            )

            tabla_flujos, sumatorio = calcular_renta_fraccionada(
                tabla_flujos, tipo_renta, cuantia_inicial,
                factores, fracciones_por_anio
            )

            # Estandarizar columnas
            if 'k p_x * C_k * v^k' in tabla_flujos.columns:
                tabla_flujos['valor_actual'] = tabla_flujos['k p_x * C_k * v^k']
            if 'k' not in tabla_flujos.columns:
                tabla_flujos['k'] = tabla_flujos['t'].astype(int)
            if 't_relativo' not in tabla_flujos.columns:
                tabla_flujos['t_relativo'] = tabla_flujos['t'] - (diferimiento or 0)

            # Prima única es el sumatorio de valor_actual
            prima_unica = sumatorio
            # Calcular valor actuarial unitario solo para rentas constantes
            valor_actuarial_unitario = sumatorio / cuantia_inicial if seleccion_incremento == "Sin incremento" else None

            # Mostrar resultados
            mostrar_tabla_con_incrementos(tabla_flujos, tree, fracciones_por_anio)
            if seleccion_incremento == "Sin incremento":
                resultado_label.config(
                    text=f"Valor actuarial unitario: {valor_actuarial_unitario:.6f}\n"
                         f"Prima única: {prima_unica:.2f} €",
                    fg="#030303"
                )
            else:
                resultado_label.config(
                    text=f"Prima única (sumatorio C_k * v^k * k p_x): {prima_unica:.2f} €",
                    fg="#030303"
                )
        else:
            if seleccion_incremento == "Geométrico fijo":
                factor_q = 1 + float(entry_factor_q.get()) / 100
                sumatorio, valor_renta, tabla_flujos = renta_geometrica(
                    tipo_renta, edad_renta, cuantia_inicial, temporalidad, diferimiento,
                    interes=interes, lista_intereses=lista_intereses,
                    tabla_generacion=tabla_generacion,
                    lista_factores=[factor_q], saltos_factores=None,
                    fracciones_por_anio=1
                )
            elif seleccion_incremento == "Aritmético fijo":
                incremento_h = float(entry_incremento_h.get())
                sumatorio, valor_renta, tabla_flujos = renta_aritmetica(
                    tipo_renta, edad_renta, cuantia_inicial, temporalidad, diferimiento,
                    interes=interes, lista_intereses=lista_intereses,
                    tabla_generacion=tabla_generacion,
                    incremento_fijo=incremento_h,
                    fracciones_por_anio=1
                )
            elif seleccion_incremento == "Geométrico variable":
                incrementos = [float(i.strip()) / 100 for i in entry_incrementos.get().split(",")]
                saltos_incrementos = [int(s.strip()) for s in entry_saltos_incrementos.get().split(",")]
                lista_factores = [1 + i for i in incrementos]
                sumatorio, valor_renta, tabla_flujos = renta_geometrica(
                    tipo_renta, edad_renta, cuantia_inicial, temporalidad, diferimiento,
                    interes=interes, lista_intereses=lista_intereses,
                    tabla_generacion=tabla_generacion,
                    lista_factores=lista_factores, saltos_factores=saltos_incrementos,
                    fracciones_por_anio=1
                )
            elif seleccion_incremento == "Aritmético variable":
                lista_incrementos = [float(i.strip()) for i in entry_incrementos.get().split(",")]
                saltos_incrementos = [int(s.strip()) for s in entry_saltos_incrementos.get().split(",")]
                sumatorio, valor_renta, tabla_flujos = renta_aritmetica(
                    tipo_renta, edad_renta, cuantia_inicial, temporalidad, diferimiento,
                    interes=interes, lista_intereses=lista_intereses,
                    tabla_generacion=tabla_generacion,
                    lista_incrementos=lista_incrementos, saltos_incrementos=saltos_incrementos,
                    fracciones_por_anio=1
                )
            else:  # "Sin incremento"
                sumatorio, valor_renta, tabla_flujos = renta_geometrica(
                    tipo_renta, edad_renta, cuantia_inicial, temporalidad, diferimiento,
                    interes=interes, lista_intereses=lista_intereses,
                    tabla_generacion=tabla_generacion,
                    lista_factores=[1.0],
                    fracciones_por_anio=1
                )

            # Estandarizar columnas
            if 'k p_x * C_k * v^k' in tabla_flujos.columns:
                tabla_flujos['valor_actual'] = tabla_flujos['k p_x * C_k * v^k']
            if 'k' not in tabla_flujos.columns:
                tabla_flujos['k'] = tabla_flujos['t'].astype(int)
            if 't_relativo' not in tabla_flujos.columns:
                tabla_flujos['t_relativo'] = tabla_flujos['t'] - (diferimiento or 0)

            # Prima única es el sumatorio de valor_actual
            prima_unica = sumatorio
            # Calcular valor actuarial unitario solo para rentas constantes
            valor_actuarial_unitario = sumatorio / cuantia_inicial if seleccion_incremento == "Sin incremento" else None

            # Mostrar resultados
            mostrar_tabla_con_incrementos(tabla_flujos, tree, fracciones_por_anio)
            if seleccion_incremento == "Sin incremento":
                resultado_label.config(
                    text=f"Valor actuarial unitario: {valor_actuarial_unitario:.6f}\n"
                         f"Prima única: {prima_unica:.2f} €",
                    fg="#030303"
                )
            else:
                resultado_label.config(
                    text=f"Prima única (sumatorio C_k * v^k * k p_x): {prima_unica:.2f} €",
                    fg="#030303"
                )

    except Exception as e:
        messagebox.showerror("Error de Cálculo", f"Error: {str(e)}")

# Configuración de la ventana principal
root = tk.Tk()
root.title("JUPAMA ACTUARIAL SOFTWARE")
root.geometry("1000x800")
root.configure(bg="#F1EFEC")

# Forzar el tema 'clam' para mejor control de estilos
style = ttk.Style()
style.theme_use('clam')

# Estilo general
label_style = {"bg": "#D4C9BE", "fg": "#030303", "font": ("Roboto", 11, "bold")}
entry_style = ttk.Style()
entry_style.configure("TEntry", fieldbackground="#FFFFFF", foreground="#030303", bordercolor="#123458", lightcolor="#123458")
combo_style = ttk.Style()
combo_style.configure("TCombobox", fieldbackground="#FFFFFF", foreground="#030303", background="#D4C9BE", bordercolor="#123458")

# Título principal
title_frame = tk.Frame(root, bg="#123458", bd=1, relief="flat")
title_frame.pack(fill="x")
title_label = tk.Label(title_frame, text="JUPAMA ACTUARIAL SOFTWARE", bg="#123458", fg="#FFFFFF", font=("Roboto", 18, "bold"))
title_label.pack(pady=10)

# Frame principal para entradas
input_frame = tk.Frame(root, bg="#D4C9BE", bd=1, relief="flat")
input_frame.pack(pady=10, padx=20, fill="x")

# Subframes para organizar los parámetros en columnas
left_frame = tk.Frame(input_frame, bg="#D4C9BE")
left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="n")
center_frame = tk.Frame(input_frame, bg="#D4C9BE")
center_frame.grid(row=0, column=1, padx=10, pady=5, sticky="n")
right_frame = tk.Frame(input_frame, bg="#D4C9BE")
right_frame.grid(row=0, column=2, padx=10, pady=5, sticky="n")

# --- Sección Izquierda: Datos Generales ---
tk.Label(left_frame, text="Datos Generales", bg="#D4C9BE", fg="#123458", font=("Roboto", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
tk.Label(left_frame, text="Año de nacimiento:", **label_style).grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_anio_nacimiento = ttk.Entry(left_frame)
entry_anio_nacimiento.grid(row=1, column=1, padx=5, pady=5, sticky="w")
entry_anio_nacimiento.insert(0, "1958")

tk.Label(left_frame, text="Edad actuarial:", **label_style).grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_edad_renta = ttk.Entry(left_frame)
entry_edad_renta.grid(row=2, column=1, padx=5, pady=5, sticky="w")
entry_edad_renta.insert(0, "48")

tk.Label(left_frame, text="Tabla de mortalidad:", **label_style).grid(row=3, column=0, padx=5, pady=5, sticky="e")
combo_tabla = ttk.Combobox(left_frame, values=[
    "PERM2000C", "PERF2000C", "PERM2000P", "PERF2000P",
    "PERM_2020_Indiv_2Orden", "PERM_2020_Indiv_1Orden",
    "PERF_2020_Indiv_2Orden", "PERF_2020_Indiv_1Orden",
    "PERM_2020_Colectivos_2Orden", "PERM_2020_Colectivos_1Orden",
    "PERF_2020_Colectivos_2Orden", "PERF_2020_Colectivos_1Orden",
    "PER_2020_Indiv_1Orden_UNISEX",
    "PER_2020_Colec_1Orden_UNISEX",
    "PER_2000P_UNISEX"
], state="readonly")
combo_tabla.grid(row=3, column=1, padx=5, pady=5, sticky="w")
combo_tabla.set("PERM2000C")
combo_tabla.bind("<<ComboboxSelected>>", actualizar_campos_tabla)

# Nuevos campos para proporciones (inicialmente ocultos)
label_prop_hombres = tk.Label(left_frame, text="Porcentaje de hombres (%):", **label_style)
label_prop_hombres.grid(row=4, column=0, padx=5, pady=5, sticky="e")
entry_prop_hombres = ttk.Entry(left_frame)
entry_prop_hombres.grid(row=4, column=1, padx=5, pady=5, sticky="w")
entry_prop_hombres.insert(0, "50")

label_prop_mujeres = tk.Label(left_frame, text="Porcentaje de mujeres (%):", **label_style)
label_prop_mujeres.grid(row=5, column=0, padx=5, pady=5, sticky="e")
entry_prop_mujeres = ttk.Entry(left_frame)
entry_prop_mujeres.grid(row=5, column=1, padx=5, pady=5, sticky="w")
entry_prop_mujeres.insert(0, "50")

# --- Sección Central: Datos de la Renta ---
tk.Label(center_frame, text="Datos de la Renta", bg="#D4C9BE", fg="#123458", font=("Roboto", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
tk.Label(center_frame, text="Tipo de renta:", **label_style).grid(row=1, column=0, padx=5, pady=5, sticky="e")
combo_tipo_renta = ttk.Combobox(center_frame, values=["Prepagable", "Pospagable"], state="readonly")
combo_tipo_renta.grid(row=1, column=1, padx=5, pady=5, sticky="w")
combo_tipo_renta.set("Prepagable")

tk.Label(center_frame, text="Cuantía inicial (€):", **label_style).grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_cuantia_inicial = ttk.Entry(center_frame)
entry_cuantia_inicial.grid(row=2, column=1, padx=5, pady=5, sticky="w")
entry_cuantia_inicial.insert(0, "15000")

tk.Label(center_frame, text="Temporalidad:", **label_style).grid(row=3, column=0, padx=5, pady=5, sticky="e")
combo_temporalidad = ttk.Combobox(center_frame, values=["Vitalicia", "Temporal"], state="readonly")
combo_temporalidad.grid(row=3, column=1, padx=5, pady=5, sticky="w")
combo_temporalidad.set("Vitalicia")
combo_temporalidad.bind("<<ComboboxSelected>>", actualizar_campos_temporalidad)

label_duracion = tk.Label(center_frame, text="Duración (años):", **label_style)
entry_duracion = ttk.Entry(center_frame)

tk.Label(center_frame, text="Diferimiento (años):", **label_style).grid(row=4, column=0, padx=5, pady=5, sticky="e")
entry_diferimiento = ttk.Entry(center_frame)
entry_diferimiento.grid(row=4, column=1, padx=5, pady=5, sticky="w")
entry_diferimiento.insert(0, "0")

tk.Label(center_frame, text="Periodicidad:", **label_style).grid(row=5, column=0, padx=5, pady=5, sticky="e")
combo_periodicidad = ttk.Combobox(center_frame, values=["Anual", "Fraccionada"], state="readonly")
combo_periodicidad.grid(row=5, column=1, padx=5, pady=5, sticky="w")
combo_periodicidad.set("Anual")
combo_periodicidad.bind("<<ComboboxSelected>>", actualizar_campos_periodicidad)

label_fracciones = tk.Label(center_frame, text="Fracciones por año:", **label_style)
entry_fracciones = ttk.Entry(center_frame)
entry_fracciones.insert(0, "12")

# --- Sección Derecha: Intereses e Incrementos ---
tk.Label(right_frame, text="Intereses e Incrementos", bg="#D4C9BE", fg="#123458", font=("Roboto", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

# Subframe para Intereses
interes_frame = tk.Frame(right_frame, bg="#D4C9BE")
interes_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

tk.Label(interes_frame, text="Intereses", bg="#D4C9BE", fg="#123458", font=("Roboto", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=2)
tk.Label(interes_frame, text="Tipo de interés:", **label_style).grid(row=1, column=0, padx=5, pady=5, sticky="e")
combo_tipo_interes = ttk.Combobox(interes_frame, values=["Fija", "Variable"], state="readonly")
combo_tipo_interes.grid(row=1, column=1, padx=5, pady=5, sticky="w")
combo_tipo_interes.set("Fija")
combo_tipo_interes.bind("<<ComboboxSelected>>", actualizar_campos_interes)

label_interes_fijo = tk.Label(interes_frame, text="Interés fijo (%, ej. 2):", **label_style)
label_interes_fijo.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_interes_fijo = ttk.Entry(interes_frame)
entry_interes_fijo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
entry_interes_fijo.insert(0, "2.75")

label_intereses = tk.Label(interes_frame, text="Tasas (%, ej. 2, 4):", **label_style)
entry_intereses = ttk.Entry(interes_frame)
entry_intereses.insert(0, "2, 4, 5")

label_saltos = tk.Label(interes_frame, text="Años de cambio (ej. 2, 5, 6):", **label_style)
entry_saltos = ttk.Entry(interes_frame)
entry_saltos.insert(0, "2, 5, 6")

# Subframe para Incrementos
incremento_frame = tk.Frame(right_frame, bg="#D4C9BE")
incremento_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="w")

tk.Label(incremento_frame, text="Incrementos", bg="#D4C9BE", fg="#123458", font=("Roboto", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=2)
tk.Label(incremento_frame, text="Tipo de incremento:", **label_style).grid(row=1, column=0, padx=5, pady=5, sticky="e")
combo_tipo_incremento = ttk.Combobox(incremento_frame, values=["Sin incremento", "Geométrico fijo", "Aritmético fijo", "Geométrico variable", "Aritmético variable"], state="readonly")
combo_tipo_incremento.grid(row=1, column=1, padx=5, pady=5, sticky="w")
combo_tipo_incremento.set("Aritmético fijo")
combo_tipo_incremento.bind("<<ComboboxSelected>>", actualizar_campos_incrementos)

label_factor_q = tk.Label(incremento_frame, text="Incremento geométrico (%):", **label_style)
entry_factor_q = ttk.Entry(incremento_frame)
entry_factor_q.insert(0, "2.5")

label_incremento_h = tk.Label(incremento_frame, text="Incremento aritmético (€):", **label_style)
entry_incremento_h = ttk.Entry(incremento_frame)
entry_incremento_h.insert(0, "500")

label_incrementos = tk.Label(incremento_frame, text="Incrementos (%, ej. 2.5, 2):", **label_style)
entry_incrementos = ttk.Entry(incremento_frame)
entry_incrementos.insert(0, "2.5, 2")

label_saltos_incrementos = tk.Label(incremento_frame, text="Años de cambio (ej. 8):", **label_style)
entry_saltos_incrementos = ttk.Entry(incremento_frame)
entry_saltos_incrementos.insert(0, "8")

# Inicializar visibilidad
actualizar_campos_interes()
actualizar_campos_temporalidad()
actualizar_campos_periodicidad()
actualizar_campos_incrementos()
actualizar_campos_tabla()

# Botón Calcular y Resultado
button_frame = tk.Frame(root, bg="#F1EFEC")
button_frame.pack(pady=10)

button_style = ttk.Style()
button_style.configure("TButton", font=("Roboto", 12, "bold"), background="#123458", foreground="#FFFFFF", borderwidth=1, relief="raised")
button_style.map("TButton", background=[("active", "#0F2A44")], foreground=[("active", "#FFFFFF")])

calcular_button = ttk.Button(button_frame, text="Calcular", command=calcular, style="TButton")
calcular_button.pack()

resultado_label = tk.Label(root, text="", bg="#F1EFEC", font=("Roboto", 12, "bold"), fg="#030303")
resultado_label.pack(pady=10)

# Tabla
table_frame = tk.Frame(root, bg="#D4C9BE")
table_frame.pack(pady=10, padx=20, fill="both", expand=True)

tree_style = ttk.Style()
tree_style.configure("Treeview", background="#FFFFFF", foreground="#030303", fieldbackground="#FFFFFF", font=("Roboto", 10))
tree_style.configure("Treeview.Heading", font=("Roboto", 11, "bold"), background="#123458", foreground="#FFFFFF", relief="flat")
tree_style.map("Treeview", background=[("selected", "#E0E0E0")])
tree_style.map("Treeview.Heading", background=[("active", "#0F2A44")], foreground=[("active", "#FFFFFF")])

columns = ('k', 'k p_x', 'C_k', 'v^k', 'k p_x * C_k * v^k')
tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="Treeview")
tree.heading('k', text='k')
tree.heading('k p_x', text='k p_x')
tree.heading('C_k', text='C_k')
tree.heading('v^k', text='v^k')
tree.heading('k p_x * C_k * v^k', text='k p_x * C_k * v^k')
tree.column('k', width=80, anchor='center')
tree.column('k p_x', width=120, anchor='center')
tree.column('C_k', width=120, anchor='center')
tree.column('v^k', width=120, anchor='center')
tree.column('k p_x * C_k * v^k', width=140, anchor='center')

# Scrollbar para la tabla
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# Usar grid para mejor control
tree.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

# Configurar grid para que table_frame se expanda
table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

# Iniciar la ventana
root.mainloop()