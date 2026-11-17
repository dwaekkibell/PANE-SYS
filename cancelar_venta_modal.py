import customtkinter as ctk
from tkinter import messagebox

class VentanaAutorizacionAdmin(ctk.CTkToplevel):
    def __init__(self, parent, supabase, id_venta_a_cancelar, on_exito):
        super().__init__(parent)
        self.supabase = supabase
        self.id_venta = id_venta_a_cancelar
        self.on_exito = on_exito

        self.title("Autorización de Administrador - PANE-SYS")
        self.geometry("340x220")
        self.resizable(False, False)
        self.configure(fg_color="#FDFBF7")
        self.grab_set()

        # UI
        ctk.CTkLabel(self, text="🔒 Autorización Requerida", font=("Arial", 15, "bold"), text_color="#C0392B").pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Ingrese la contraseña del administrador\npara cancelar esta venta y retornar stock:", font=("Arial", 11), text_color="#3E2723", justify="center").pack(pady=5)

        self.entry_pass = ctk.CTkEntry(self, width=260, height=35, show="*", placeholder_text="Contraseña de Admin", fg_color="#FFFFFF", border_color="#D7CCC8")
        self.entry_pass.pack(padx=20, pady=10)
        self.entry_pass.focus()
        
        self.entry_pass.bind("<Return>", lambda event: self.verificar_y_cancelar())

        btn_autorizar = ctk.CTkButton(
            self, 
            text="✔ Autorizar Cancelación", 
            command=self.verificar_y_cancelar, 
            fg_color="#C0392B", 
            hover_color="#962D22", 
            height=35, 
            font=("Arial", 12, "bold")
        )
        btn_autorizar.pack(pady=(5, 15))

    def verificar_y_cancelar(self):
        password_ingresada = self.entry_pass.get().strip()
        if not password_ingresada:
            messagebox.showwarning("Campo Vacío", "Por favor ingrese la contraseña.", parent=self)
            return

        try:
            res = self.supabase.table("usuario").select("*").eq("rol", "admin").execute()
            
            admin_valido = False
            if res.data:
                for admin in res.data:
                    pass_en_db = str(admin.get("password", "")).strip()
                    if pass_en_db == password_ingresada:
                        admin_valido = True
                        break

            if admin_valido:
                self.ejecutar_reversion_venta()
            else:
                messagebox.showerror("Acceso Denegado", "Contraseña de administrador incorrecta.", parent=self)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo verificar la credencial:\n{e}", parent=self)

    def ejecutar_reversion_venta(self):
        try:
            res_det = self.supabase.table("detalleventa").select("*").eq("idVenta", self.id_venta).execute()
            
            if res_det.data:
                for det in res_det.data:
                    id_prod = det.get("idProducto")
                    cantidad_vendida = int(det.get("cantidad", 0))

                    res_venta_info = self.supabase.table("venta").select("idturno").eq("idVenta", self.id_venta).execute()
                    if res_venta_info.data:
                        id_turno_venta = res_venta_info.data[0].get("idturno")

                        res_turno_det = self.supabase.table("detalle_turno").select("iddetalle, cantidad").eq("idturno", id_turno_venta).eq("idproducto", id_prod).execute()
                        
                        if res_turno_det.data:
                            row_t = res_turno_det.data[0]
                            id_detalle_turno = row_t.get("iddetalle")
                            stock_actual = int(row_t.get("cantidad", 0))
                            
                            nuevo_stock = stock_actual + cantidad_vendida

                            self.supabase.table("detalle_turno").update({"cantidad": nuevo_stock}).eq("iddetalle", id_detalle_turno).execute()

            self.supabase.table("detalleventa").delete().eq("idVenta", self.id_venta).execute()
            self.supabase.table("venta").delete().eq("idVenta", self.id_venta).execute()

            messagebox.showinfo("Venta Cancelada", "La venta fue cancelada con éxito y los productos se han devuelto al stock del turno.", parent=self)
            self.destroy()
            
            if self.on_exito:
                self.on_exito()

        except Exception as e:
            messagebox.showerror("Error de Reversión", "No se pudo completar la cancelación de la venta:\n" + str(e), parent=self)