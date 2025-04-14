# frontend.py
import tkinter as tk
from tkinter import ttk
import pandas as pd
from backend import funcion_intereses, tabla_gen, renta

# Función para limpiar la tabla anterior
def limpiar_tabla(tree):
    for item in tree.get_children():
        tree.delete(item)

# Función para mostrar la tabla
def mostrar_tabla(tabla_flujos, tree):
    limpiar_tabla(tree)
    
    # Mostrar todas las filas de la tabla
    for index, row in tabla_flujos.iterrows():
        tree.insert("", tk.END, values=(
            f"{row['k']:.2f}",  # Mostrar k con 2 decimales (años fraccionarios)
            f"{row['v^k']:.6f}",
            f"{row['k p_x']:.6f}",
            f"{row['v^k * k p_x']:.6f}",
            f"{row['C * k p_x']:.6f}"
        ))

# Funciones para mostrar/ocultar campos de tasas de interés
def actualizar_campos_interes(*args):
    seleccion = combo_tipo_interes.get()
    if seleccion == "Fija":
        label_interes_fijo.grid()
        entry_interes_fijo.grid()
        label_intereses.grid_remove()
        entry_intereses.grid_remove()
        label_saltos.grid_remove()
        entry_saltos.grid_remove()
    elif seleccion == "Variable":
        label_interes_fijo.grid_remove()
        entry_interes_fijo.grid_remove()
        label_intereses.grid()
        entry_intereses.grid()
        label_saltos.grid()
        entry_saltos.grid()

# Funciones para mostrar/ocultar campos de fracciones
def actualizar_campos_fracciones(*args):
    seleccion = combo_periodicidad.get()
    if seleccion == "Anual":
        label_fracciones.grid_remove()
        entry_fracciones.grid_remove()
    elif seleccion == "Fraccionada":
        label_fracciones.grid()
        entry_fracciones.grid()

# Función principal de cálculo
def calcular():
    try:
        # Obtener los valores de los campos
        g = int(entry_anio_nacimiento.get())
        nombre_tabla = combo_tabla.get()
        if not nombre_tabla:
            raise ValueError("Debe seleccionar una tabla de mortalidad.")
        
        # Edad al momento de contratación (necesaria para funcion_intereses si se usa)
        edad_renta = int(entry_edad_renta.get())

        # Temporalidad (necesaria para funcion_intereses si se usa)
        temporalidad = combo_temporalidad.get()
        if temporalidad == "Vitalicia":
            temporalidad = None
        elif temporalidad == "Temporal":
            temporalidad = int(entry_duracion.get())
        else:
            raise ValueError("Debe seleccionar si la renta es vitalicia o temporal.")
        
        # Generar la tabla generacional (necesaria para funcion_intereses si se usa)
        tabla_generacion = tabla_gen(g, nombre_tabla)

        # Determinar si la tasa es fija o variable
        # Intereses
        # Intereses
        # Intereses
        interes = None
        lista_intereses = None
        if combo_tipo_interes.get() == "Fija":
            interes_str = entry_interes_fijo.get().strip()
            if not interes_str:
                raise ValueError("El interés fijo no puede estar vacío.")
            interes = float(interes_str) / 100
        else:
            intereses_str = entry_intereses.get().strip()
            saltos_str = entry_saltos.get().strip()
            if not intereses_str or not saltos_str:
                raise ValueError("Las tasas y los saltos no pueden estar vacíos para intereses variables.")
            try:
                intereses = [float(i.strip()) / 100 for i in intereses_str.split(",") if i.strip()]
                saltos = [int(s.strip()) for s in saltos_str.split(",") if s.strip()]
                if not intereses or not saltos:
                    raise ValueError("Debe proporcionar al menos una tasa y un salto.")
                # Pasar temporalidad, edad_renta y tabla_generacion
                lista_intereses = funcion_intereses(intereses, saltos, edad_renta, tabla_generacion, temporalidad)
            except ValueError as e:
                raise ValueError(f"Error en tasas o saltos: {str(e)}")

        # Tipo de renta
        tipo_renta = combo_tipo_renta.get()
        if not tipo_renta:
            raise ValueError("Debe seleccionar un tipo de renta (prepagable/pospagable).")
        
        capital = float(entry_capital.get())
        
        # Diferimiento
        diferimiento = entry_diferimiento.get()
        if diferimiento == "":
            diferimiento = None
        else:
            diferimiento = int(diferimiento)

        # Periodicidad (Anual o Fraccionada)
        periodicidad = combo_periodicidad.get()
        if periodicidad == "Anual":
            fracciones_por_anio = 1
        elif periodicidad == "Fraccionada":
            fracciones_str = entry_fracciones.get()
            if not fracciones_str:
                raise ValueError("Debe ingresar el número de fracciones por año.")
            try:
                fracciones_por_anio = int(fracciones_str.strip())
                if fracciones_por_anio <= 0:
                    raise ValueError("El número de fracciones por año debe ser mayor que 0.")
            except ValueError:
                raise ValueError("El número de fracciones por año debe ser un número entero válido (ej. 12 para mensual).")
        else:
            raise ValueError("Debe seleccionar la periodicidad de la renta (Anual o Fraccionada).")

        # Tipo de ajuste
        ajuste_seleccionado = combo_ajuste.get()
        if ajuste_seleccionado == "Sin ajuste":
            tipo_ajuste = None
            factor_q = None
            incremento_h = None
        elif ajuste_seleccionado == "Geométrico":
            tipo_ajuste = "geometrica"
            factor_q = float(entry_factor_q.get())
            incremento_h = None
        elif ajuste_seleccionado == "Aritmético":
            tipo_ajuste = "aritmetica"
            factor_q = None
            incremento_h = float(entry_incremento_h.get())
        else:
            raise ValueError("Tipo de ajuste no válido seleccionado.")

        # Calcular la renta
        resultado = renta(tipo_renta, edad_renta, capital, temporalidad, diferimiento, lista_intereses=lista_intereses, interes=interes, tabla_generacion=tabla_generacion, tipo_ajuste=tipo_ajuste, factor_q=factor_q, incremento_h=incremento_h, fracciones_por_anio=fracciones_por_anio)
        print("Resultado de renta:", resultado)  # Depuración
        if len(resultado) != 3:
            raise ValueError(f"La función renta devolvió {len(resultado)} valores, pero se esperaban 3 (sumatorio, valor_renta, tabla_flujos).")
        sumatorio, valor_renta, tabla_flujos = resultado
        resultado_label.config(text=f"Valor actual actuarial unitario: {sumatorio:.6f}\nValor actual actuarial: {valor_renta:.2f}")

        # Mostrar la tabla
        mostrar_tabla(tabla_flujos, tree)

    except Exception as e:
        resultado_label.config(text=f"Error: {str(e)}", fg="red")

# Crear la ventana principal
root = tk.Tk()
root.title("Jupama Actuarial Software")
root.geometry("1000x800")
root.configure(bg="#f0f4f8")

# Estilo para los widgets
style = ttk.Style()
style.configure("TLabel", background="#f0f4f8", font=("Helvetica", 11))
style.configure("TEntry", font=("Helvetica", 11))
style.configure("TCombobox", font=("Helvetica", 11))
style.configure("TButton", font=("Helvetica", 12, "bold"))

# Encabezado
header_frame = tk.Frame(root, bg="#2c3e50", pady=20)
header_frame.pack(fill="x")

# Título del programa
header_label = tk.Label(
    header_frame,
    text="Jupama Actuarial Software",
    font=("Helvetica", 20, "bold"),
    fg="white",
    bg="#2c3e50"
)
header_label.pack()

# Subtítulo
subtitle_label = tk.Label(
    header_frame,
    text="Cálculo de Rentas Actuariales",
    font=("Helvetica", 12, "italic"),
    fg="#dcdcdc",
    bg="#2c3e50"
)
subtitle_label.pack()

# Frame principal para las entradas y la tabla
main_frame = tk.Frame(root, bg="#f0f4f8", padx=20, pady=20)
main_frame.pack(fill="both", expand=True)

# Frame para las entradas (izquierda)
input_frame = tk.LabelFrame(
    main_frame,
    text="Datos de Entrada",
    font=("Helvetica", 14, "bold"),
    bg="#f0f4f8",
    fg="#2c3e50",
    padx=15,
    pady=15
)
input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

# Año de nacimiento
tk.Label(input_frame, text="Año de nacimiento:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_anio_nacimiento = ttk.Entry(input_frame)
entry_anio_nacimiento.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Tabla de mortalidad
tk.Label(input_frame, text="Tabla de mortalidad:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
combo_tabla = ttk.Combobox(
    input_frame,
    values=['PERM2000C', 'PERF2000C', 'PERM2000P', 'PERF2000P',
            'PERM_2020_Indiv_2Orden', 'PERM_2020_Indiv_1Orden',
            'PERF_2020_Indiv_2Orden', 'PERF_2020_Indiv_1Orden',
            'PERM_2020_Colectivos_2Orden', 'PERM_2020_Colectivos_1Orden',
            'PERF_2020_Colectivos_2Orden', 'PERF_2020_Colectivos_1Orden'],
    state="readonly"
)
combo_tabla.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Tipo de tasa de interés (Fija o Variable)
tk.Label(input_frame, text="Tipo de tasa de interés:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
combo_tipo_interes = ttk.Combobox(input_frame, values=["Fija", "Variable"], state="readonly")
combo_tipo_interes.grid(row=2, column=1, padx=5, pady=5, sticky="w")
combo_tipo_interes.set("Fija")  # Valor por defecto
combo_tipo_interes.bind("<<ComboboxSelected>>", actualizar_campos_interes)

# Tasa de interés fija
label_interes_fijo = tk.Label(input_frame, text="Tasa de interés fija (%, ej. 3):", bg="#f0f4f8", font=("Helvetica", 11))
label_interes_fijo.grid(row=3, column=0, padx=5, pady=5, sticky="e")
entry_interes_fijo = ttk.Entry(input_frame)
entry_interes_fijo.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Tasas de interés variables (separadas por comas, ej. 2, 4, 5)
label_intereses = tk.Label(input_frame, text="Tasas de interés (%, ej. 2, 4, 5):", bg="#f0f4f8", font=("Helvetica", 11))
label_intereses.grid(row=4, column=0, padx=5, pady=5, sticky="e")
entry_intereses = ttk.Entry(input_frame)
entry_intereses.grid(row=4, column=1, padx=5, pady=5, sticky="w")

# Años de cambio (saltos, separados por comas, ej. 2, 5, 6)
label_saltos = tk.Label(input_frame, text="Años de cambio (ej. 2, 5, 6):", bg="#f0f4f8", font=("Helvetica", 11))
label_saltos.grid(row=5, column=0, padx=5, pady=5, sticky="e")
entry_saltos = ttk.Entry(input_frame)
entry_saltos.grid(row=5, column=1, padx=5, pady=5, sticky="w")

# Tipo de renta
tk.Label(input_frame, text="Tipo de renta:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=6, column=0, padx=5, pady=5, sticky="e")
combo_tipo_renta = ttk.Combobox(input_frame, values=["prepagable", "pospagable"], state="readonly")
combo_tipo_renta.grid(row=6, column=1, padx=5, pady=5, sticky="w")

# Edad al momento de contratación
tk.Label(input_frame, text="Edad al momento de contratación:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=7, column=0, padx=5, pady=5, sticky="e")
entry_edad_renta = ttk.Entry(input_frame)
entry_edad_renta.grid(row=7, column=1, padx=5, pady=5, sticky="w")

# Capital a asegurar
tk.Label(input_frame, text="Capital a asegurar:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=8, column=0, padx=5, pady=5, sticky="e")
entry_capital = ttk.Entry(input_frame)
entry_capital.grid(row=8, column=1, padx=5, pady=5, sticky="w")

# Temporalidad (vitalicia o temporal)
tk.Label(input_frame, text="Temporalidad:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=9, column=0, padx=5, pady=5, sticky="e")
combo_temporalidad = ttk.Combobox(input_frame, values=["Vitalicia", "Temporal"], state="readonly")
combo_temporalidad.grid(row=9, column=1, padx=5, pady=5, sticky="w")

# Duración (si es temporal)
tk.Label(input_frame, text="Duración (si temporal):", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=10, column=0, padx=5, pady=5, sticky="e")
entry_duracion = ttk.Entry(input_frame)
entry_duracion.grid(row=10, column=1, padx=5, pady=5, sticky="w")

# Diferimiento
tk.Label(input_frame, text="Diferimiento en años (dejar vacío si no hay):", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=11, column=0, padx=5, pady=5, sticky="e")
entry_diferimiento = ttk.Entry(input_frame)
entry_diferimiento.grid(row=11, column=1, padx=5, pady=5, sticky="w")

# Periodicidad (Anual o Fraccionada)
tk.Label(input_frame, text="Periodicidad de la renta:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=12, column=0, padx=5, pady=5, sticky="e")
combo_periodicidad = ttk.Combobox(input_frame, values=["Anual", "Fraccionada"], state="readonly")
combo_periodicidad.grid(row=12, column=1, padx=5, pady=5, sticky="w")
combo_periodicidad.set("Anual")  # Valor por defecto
combo_periodicidad.bind("<<ComboboxSelected>>", actualizar_campos_fracciones)

# Número de fracciones por año (si es fraccionada)
label_fracciones = tk.Label(input_frame, text="Fracciones por año (ej. 12 para mensual):", bg="#f0f4f8", font=("Helvetica", 11))
label_fracciones.grid(row=13, column=0, padx=5, pady=5, sticky="e")
entry_fracciones = ttk.Entry(input_frame)
entry_fracciones.grid(row=13, column=1, padx=5, pady=5, sticky="w")

# Tipo de ajuste
tk.Label(input_frame, text="Tipo de ajuste:", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=14, column=0, padx=5, pady=5, sticky="e")
combo_ajuste = ttk.Combobox(input_frame, values=["Sin ajuste", "Geométrico", "Aritmético"], state="readonly")
combo_ajuste.grid(row=14, column=1, padx=5, pady=5, sticky="w")

# Factor q (para ajuste geométrico)
tk.Label(input_frame, text="Factor q (geométrico, ej. 1.03):", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=15, column=0, padx=5, pady=5, sticky="e")
entry_factor_q = ttk.Entry(input_frame)
entry_factor_q.grid(row=15, column=1, padx=5, pady=5, sticky="w")

# Incremento h (para ajuste aritmético)
tk.Label(input_frame, text="Incremento h (aritmético, ej. 100):", bg="#f0f4f8", font=("Helvetica", 11)).grid(row=16, column=0, padx=5, pady=5, sticky="e")
entry_incremento_h = ttk.Entry(input_frame)
entry_incremento_h.grid(row=16, column=1, padx=5, pady=5, sticky="w")

# Inicializar visibilidad de los campos
actualizar_campos_interes()
actualizar_campos_fracciones()

# Frame para la tabla (derecha)
table_frame = tk.LabelFrame(
    main_frame,
    text="Flujos Probables de Pago",
    font=("Helvetica", 14, "bold"),
    bg="#f0f4f8",
    fg="#2c3e50",
    padx=15,
    pady=15
)
table_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

# Configurar el Treeview para la tabla
columns = ('k', 'v^k', 'k p_x', 'v^k * k p_x', 'FP')
tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
tree.heading('k', text='k')
tree.heading('v^k', text='v^k')
tree.heading('k p_x', text='k p_x')
tree.heading('v^k * k p_x', text='v^k * k p_x')
tree.heading('FP', text='C * k p_x (FP)')
tree.column('k', width=50, anchor='center')
tree.column('v^k', width=100, anchor='center')
tree.column('k p_x', width=100, anchor='center')
tree.column('v^k * k p_x', width=100, anchor='center')
tree.column('FP', width=100, anchor='center')

# Añadir barra de desplazamiento
scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(fill=tk.BOTH, expand=True)

# Frame para el botón de cálculo
button_frame = tk.Frame(main_frame, bg="#f0f4f8")
button_frame.grid(row=1, column=0, columnspan=2, pady=10)

# Botón para calcular
calcular_button = ttk.Button(button_frame, text="Calcular", command=calcular, style="Accent.TButton")
style.configure("Accent.TButton", background="#3498db", foreground="white", font=("Helvetica", 12, "bold"))
calcular_button.pack()

# Frame para los resultados
result_frame = tk.LabelFrame(
    main_frame,
    text="Resultados",
    font=("Helvetica", 14, "bold"),
    bg="#f0f4f8",
    fg="#2c3e50",
    padx=15,
    pady=15
)
result_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")

# Etiqueta para mostrar el resultado
resultado_label = tk.Label(
    result_frame,
    text="",
    font=("Helvetica", 12),
    bg="#f0f4f8",
    fg="#2c3e50",
    justify="left"
)
resultado_label.pack()

# Footer
footer_frame = tk.Frame(root, bg="#2c3e50", pady=10)
footer_frame.pack(fill="x", side="bottom")

footer_label = tk.Label(
    footer_frame,
    text="© 2025 Jupama Actuarial Software. Todos los derechos reservados.",
    font=("Helvetica", 10),
    fg="#dcdcdc",
    bg="#2c3e50"
)
footer_label.pack()

# Configurar el grid para que se expanda correctamente
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_rowconfigure(0, weight=1)

# Iniciar la aplicación
root.mainloop()