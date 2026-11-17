import threading
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

class TurnosModuloFrame(ctk.CTkFrame):
    def __init__(self, parent, supabase_client):
        super().__init__(parent, fg_color="transparent")
        self.supabase = supabase_client
        self.entradas_stock_turno = {}
        self.empleados_dict = {}

        # --- TÍTULO DE LA SECCIÓN ---
        ctk.CTkLabel(
            self, 
            text="Asignación de Turno y Stock Diario", 
            font=("Arial", 22, "bold"), 
            text_color="#3E2723"
        ).pack(anchor="w", padx=30, pady=(20, 5))
        
        ctk.CTkLabel(
            self, 
            text="Asigna el fondo de caja y la cantidad de pan que se lleva el empleado a ruta.", 
            font=("Arial", 13), 
            text_color="gray"
        ).pack(anchor="w", padx=30, pady=(0, 15))

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=5)

        # --- COLUMNA IZQUIERDA: Configuración del Turno ---
        left_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3", width=340)
        left_frame.pack(side="left", fill="y", padx=(0, 15), pady=5)
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="Configuración del Turno", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(20, 15))

        ctk.CTkLabel(left_frame, text="Seleccionar Empleado:", font=("Arial", 11, "bold"), text_color="#3E2723").pack(anchor="w", padx=20, pady=(5, 2))
        self.combo_empleado = ctk.CTkComboBox(left_frame, values=["Cargando..."], width=300, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.combo_empleado.pack(padx=20, pady=(0, 15))

        ctk.CTkLabel(left_frame, text="Fondo de Caja Inicial ($):", font=("Arial", 11, "bold"), text_color="#3E2723").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_fondo_caja = ctk.CTkEntry(left_frame, placeholder_text="ej. 500.00", width=300, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_fondo_caja.pack(padx=20, pady=(0, 15))

        ctk.CTkLabel(left_frame, text="Descripción / Horario del Turno:", font=("Arial", 11, "bold"), text_color="#3E2723").pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_desc_turno = ctk.CTkEntry(left_frame, placeholder_text="ej. Turno Matutino - Ruta Centro", width=300, height=36, fg_color="#F9F6F0", border_color="#D7CCC8")
        self.entry_desc_turno.pack(padx=20, pady=(0, 25))

        btn_guardar_turno = ctk.CTkButton(
            left_frame, 
            text="🚀 Asignar Turno y Stock", 
            command=self.guardar_asignacion_turno, 
            fg_color="#27AE60", 
            hover_color="#1E8449", 
            height=42, 
            font=("Arial", 13, "bold")
        )
        btn_guardar_turno.pack(padx=20, pady=10, fill="x")

        # --- COLUMNA DERECHA: Asignación de Panes ---
        right_frame = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E6DCC3")
        right_frame.pack(side="right", fill="both", expand=True, padx=(0, 0), pady=5)

        ctk.CTkLabel(right_frame, text="Stock de Pan a Entregar (Producción del Día)", font=("Arial", 14, "bold"), text_color="#5C3A21").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(right_frame, text="Indica cuántas piezas de cada pan se le cargan al empleado en su canasta.", font=("Arial", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))

        self.scroll_productos_turno = ctk.CTkScrollableFrame(right_frame, fg_color="#F9F6F0", corner_radius=10)
        self.scroll_productos_turno.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        threading.Thread(target=self.cargar_datos_turno_async, daemon=True).start()

    def cargar_datos_turno_async(self):
        empleados_lista = []
        self.empleados_dict = {}
        productos_lista = []

        try:
            res_usu = self.supabase.table("usuario").select("idUsuario, nombre").execute()
            if res_usu.data:
                for u in res_usu.data:
                    nom = u.get("nombre", "Sin nombre")
                    uid = u.get("idUsuario")
                    empleados_lista.append(nom)
                    self.empleados_dict[nom] = uid

            res_prod = self.supabase.table("producto").select("idProducto, nombre, precio_vent").execute()
            if res_prod.data:
                productos_lista = res_prod.data
        except Exception as e:
            print(f"Error cargando datos para turno: {e}")

        def actualizar_ui():
            if empleados_lista:
                self.combo_empleado.configure(values=empleados_lista)
                self.combo_empleado.set(empleados_lista[0])
            else:
                self.combo_empleado.configure(values=["Sin empleados"])
                self.combo_empleado.set("Sin empleados")

            for widget in self.scroll_productos_turno.winfo_children():
                widget.destroy()

            self.entradas_stock_turno.clear()

            if productos_lista:
                for prod in productos_lista:
                    pid = prod.get("idProducto")
                    nombre = prod.get("nombre")
                    precio = prod.get("precio_vent", 0)

                    fila = ctk.CTkFrame(self.scroll_productos_turno, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E6DCC3")
                    fila.pack(fill="x", padx=10, pady=6)

                    lbl_info = ctk.CTkLabel(fila, text=f"🍞 {nombre}  (Base: ${precio:,.2f})", font=("Arial", 12, "bold"), text_color="#3E2723")
                    lbl_info.pack(side="left", padx=15, pady=10)

                    entry_cant = ctk.CTkEntry(fila, placeholder_text="0", width=80, height=32, justify="center", fg_color="#FDFBF7", border_color="#D7CCC8")
                    entry_cant.pack(side="right", padx=15, pady=10)
                    entry_cant.insert(0, "0")

                    self.entradas_stock_turno[pid] = entry_cant
            else:
                ctk.CTkLabel(self.scroll_productos_turno, text="No hay productos registrados en el catálogo.", font=("Arial", 12), text_color="gray").pack(pady=20)

        self.after(0, actualizar_ui)

    def guardar_asignacion_turno(self):
        empleado_nom = self.combo_empleado.get()
        fondo_str = self.entry_fondo_caja.get().strip()
        desc_turno = self.entry_desc_turno.get().strip()

        if not fondo_str or empleado_nom == "Sin empleados":
            messagebox.showwarning("Campos incompletos", "Por favor selecciona un empleado e indica el fondo de caja inicial.")
            return

        try:
            fondo_caja = float(fondo_str)
            id_usuario = self.empleados_dict.get(empleado_nom)

            stock_asignado = {}
            for pid, entry in self.entradas_stock_turno.items():
                val_txt = entry.get().strip()
                cant = int(val_txt) if val_txt.isdigit() else 0
                if cant > 0:
                    stock_asignado[pid] = cant

            if not stock_asignado:
                messagebox.showwarning("Sin stock", "Debes asignarle al menos un producto con cantidad mayor a 0 para este turno.")
                return

            res_turno = self.supabase.table("turno").insert({
                "idusuario": id_usuario,
                "fondo_caja": fondo_caja,
                "nombre_turno": desc_turno if desc_turno else "Turno Activo",
                "hora_inicio": datetime.now().isoformat()
            }).execute()

            if res_turno.data:
                turno_creado = res_turno.data[0]
                id_turno = turno_creado.get("idturno") or turno_creado.get("idTurno")

                for pid, cant in stock_asignado.items():
                    self.supabase.table("detalle_turno").insert({
                        "idturno": id_turno,
                        "idproducto": pid,
                        "cantidad": cant
                    }).execute()

            messagebox.showinfo("¡Éxito!", f"Turno y stock asignados correctamente a {empleado_nom}.\nEl empleado ya puede iniciar sesión y verificar su canasta.")
            
            self.entry_fondo_caja.delete(0, "end")
            self.entry_desc_turno.delete(0, "end")
            for entry in self.entradas_stock_turno.values():
                entry.delete(0, "end")
                entry.insert(0, "0")

        except ValueError:
            messagebox.showerror("Error", "El fondo de caja y las cantidades deben ser números válidos.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el turno:\n{e}")