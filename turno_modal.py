import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class VentanaTurnoModal(ctk.CTkToplevel):
    def __init__(self, parent, supabase_client, id_usuario, callback_exito):
        super().__init__(parent)
        self.title("PANE-SYS - Verificación de Turno y Stock")
        self.geometry("450x560")
        self.resizable(False, False)
        self.configure(fg_color="#FDFBF7")
        
        # Ventana modal
        self.transient(parent)
        self.grab_set()

        self.supabase = supabase_client
        self.id_usuario = id_usuario
        self.callback_exito = callback_exito

        ctk.CTkLabel(self, text="📦 Verificación de Turno Asignado", font=("Arial", 18, "bold"), text_color="#3E2723").pack(pady=(20, 5))
        ctk.CTkLabel(self, text="El administrador te ha asignado el siguiente turno y stock:", font=("Arial", 12), text_color="gray").pack(pady=(0, 10))

        self.frame_info = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E6DCC3")
        self.frame_info.pack(fill="x", padx=20, pady=10)

        self.lbl_turno = ctk.CTkLabel(self.frame_info, text="Turno: Cargando...", font=("Arial", 13, "bold"), text_color="#5C3A21")
        self.lbl_turno.pack(anchor="w", padx=15, pady=(10, 2))

        self.lbl_fondo = ctk.CTkLabel(self.frame_info, text="Fondo de Caja: $0.00", font=("Arial", 13), text_color="#3E2723")
        self.lbl_fondo.pack(anchor="w", padx=15, pady=(2, 10))

        ctk.CTkLabel(self, text="Stock de Pan Asignado a Ruta:", font=("Arial", 13, "bold"), text_color="#3E2723").pack(anchor="w", padx=20, pady=(10, 5))

        self.scroll_stock = ctk.CTkScrollableFrame(self, fg_color="#FFFFFF", corner_radius=10, height=140, border_width=1, border_color="#E6DCC3")
        self.scroll_stock.pack(fill="x", padx=20, pady=5)

        self.btn_aceptar = ctk.CTkButton(
            self, 
            text="✅ Confirmar y Entrar al POS", 
            command=self.verificar_y_entrar, 
            fg_color="#27AE60", 
            hover_color="#1E8449", 
            height=40, 
            font=("Arial", 13, "bold")
        )
        self.btn_aceptar.pack(pady=(15, 15))
        self.btn_aceptar.configure(state="disabled")

        self.cargar_datos_turno()

    def cargar_datos_turno(self):
        try:
            res_turno = self.supabase.table("turno").select("*").eq("idusuario", self.id_usuario).is_("hora_fin", "null").execute()

            if not res_turno.data or len(res_turno.data) == 0:
                messagebox.showwarning("Sin Turno", "No tienes ningún turno asignado por el administrador.")
                self.destroy()
                return

            self.turno_asignado = res_turno.data[0]
            id_turno = self.turno_asignado.get("idturno") or self.turno_asignado.get("idTurno")
            nombre_t = self.turno_asignado.get("nombre_turno", "Turno Activo")
            fondo = self.turno_asignado.get("fondo_caja", 0.0)

            self.lbl_turno.configure(text=f"Turno: {nombre_t}")
            self.lbl_fondo.configure(text=f"Fondo de Caja Inicial: ${float(fondo):.2f}")

            res_prod = self.supabase.table("producto").select("*").execute()
            nombres_prod = {}
            if res_prod.data:
                for p in res_prod.data:
                    pid_val = p.get("idProducto") or p.get("idproducto") or p.get("id")
                    p_nombre = p.get("nombre") or p.get("nombre_producto") or "Producto"
                    if pid_val is not None:
                        nombres_prod[pid_val] = p_nombre

            res_detalle = self.supabase.table("detalle_turno").select("idproducto, cantidad").eq("idturno", id_turno).execute()

            for widget in self.scroll_stock.winfo_children():
                widget.destroy()

            if res_detalle.data and len(res_detalle.data) > 0:
                for det in res_detalle.data:
                    pid = det.get("idproducto")
                    cant = det.get("cantidad", 0)
                    nombre_pan = nombres_prod.get(pid, f"Producto ID {pid}")

                    fila = ctk.CTkFrame(self.scroll_stock, fg_color="transparent")
                    fila.pack(fill="x", pady=3)

                    ctk.CTkLabel(fila, text=f"• {nombre_pan}", font=("Arial", 12), text_color="#3E2723").pack(side="left", padx=5)
                    ctk.CTkLabel(fila, text=f"{cant} pzs", font=("Arial", 12, "bold"), text_color="#8D5524").pack(side="right", padx=5)
                
                self.btn_aceptar.configure(state="normal")
            else:
                ctk.CTkLabel(self.scroll_stock, text="No hay piezas registradas en este turno.", font=("Arial", 11), text_color="gray").pack(pady=20)
                self.btn_aceptar.configure(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la información del turno:\n{e}")

    def verificar_y_entrar(self):
        try:
            id_turno = self.turno_asignado.get("idturno") or self.turno_asignado.get("idTurno")
            nombre_t = self.turno_asignado.get("nombre_turno", "Turno Activo")
            
            self.callback_exito(id_turno, nombre_t)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo acceder al POS:\n{e}")