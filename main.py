import customtkinter as ctk
from tkinter import messagebox
from supabase import create_client, Client
import os
from PIL import Image

from admin_dashboard import AdminDashboard
from employee_dashboard import EmployeeDashboard

SUPABASE_URL = "https://ksymuaamkjzoehupdcdp.supabase.co"
SUPABASE_KEY = "sb_publishable_Mdq1uUvlrQikfraqcZ7vDw_dhGeeBW2"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PANE-SYS - Iniciar Sesión")
        self.geometry("420x520")
        self.resizable(False, False)
        
        self.update_idletasks()
        ancho = 420
        alto = 520
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width - ancho) // 2
        y = ((screen_height - 60) - alto) // 2
        
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.configure(fg_color="#FDFBF7")

        main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20, border_width=1, border_color="#E6DCC3")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        if os.path.exists("logo.png"):
            try:
                img = ctk.CTkImage(light_image=Image.open("logo.png"), size=(70, 70))
                lbl_img = ctk.CTkLabel(main_frame, image=img, text="")
                lbl_img.pack(pady=(25, 10))
            except Exception:
                pass

        ctk.CTkLabel(main_frame, text="🍞 PANE-SYS", font=("Arial", 22, "bold"), text_color="#5C3A21").pack(pady=(5, 5))
        ctk.CTkLabel(main_frame, text="Sistema de Control y Gestión", font=("Arial", 12), text_color="gray").pack(pady=(0, 25))

        self.entry_usuario = ctk.CTkEntry(main_frame, placeholder_text="Usuario", width=280, height=42, fg_color="#F9F6F0", border_color="#D7CCC8", font=("Arial", 13))
        self.entry_usuario.pack(pady=10)

        self.entry_password = ctk.CTkEntry(main_frame, placeholder_text="Contraseña", show="*", width=280, height=42, fg_color="#F9F6F0", border_color="#D7CCC8", font=("Arial", 13))
        self.entry_password.pack(pady=10)

        btn_login = ctk.CTkButton(main_frame, text="Iniciar Sesión", command=self.verificar_login, fg_color="#8D5524", hover_color="#6F431B", height=42, width=280, font=("Arial", 14, "bold"))
        btn_login.pack(pady=(25, 20))

    def verificar_login(self):
        user = self.entry_usuario.get().strip()
        pwd = self.entry_password.get().strip()

        if not user or not pwd:
            messagebox.showerror("Campos vacíos", "Por favor ingresa usuario y contraseña.")
            return

        try:
            response = supabase.table("usuario").select("*").eq("usuario", user).eq("password", pwd).execute()
            
            if response.data and len(response.data) > 0:
                usuario_encontrado = response.data[0]
                rol = usuario_encontrado.get("rol", "").strip().lower()
                nombre = usuario_encontrado.get("nombre", "Usuario")
                id_usuario = usuario_encontrado.get("idUsuario", 1)

                messagebox.themes = "green"
                messagebox.showinfo("Bienvenido", f"¡Acceso concedido!\nHola, {nombre}")
                
                self.destroy() 

                if rol == "admin":
                    app_admin = AdminDashboard(nombre_usuario=nombre)
                    app_admin.mainloop()
                elif rol == "empleado":
                    app_emp = EmployeeDashboard(nombre_usuario=nombre, id_usuario=id_usuario)
                    app_emp.mainloop()
                else:
                    messagebox.showerror("Error de Rol", f"El rol '{rol}' no está configurado en el sistema.")
            else:
                messagebox.showerror("Acceso Denegado", "Usuario o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar con Supabase:\n{e}")

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()