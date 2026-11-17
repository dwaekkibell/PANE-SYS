# 🥐 PANE-SYS
Sistema de Escritorio para la Gestión Integral y Punto de Venta (POS) en Panaderías.

---

## 📋 Descripción del Proyecto
**PANE-SYS** es una aplicación de escritorio desarrollada en Python con una interfaz moderna, diseñada específicamente para optimizar la administración y el control operativo de una pequeña panadería tradicional o local comercial fijo. El sistema centraliza el control de turnos de empleados, cobros en mostrador, inventario de insumos, control de mermas y métricas financieras en tiempo real conectándose de forma segura a una base de datos en la nube.

---

## ✨ Características Principales
* **🔐 Control de Acceso por Roles:** Módulos diferenciados y seguros para Administradores y Empleados.
* **💰 Punto de Venta (POS):** Carrito de compras dinámico, selección rápida de productos del catálogo y cálculo automático de totales y cambio.
* **🕒 Gestión de Turnos y Cortes de Caja:** Apertura y cierre de turnos por empleado con registro detallado de entradas, salidas y efectivo en caja.
* **📊 Tablero y Métricas en Tiempo Real:** Visualización gráfica del rendimiento de ventas de productos mediante integración con gráficos dinámicos y tarjetas de control gerencial.
* **📦 Control de Inventario e Insumos:** Monitoreo constante de stock de productos y registro de mermas.
* **📄 Generación de Reportes:** Creación automática de reportes detallados en formato PDF tanto de ventas como de cierres de turno.

---

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.14
* **Interfaz Gráfica (UI):** CustomTkinter (diseño moderno y estilizado sobre Tkinter)
* **Gráficas y Visualización:** Matplotlib
* **Base de Datos y Backend:** Supabase (PostgreSQL en la nube)
* **Generación de Reportes:** ReportLab
* **Empaquetado:** PyInstaller

---

## 📂 Estructura del Proyecto
```text
PANE-SYS/
│
├── images/                  # Recursos gráficos e iconos de la interfaz
├── Reportes/                # Almacenamiento local de reportes de ventas en PDF
├── Reportes de Turnos/      # Almacenamiento local de cortes de caja en PDF
├── main.py                  # Archivo principal de ejecución y controlador de vistas
├── admin_dashboard.py       # Panel de control gerencial y métricas
├── employee_dashboard.py    # Interfaz operativa para empleados y POS
├── logo.png                 # Logotipo institucional del sistema
├── .gitignore               # Archivos excluidos del control de versiones
└── README.md                # Documentación del proyecto
```

## 🚀 Instalación y Ejecución (Modo Desarrollo)
* Clona este repositorio:
git clone [https://github.com/dwaekkibell/PANE-SYS.git](https://github.com/dwaekkibell/PANE-SYS.git)
Instala las dependencias necesarias:

Bash
pip install customtkinter matplotlib reportlab supabase
Ejecuta el sistema:

Bash
python main.py
👥 Autor
Proyecto desarrollado con fines académicos para la gestión y optimización de procesos comerciales.



