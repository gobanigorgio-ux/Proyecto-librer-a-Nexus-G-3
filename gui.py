"""
Interfaz grafica para Nexus Library.

Incluye login, dashboard, gestion de libros/usuarios/prestamos, lista de espera,
visualizacion del BST, recorrido de lista enlazada y analisis de complejidad.
"""

import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
except ImportError:
    Image = None
    ImageTk = None
    ImageDraw = None
    ImageFilter = None

from biblioteca import Biblioteca
from tads import EstadoLibro, EstadoUsuario


BG = "#eef2f7"
CARD = "#ffffff"
DARK = "#0f172a"
DARK_2 = "#1e293b"
BLUE = "#2563eb"
CYAN = "#0891b2"
GREEN = "#16a34a"
RED = "#dc2626"
ORANGE = "#f59e0b"
PURPLE = "#7c3aed"
PINK = "#db2777"
TEXT = "#111827"
MUTED = "#64748b"
BORDER = "#dbe3ef"

THEMES = {
    "light": {
        "bg": "#eef4ff",
        "card": "#ffffff",
        "surface": "#f8fbff",
        "sidebar": "#101827",
        "sidebar_2": "#1d2b44",
        "text": "#101827",
        "muted": "#64748b",
        "border": "#d8e4f4",
        "hero": "#172554",
        "hero_2": "#0e7490",
        "canvas": "#f8fafc",
    },
    "dark": {
        "bg": "#0b1120",
        "card": "#111827",
        "surface": "#162033",
        "sidebar": "#030712",
        "sidebar_2": "#182033",
        "text": "#f8fafc",
        "muted": "#a8b3c7",
        "border": "#26354d",
        "hero": "#08111f",
        "hero_2": "#164e63",
        "canvas": "#101827",
    },
}


def asset_path(nombre):
    return os.path.join(os.path.dirname(__file__), "imagenes", nombre)


def limpiar(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def ajustar_color(color, factor=1.12):
    if not color.startswith("#") or len(color) != 7:
        return color
    partes = []
    for i in (1, 3, 5):
        valor = int(color[i:i + 2], 16)
        if factor >= 1:
            valor = int(valor + (255 - valor) * (factor - 1))
        else:
            valor = int(valor * factor)
        partes.append(max(0, min(255, valor)))
    return "#%02x%02x%02x" % tuple(partes)


def boton(parent, text, command, color=BLUE, fill=False):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg="white",
        activebackground=ajustar_color(color, 0.88),
        activeforeground="white",
        bd=0,
        relief=tk.FLAT,
        cursor="hand2",
        font=("Segoe UI", 10, "bold"),
        padx=14,
        pady=8,
    )
    btn.bind("<Enter>", lambda _e: btn.config(bg=ajustar_color(color, 1.12)))
    btn.bind("<Leave>", lambda _e: btn.config(bg=color))
    btn.bind("<ButtonPress-1>", lambda _e: btn.config(bg=ajustar_color(color, 0.72), relief=tk.SUNKEN))
    btn.bind("<ButtonRelease-1>", lambda _e: btn.config(bg=ajustar_color(color, 1.04), relief=tk.FLAT))
    if fill:
        btn.pack(fill=tk.X, ipady=2)
    return btn


class InterfazBiblioteca:
    def __init__(self, ventana_principal):
        self.root = ventana_principal
        self.root.title("Nexus Library - Biblioteca Inteligente")
        self.root.geometry("1240x760")
        self.root.minsize(1040, 660)
        self.root.configure(bg=BG)

        self.biblioteca = Biblioteca()
        self.logo_img = None
        self.logo_small = None
        self.bg_login_original = None
        self.bg_login_tk = None
        self.frame_actual = None
        self.modo = "light"

        self.configurar_estilos()
        if not self.biblioteca.hay_datos_guardados():
            self.cargar_datos_ejemplo()
        self.mostrar_login()

    @property
    def theme(self):
        return THEMES[self.modo]

    def alternar_tema(self):
        self.modo = "dark" if self.modo == "light" else "light"
        self.root.configure(bg=self.theme["bg"])
        self.configurar_estilos()
        if isinstance(self.frame_actual, DashboardFrame):
            self.mostrar_dashboard()
        else:
            self.mostrar_login()

    def configurar_estilos(self):
        t = self.theme
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Treeview",
            rowheight=30,
            font=("Segoe UI", 9),
            borderwidth=0,
            background=t["surface"],
            foreground=t["text"],
            fieldbackground=t["surface"],
        )
        style.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", "white")])
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background=t["sidebar_2"],
            foreground="white",
            relief=tk.FLAT,
        )
        style.configure("TCombobox", padding=5)

    def cambiar_frame(self, frame):
        if self.frame_actual is not None:
            self.frame_actual.destroy()
        self.frame_actual = frame
        self.frame_actual.pack(fill=tk.BOTH, expand=True)

    def cargar_imagen(self, ruta, size):
        if Image is None or ImageTk is None:
            return None
        try:
            img = Image.open(ruta).convert("RGBA")
            img.thumbnail(size, Image.Resampling.LANCZOS)
            lienzo = Image.new("RGBA", size, (255, 255, 255, 0))
            x = (size[0] - img.width) // 2
            y = (size[1] - img.height) // 2
            lienzo.alpha_composite(img, (x, y))
            return ImageTk.PhotoImage(lienzo)
        except Exception:
            return None

    def mostrar_login(self):
        self.cambiar_frame(LoginFrame(self.root, self))

    def mostrar_dashboard(self):
        self.cambiar_frame(DashboardFrame(self.root, self))

    def cargar_datos_ejemplo(self):
        libros = [
            ("L001", "Cien Anos de Soledad", "Gabriel Garcia Marquez", 1967, "Novela"),
            ("L002", "Don Quijote", "Miguel de Cervantes", 1605, "Clasico"),
            ("L003", "1984", "George Orwell", 1949, "Distopia"),
            ("L004", "Orgullo y Prejuicio", "Jane Austen", 1813, "Romance"),
            ("L005", "Python Avanzado", "David Beazley", 2013, "Tecnico"),
            ("L006", "Estructuras de Datos", "Mark Allen Weiss", 2014, "Academico"),
            ("L007", "Algoritmos", "Robert Sedgewick", 2011, "Academico"),
        ]
        usuarios = [
            ("U001", "Juan Perez", "juan@email.com", "50221001"),
            ("U002", "Maria Garcia", "maria@email.com", "50221002"),
            ("U003", "Carlos Lopez", "carlos@email.com", "50221003"),
            ("U004", "Ana Martinez", "ana@email.com", "50221004"),
        ]
        for item in libros:
            self.biblioteca.registrar_libro(*item)
        for item in usuarios:
            self.biblioteca.registrar_usuario(*item)


class LoginFrame(tk.Frame):
    def __init__(self, master, app):
        t = app.theme
        super().__init__(master, bg=t["sidebar"])
        self.app = app
        self.fondo = None
        self.logo = app.cargar_imagen(asset_path("logo.png"), (250, 190))
        self.bg_original = None

        self.canvas = tk.Canvas(self, bg=t["sidebar"], highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cargar_fondo()
        self.canvas.bind("<Configure>", self.dibujar_fondo)

        panel = tk.Frame(self, bg=t["sidebar"], width=450, padx=24, pady=24)
        panel.pack(side=tk.RIGHT, fill=tk.Y)
        panel.pack_propagate(False)

        card = tk.Frame(panel, bg=t["card"], padx=34, pady=32, highlightthickness=1, highlightbackground=t["border"])
        card.pack(fill=tk.BOTH, expand=True)

        if self.logo:
            tk.Label(card, image=self.logo, bg=t["card"]).pack(pady=(0, 8))
        else:
            tk.Label(card, text="NEXUS", bg=t["card"], fg=t["text"], font=("Segoe UI", 28, "bold")).pack(pady=(0, 8))

        tk.Label(card, text="Biblioteca Inteligente", bg=t["card"], fg=t["text"],
                 font=("Segoe UI", 22, "bold")).pack(pady=(0, 4))
        tk.Label(card, text="Acceso administrativo", bg=t["card"], fg=t["muted"],
                 font=("Segoe UI", 10, "bold")).pack(pady=(0, 20))

        self.usuario = self.campo(card, "Usuario")
        self.clave = self.campo(card, "Contrasena", show="*")
        self.clave.bind("<Return>", lambda _e: self.login())

        boton(card, "ENTRAR AL SISTEMA", self.login, BLUE, fill=True)

        tk.Label(
            card,
            text="Credenciales de demostracion\nadmin / admin123",
            bg=t["card"],
            fg=t["muted"],
            justify=tk.LEFT,
            font=("Segoe UI", 9),
        ).pack(anchor=tk.W, pady=(18, 0))

        tk.Frame(card, bg=t["border"], height=1).pack(fill=tk.X, pady=20)
        boton(card, "Cambiar modo claro/oscuro", self.app.alternar_tema, PURPLE, fill=True)

        resumen = tk.Frame(card, bg=t["surface"], padx=16, pady=14, highlightthickness=1,
                           highlightbackground=t["border"])
        resumen.pack(fill=tk.X, pady=(22, 0))
        for etiqueta, valor, color in [
            ("Coleccion", len(self.app.biblioteca.libros), BLUE),
            ("Lectores", len(self.app.biblioteca.usuarios), CYAN),
            ("Disponibles", len(self.app.biblioteca.obtener_libros_disponibles()), GREEN),
        ]:
            item = tk.Frame(resumen, bg=t["surface"])
            item.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(item, text=str(valor), bg=t["surface"], fg=color,
                     font=("Segoe UI", 18, "bold")).pack()
            tk.Label(item, text=etiqueta, bg=t["surface"], fg=t["muted"],
                     font=("Segoe UI", 8, "bold")).pack()

    def campo(self, parent, label, show=None):
        t = self.app.theme
        tk.Label(parent, text=label, bg=t["card"], fg=t["text"], font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        entrada = tk.Entry(parent, show=show, bd=0, font=("Segoe UI", 12), highlightthickness=1,
                           highlightbackground="#cbd5e1", highlightcolor=BLUE)
        entrada.pack(fill=tk.X, ipady=8, pady=(6, 14))
        return entrada

    def cargar_fondo(self):
        if Image is None:
            return
        try:
            self.bg_original = Image.open(asset_path("biblioteca_fondo.png")).convert("RGB")
        except Exception:
            self.bg_original = None

    def dibujar_fondo(self, event=None):
        ancho = max(self.canvas.winfo_width(), 600)
        alto = max(self.canvas.winfo_height(), 660)
        self.canvas.delete("all")
        if self.bg_original is not None and ImageTk is not None:
            img = self.bg_original.resize((ancho, alto), Image.Resampling.LANCZOS)
            self.fondo = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.fondo, anchor="nw")
            self.canvas.create_rectangle(0, 0, ancho, alto, fill="#020617", stipple="gray25", outline="")
        else:
            self.canvas.create_rectangle(0, 0, ancho, alto, fill=DARK, outline="")
        self.canvas.create_text(48, 58, anchor=tk.W, text="Nexus Library", fill="white",
                                font=("Segoe UI", 38, "bold"))
        self.canvas.create_text(50, 108, anchor=tk.W, text="Biblioteca moderna, visual y profesional",
                                fill="#bae6fd", font=("Segoe UI", 15, "bold"))
        self.canvas.create_text(50, alto - 108, anchor=tk.W,
                                text="Gestion inteligente de catalogos, usuarios y prestamos",
                                fill="white", font=("Segoe UI", 18, "bold"))
        self.canvas.create_text(52, alto - 72, anchor=tk.W,
                                text="Panel con estadisticas, graficos y experiencia visual renovada.",
                                fill="#dbeafe", font=("Segoe UI", 12))

    def login(self):
        if self.usuario.get().strip() == "admin" and self.clave.get().strip() == "admin123":
            self.app.mostrar_dashboard()
        else:
            messagebox.showerror("Acceso denegado", "Use admin / admin123 para entrar.")


class DashboardFrame(tk.Frame):
    def __init__(self, master, app):
        self.t = app.theme
        super().__init__(master, bg=self.t["bg"])
        self.app = app
        self.bib = app.biblioteca
        self.logo = app.cargar_imagen(asset_path("logo.png"), (150, 106))
        self.logo_hero = app.cargar_imagen(asset_path("logo.png"), (250, 178))
        self.biblioteca_img = app.cargar_imagen(asset_path("biblioteca_fondo.png"), (440, 230))
        self.seccion = None

        self.sidebar = tk.Frame(self, bg=self.t["sidebar"], width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self, bg=self.t["bg"])
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.crear_sidebar()
        self.mostrar_inicio()

    def crear_sidebar(self):
        marca = tk.Frame(self.sidebar, bg=self.t["sidebar"], padx=18, pady=18)
        marca.pack(fill=tk.X)
        if self.logo:
            tk.Label(marca, image=self.logo, bg=self.t["sidebar"]).pack(anchor=tk.W)
        tk.Label(marca, text="Nexus Library", bg=self.t["sidebar"], fg="white",
                 font=("Segoe UI", 20, "bold")).pack(anchor=tk.W, pady=(4, 0))
        tk.Label(marca, text="Biblioteca inteligente", bg=self.t["sidebar"], fg="#7dd3fc",
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)

        opciones = [
            ("Inicio", self.mostrar_inicio),
            ("Libros", self.mostrar_libros),
            ("Usuarios", self.mostrar_usuarios),
            ("Prestamos", self.mostrar_prestamos),
            ("Busqueda", self.mostrar_busqueda),
            ("Espera", self.mostrar_espera),
            ("Estructuras", self.mostrar_estructuras),
            ("Reportes", self.mostrar_reportes),
        ]
        for texto, comando in opciones:
            btn = tk.Button(self.sidebar, text=texto, command=comando, bg=self.t["sidebar_2"], fg="white",
                            activebackground=BLUE, activeforeground="white", bd=0,
                            font=("Segoe UI", 10, "bold"), cursor="hand2", anchor=tk.W,
                            padx=22, pady=11)
            btn.pack(fill=tk.X, padx=14, pady=4)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BLUE))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.t["sidebar_2"]))
            btn.bind("<ButtonPress-1>", lambda e, b=btn: b.config(bg=ajustar_color(BLUE, 0.72)))
            btn.bind("<ButtonRelease-1>", lambda e, b=btn: b.config(bg=BLUE))

        boton(self.sidebar, "Modo claro/oscuro", self.app.alternar_tema, PURPLE).pack(
            side=tk.BOTTOM, fill=tk.X, padx=14, pady=(0, 8)
        )

        tk.Button(self.sidebar, text="Cerrar sesion", command=self.app.mostrar_login,
                  bg=RED, fg="white", activebackground="#b91c1c", activeforeground="white",
                  bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2", padx=18, pady=10).pack(
            side=tk.BOTTOM, fill=tk.X, padx=14, pady=18
        )

    def limpiar(self):
        limpiar(self.content)

    def titulo(self, titulo, subtitulo):
        cab = tk.Frame(self.content, bg=self.t["bg"])
        cab.pack(fill=tk.X, padx=28, pady=(24, 10))
        tk.Label(cab, text=titulo, bg=self.t["bg"], fg=self.t["text"], font=("Segoe UI", 24, "bold")).pack(anchor=tk.W)
        tk.Label(cab, text=subtitulo, bg=self.t["bg"], fg=self.t["muted"], font=("Segoe UI", 10)).pack(anchor=tk.W)

    def panel(self, parent=None, **pack):
        contenedor = parent or self.content
        frame = tk.Frame(contenedor, bg=self.t["card"], padx=16, pady=16, highlightthickness=1,
                         highlightbackground=self.t["border"])
        frame.pack(**pack)
        return frame

    def card_metrica(self, parent, titulo, valor, color):
        card = tk.Frame(parent, bg=self.t["card"], padx=16, pady=14, highlightthickness=1,
                        highlightbackground=self.t["border"])
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        tk.Label(card, text=titulo, bg=self.t["card"], fg=self.t["muted"], font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        tk.Label(card, text=str(valor), bg=self.t["card"], fg=color, font=("Segoe UI", 24, "bold")).pack(anchor=tk.W)

    def tabla(self, parent, columnas, filas, alto=12):
        marco = tk.Frame(parent, bg=self.t["card"])
        marco.pack(fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(marco)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree = ttk.Treeview(marco, columns=columnas, show="headings", height=alto, yscrollcommand=scroll.set)
        scroll.config(command=tree.yview)
        for col in columnas:
            tree.heading(col, text=col, anchor=tk.W)
            tree.column(col, width=130, anchor=tk.W)

        for fila in filas:
            tree.insert("", tk.END, values=fila)
        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def etiqueta_form(self, parent, texto, row, column):
        tk.Label(parent, text=texto, bg=self.t["card"], fg=self.t["text"],
                 font=("Segoe UI", 9, "bold")).grid(row=row, column=column, sticky=tk.W)

    def validar_campos(self, campos, nombres):
        vacios = [nombres[key] for key, entrada in campos.items() if not entrada.get().strip()]
        if vacios:
            messagebox.showwarning("Datos incompletos", "Complete estos campos: " + ", ".join(vacios))
            return False
        return True

    def confirmar_accion_peligrosa(self, titulo, detalle, palabra="ELIMINAR"):
        if not messagebox.askyesno(titulo, detalle + "\n\nEsta accion no se puede deshacer."):
            return False
        respuesta = simpledialog.askstring(
            titulo,
            f"Para confirmar definitivamente, escriba {palabra}:",
            parent=self,
        )
        if respuesta != palabra:
            messagebox.showwarning("Accion cancelada", f"No se escribio {palabra}. No se realizo ningun cambio.")
            return False
        return True

    def tarjeta_color(self, parent, titulo, texto, color):
        card = tk.Frame(parent, bg=color, padx=16, pady=14)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
        tk.Label(card, text=titulo, bg=color, fg="white",
                 font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        tk.Label(card, text=texto, bg=color, fg="#eef6ff", justify=tk.LEFT,
                 wraplength=220, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(6, 0))
        return card

    def mostrar_inicio(self):
        self.limpiar()
        stats = self.bib.obtener_estadisticas()

        hero = tk.Frame(self.content, bg=self.t["hero"], padx=24, pady=18, highlightthickness=0)
        hero.pack(fill=tk.X, padx=28, pady=(24, 12))
        hero_text = tk.Frame(hero, bg=self.t["hero"])
        hero_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(hero_text, text="Nexus Library", bg=self.t["hero"], fg="white",
                 font=("Segoe UI", 30, "bold")).pack(anchor=tk.W)
        tk.Label(hero_text, text="Panel profesional de biblioteca inteligente", bg=self.t["hero"],
                 fg="#bfdbfe", font=("Segoe UI", 13, "bold")).pack(anchor=tk.W, pady=(2, 10))
        tk.Label(hero_text, text="Catalogo, prestamos, lectores y reportes en una experiencia moderna.",
                 bg=self.t["hero"], fg="#e0f2fe", font=("Segoe UI", 10)).pack(anchor=tk.W)
        if self.logo_hero:
            tk.Label(hero, image=self.logo_hero, bg=self.t["hero"]).pack(side=tk.RIGHT, padx=(20, 0))

        fila = tk.Frame(self.content, bg=self.t["bg"])
        fila.pack(fill=tk.X, padx=20, pady=6)
        self.card_metrica(fila, "Libros", stats["total_libros"], BLUE)
        self.card_metrica(fila, "Usuarios", stats["total_usuarios"], CYAN)
        self.card_metrica(fila, "Disponibles", stats["libros_disponibles"], GREEN)
        self.card_metrica(fila, "Prestamos activos", stats["prestamos_activos"], ORANGE)

        destacados = tk.Frame(self.content, bg=self.t["bg"])
        destacados.pack(fill=tk.X, padx=22, pady=(6, 2))
        self.tarjeta_color(destacados, "Busqueda rapida",
                           "El catalogo se organiza para encontrar libros por codigo, titulo o autor.",
                           BLUE)
        self.tarjeta_color(destacados, "Control de prestamos",
                           "Cada prestamo actualiza disponibilidad, historial y reportes.",
                           GREEN)
        self.tarjeta_color(destacados, "Seguridad",
                           "Las acciones delicadas piden doble confirmacion antes de ejecutarse.",
                           PURPLE)

        cuerpo = tk.Frame(self.content, bg=self.t["bg"])
        cuerpo.pack(fill=tk.BOTH, expand=True, padx=28, pady=10)
        izquierda = self.panel(cuerpo, side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        derecha = self.panel(cuerpo, side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(izquierda, text="Ultimas acciones", bg=self.t["card"], fg=self.t["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))
        filas = [(a.timestamp.strftime("%H:%M:%S"), a.tipo, a.descripcion) for a in self.bib.obtener_historial(10)]
        self.tabla(izquierda, ("Hora", "Tipo", "Descripcion"), filas, 7)
        tk.Label(izquierda, text="Actividad por tipo", bg=self.t["card"], fg=self.t["text"],
                 font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(16, 8))
        actividad = tk.Canvas(izquierda, bg=self.t["canvas"], height=150, highlightthickness=1,
                              highlightbackground=self.t["border"])
        actividad.pack(fill=tk.X)
        actividad.bind("<Configure>", lambda _e: self.dibujar_actividad_reciente(actividad))

        foto = tk.Frame(derecha, bg=self.t["card"])
        foto.pack(fill=tk.X)
        if self.biblioteca_img:
            tk.Label(foto, image=self.biblioteca_img, bg=self.t["card"]).pack(fill=tk.X)
        tk.Label(derecha, text="Estadisticas de coleccion", bg=self.t["card"], fg=self.t["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor=tk.W, pady=(14, 8))
        graficos = tk.Frame(derecha, bg=self.t["card"])
        graficos.pack(fill=tk.BOTH, expand=True)
        barras = tk.Canvas(graficos, bg=self.t["canvas"], height=190, highlightthickness=1,
                           highlightbackground=self.t["border"])
        barras.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        pastel = tk.Canvas(graficos, bg=self.t["canvas"], height=190, width=210, highlightthickness=1,
                           highlightbackground=self.t["border"])
        pastel.pack(side=tk.RIGHT, fill=tk.Y)
        barras.bind("<Configure>", lambda _e: self.dibujar_barras_categorias(barras))
        pastel.bind("<Configure>", lambda _e: self.dibujar_pastel_disponibilidad(pastel, stats))

    def dibujar_actividad_reciente(self, canvas):
        canvas.delete("all")
        acciones = self.bib.obtener_historial(20)
        conteo = {}
        for accion in acciones:
            nombre = accion.tipo.replace("REGISTRO_", "NUEVO_").replace("ELIMINACION_", "ELIM_")
            conteo[nombre] = conteo.get(nombre, 0) + 1
        datos = sorted(conteo.items(), key=lambda item: item[1], reverse=True)[:4]
        if not datos:
            canvas.create_text(20, 70, anchor=tk.W, text="Sin actividad reciente",
                               fill=self.t["muted"], font=("Segoe UI", 10, "bold"))
            return
        ancho = max(canvas.winfo_width(), 420)
        maximo = max(valor for _tipo, valor in datos)
        colores = [BLUE, CYAN, ORANGE, PINK]
        for i, (tipo, valor) in enumerate(datos):
            x = 24 + i * ((ancho - 48) / max(len(datos), 1))
            bar_w = min(78, (ancho - 80) / max(len(datos), 1) - 18)
            alto = 24 + int(72 * valor / maximo)
            color = colores[i % len(colores)]
            canvas.create_rectangle(x, 112 - alto, x + bar_w, 112, fill=color, outline="")
            canvas.create_text(x + bar_w / 2, 122, text=tipo[:12], fill=self.t["muted"],
                               font=("Segoe UI", 8, "bold"))
            canvas.create_text(x + bar_w / 2, 104 - alto, text=str(valor), fill=self.t["text"],
                               font=("Segoe UI", 10, "bold"))

    def dibujar_barras_categorias(self, canvas):
        canvas.delete("all")
        libros = self.bib.listar_libros()
        conteo = {}
        for libro in libros:
            conteo[libro.categoria] = conteo.get(libro.categoria, 0) + 1
        datos = sorted(conteo.items(), key=lambda item: item[1], reverse=True)[:5]
        if not datos:
            return
        ancho = max(canvas.winfo_width(), 320)
        colores = [BLUE, CYAN, GREEN, ORANGE, PINK]
        maximo = max(valor for _cat, valor in datos)
        canvas.create_text(18, 18, anchor=tk.W, text="Libros por categoria", fill=self.t["text"],
                           font=("Segoe UI", 10, "bold"))
        for i, (categoria, valor) in enumerate(datos):
            y = 48 + i * 26
            largo = int((ancho - 160) * (valor / maximo))
            color = colores[i % len(colores)]
            canvas.create_text(18, y + 8, anchor=tk.W, text=categoria[:14], fill=self.t["muted"],
                               font=("Segoe UI", 8, "bold"))
            canvas.create_rectangle(118, y, 118 + largo, y + 16, fill=color, outline="")
            canvas.create_text(126 + largo, y + 8, anchor=tk.W, text=str(valor), fill=self.t["text"],
                               font=("Segoe UI", 8, "bold"))

    def dibujar_pastel_disponibilidad(self, canvas, stats):
        canvas.delete("all")
        total = max(stats["total_libros"], 1)
        disponibles = stats["libros_disponibles"]
        ocupados = total - disponibles
        x0, y0, x1, y1 = 42, 38, 168, 164
        grados_disp = int(360 * disponibles / total)
        canvas.create_arc(x0, y0, x1, y1, start=90, extent=grados_disp, fill=GREEN, outline="")
        canvas.create_arc(x0, y0, x1, y1, start=90 + grados_disp, extent=360 - grados_disp, fill=ORANGE, outline="")
        canvas.create_oval(76, 72, 134, 130, fill=self.t["canvas"], outline="")
        canvas.create_text(105, 92, text=f"{disponibles}/{total}", fill=self.t["text"], font=("Segoe UI", 12, "bold"))
        canvas.create_text(105, 112, text="libros", fill=self.t["muted"], font=("Segoe UI", 8, "bold"))
        canvas.create_text(18, 18, anchor=tk.W, text="Disponibilidad", fill=self.t["text"],
                           font=("Segoe UI", 10, "bold"))
        canvas.create_rectangle(24, 174, 34, 184, fill=GREEN, outline="")
        canvas.create_text(40, 179, anchor=tk.W, text=f"Disponibles {disponibles}", fill=self.t["muted"],
                           font=("Segoe UI", 8, "bold"))
        canvas.create_rectangle(118, 174, 128, 184, fill=ORANGE, outline="")
        canvas.create_text(134, 179, anchor=tk.W, text=f"Ocupados {ocupados}", fill=self.t["muted"],
                           font=("Segoe UI", 8, "bold"))

    def mostrar_libros(self):
        self.limpiar()
        self.titulo("Gestion de libros", "Registro, eliminacion y catalogo enlazado")
        form = self.panel(fill=tk.X, padx=28, pady=8)
        campos = {}
        categorias_disponibles = [
            "Ficcion", "Clasico", "Distopia", "Romance", "Tecnico", "Academico", "Novela"
        ]
        for i, (label, key, width) in enumerate([
            ("Codigo", "codigo", 10), ("Titulo", "titulo", 20), ("Autor", "autor", 18),
            ("Anio", "anio", 7), ("Categoria", "categoria", 13), ("Stock", "stock", 6)
        ]):
            self.etiqueta_form(form, label, 0, i)
            if key == "categoria":
                ent = ttk.Combobox(form, values=categorias_disponibles, state="readonly", width=width)
                ent.grid(row=1, column=i, padx=(0, 10), pady=6, ipady=5)
                ent.set(categorias_disponibles[0] if categorias_disponibles else "")
            else:
                ent = tk.Entry(form, width=width, font=("Segoe UI", 10))
                ent.grid(row=1, column=i, padx=(0, 10), pady=6, ipady=5)
            campos[key] = ent
        campos["stock"].insert(0, "1")


        def registrar():
            if not self.validar_campos(campos, {
                "codigo": "Codigo", "titulo": "Titulo", "autor": "Autor",
                "anio": "Anio", "categoria": "Categoria", "stock": "Stock"
            }):
                return

            # Año: entero (sin decimales)
            anio_txt = campos["anio"].get().strip()
            try:
                anio = int(anio_txt)
            except ValueError:
                messagebox.showerror("Dato invalido", "El anio debe ser un numero entero.")
                return

            # Categoría: string (no vacío)
            categoria = campos["categoria"].get().strip()
            if not isinstance(categoria, str) or not categoria:
                messagebox.showerror("Dato invalido", "La categoria debe ser un texto no vacio.")
                return

            try:
                stock = int(campos["stock"].get().strip())
                if stock < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Dato invalido", "El stock debe ser un numero entero (0 o mayor).")
                return

            ok, msg = self.bib.registrar_libro(
                campos["codigo"].get().strip(), campos["titulo"].get().strip(),
                campos["autor"].get().strip(), anio,
                campos["categoria"].get().strip(), stock
            )
            if ok:
                messagebox.showinfo("Libro registrado", msg)
                self.mostrar_libros()
            else:
                messagebox.showerror("No registrado", msg)

        boton(form, "Registrar", registrar, GREEN).grid(row=1, column=6, ipady=3, ipadx=8)

        lista = self.panel(fill=tk.BOTH, expand=True, padx=28, pady=8)
        filas = [(l.codigo, l.titulo, l.autor, l.anio_publicacion, l.categoria, l.stock, l.estado.value, l.cantidad_prestamos)
                 for l in self.bib.listar_libros()]
        tree = self.tabla(lista, ("Codigo", "Titulo", "Autor", "Anio", "Categoria", "Stock", "Estado", "Prestamos"), filas, 15)

        def eliminar():
            item = tree.focus()
            if not item:
                messagebox.showwarning("Seleccione", "Seleccione un libro.")
                return
            codigo = tree.item(item, "values")[0]
            titulo = tree.item(item, "values")[1]
            if not self.confirmar_accion_peligrosa(
                "Eliminar libro",
                f"Esta por eliminar el libro {codigo} - {titulo}."
            ):
                return
            ok, msg = self.bib.eliminar_libro(codigo)
            messagebox.showinfo("Resultado", msg) if ok else messagebox.showerror("Error", msg)
            self.mostrar_libros()

        boton(lista, "Eliminar seleccionado", eliminar, RED).pack(anchor=tk.E, pady=(12, 0))

    def mostrar_usuarios(self):
        self.limpiar()
        self.titulo("Gestion de usuarios", "Registro de lectores de la biblioteca")

        # Revisa préstamos retrasados y actualiza el estado moroso de cada usuario
        self.bib.actualizar_morosos()

        def validar_usuario(id_usuario, nombre, email, telefono):
            # Teléfono: exactamente 8 dígitos
            tel = telefono.strip()
            if not tel.isdigit() or len(tel) != 8:
                return False, "El telefono debe tener exactamente 8 digitos."

            # Email: debe tener un dominio valido (ejemplo: usuario@gmail.com)
            em = email.strip().lower()
            if not re.match(r'^[^@\s]+@[^@\s]+\.[a-z]{2,}$', em):
                return False, "El email debe incluir un dominio valido (ejemplo: usuario@gmail.com)."

            # Campos básicos
            if not id_usuario.strip():
                return False, "El ID no puede estar vacio."
            if not nombre.strip():
                return False, "El nombre no puede estar vacio."

            return True, "OK"

        form = self.panel(fill=tk.X, padx=28, pady=8)
        campos = {}
        for i, (label, key, width) in enumerate([
            ("ID", "id", 10), ("Nombre", "nombre", 22), ("Email", "email", 22),
            ("Telefono", "telefono", 14)
        ]):
            self.etiqueta_form(form, label, 0, i)
            ent = tk.Entry(form, width=width, font=("Segoe UI", 10))
            ent.grid(row=1, column=i, padx=(0, 10), pady=6, ipady=5)
            campos[key] = ent

        def registrar():
            if not self.validar_campos(campos, {
                "id": "ID", "nombre": "Nombre", "email": "Email",
                "telefono": "Telefono"
            }):
                return

            id_usuario = campos["id"].get().strip()
            nombre = campos["nombre"].get().strip()
            email = campos["email"].get().strip()
            telefono = campos["telefono"].get().strip()

            ok_validar, msg_validar = validar_usuario(id_usuario, nombre, email, telefono)
            if not ok_validar:
                messagebox.showerror("Dato invalido", msg_validar)
                return

            ok, msg = self.bib.registrar_usuario(id_usuario, nombre, email, telefono)
            messagebox.showinfo("Usuario", msg) if ok else messagebox.showerror("Error", msg)
            if ok:
                self.mostrar_usuarios()

        boton(form, "Registrar", registrar, GREEN).grid(row=1, column=4, ipady=3, ipadx=8)

        lista = self.panel(fill=tk.BOTH, expand=True, padx=28, pady=8)
        filas = [(u.id_usuario, u.nombre, u.email, u.telefono, len(u.libros_activos), u.estado.value)
                 for u in self.bib.listar_usuarios()]
        tree = self.tabla(lista, ("ID", "Nombre", "Email", "Telefono", "Libros activos", "Estado"), filas, 11)


        def ejecutar_eliminar():
            item = tree.focus()
            if not item:
                messagebox.showwarning("Seleccione", "Seleccione un usuario.")
                return
            values = tree.item(item, "values")
            id_usuario = values[0]
            nombre = values[1]

            if not self.confirmar_accion_peligrosa(
                "Eliminar usuario",
                f"Esta por eliminar el usuario {id_usuario} - {nombre}."
            ):
                return

            ok, msg = self.bib.eliminar_usuario(id_usuario)
            if ok:
                messagebox.showinfo("Resultado", msg)
                self.mostrar_usuarios()
            else:
                messagebox.showerror("Error", msg)

        boton(lista, "Eliminar seleccionado", ejecutar_eliminar, RED).pack(anchor=tk.E, pady=(12, 0))


    def mostrar_prestamos(self):
        self.limpiar()
        self.titulo("Prestamos y devoluciones", "Si no hay stock, el usuario se agrega automaticamente a la cola de espera (FIFO)")
        form = self.panel(fill=tk.X, padx=28, pady=8)
        self.etiqueta_form(form, "Codigo libro", 0, 0)
        codigo = tk.Entry(form, width=18, font=("Segoe UI", 10))
        codigo.grid(row=1, column=0, padx=(0, 10), pady=6, ipady=5)
        self.etiqueta_form(form, "ID usuario", 0, 1)
        usuario = tk.Entry(form, width=18, font=("Segoe UI", 10))
        usuario.grid(row=1, column=1, padx=(0, 10), pady=6, ipady=5)

        def prestar():
            if not codigo.get().strip() or not usuario.get().strip():
                messagebox.showwarning("Datos incompletos", "Ingrese codigo de libro e ID de usuario.")
                return
            ok, msg = self.bib.realizar_prestamo(codigo.get().strip(), usuario.get().strip())
            messagebox.showinfo("Prestamo", msg) if ok else messagebox.showerror("Error", msg)
            self.mostrar_prestamos()

        boton(form, "Realizar prestamo", prestar, BLUE).grid(row=1, column=2, ipady=3, ipadx=8)
        lista = self.panel(fill=tk.BOTH, expand=True, padx=28, pady=8)
        filas = []
        for p in self.bib.obtener_prestamos_activos():
            libro = self.bib.obtener_libro(p.codigo_libro)
            usuario_obj = self.bib.obtener_usuario(p.id_usuario)
            filas.append((p.id_prestamo, libro.titulo if libro else p.codigo_libro,
                          usuario_obj.nombre if usuario_obj else p.id_usuario,
                          p.fecha_prestamo.strftime("%Y-%m-%d"),
                          p.fecha_devolucion_esperada.strftime("%Y-%m-%d"), p.estado.value))
        tree = self.tabla(lista, ("ID", "Libro", "Usuario", "Fecha", "Vence", "Estado"), filas, 14)

        def devolver():
            item = tree.focus()
            if not item:
                messagebox.showwarning("Seleccione", "Seleccione un prestamo activo.")
                return
            ok, msg = self.bib.devolver_libro(int(tree.item(item, "values")[0]))
            messagebox.showinfo("Devolucion", msg) if ok else messagebox.showerror("Error", msg)
            self.mostrar_prestamos()

        boton(lista, "Devolver seleccionado", devolver, ORANGE).pack(anchor=tk.E, pady=(12, 0))

    def mostrar_busqueda(self):
        self.limpiar()
        self.titulo("Busqueda inteligente", "Consulta por codigo, titulo, autor, categoria o coincidencia parcial")
        form = self.panel(fill=tk.X, padx=28, pady=8)
        entrada = tk.Entry(form, width=34, font=("Segoe UI", 11))
        entrada.pack(side=tk.LEFT, padx=(0, 10), ipady=7)
        tipo = ttk.Combobox(form, values=("Codigo", "Titulo", "Autor", "Categoria", "Similar"), state="readonly", width=16)
        tipo.set("Codigo")
        tipo.pack(side=tk.LEFT, padx=(0, 10))
        contenedor = self.panel(fill=tk.BOTH, expand=True, padx=28, pady=8)

        def buscar():
            limpiar(contenedor)
            termino = entrada.get().strip()
            resultados = []
            if tipo.get() == "Codigo":
                libro = self.bib.buscar_por_codigo(termino)
                if libro:
                    resultados = [libro]
                comparacion = self.bib.comparar_busqueda_secuencial_vs_arbol(termino)
                tk.Label(contenedor, text=f"Comparacion: lista {comparacion['pasos_lista']} pasos vs arbol {comparacion['pasos_arbol']} pasos",
                         bg=self.t["card"], fg=BLUE, font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
            elif tipo.get() == "Titulo":
                libro = self.bib.buscar_por_titulo(termino)
                resultados = [libro] if libro else []
            elif tipo.get() == "Autor":
                libro = self.bib.buscar_por_autor(termino)
                resultados = [libro] if libro else []
            elif tipo.get() == "Categoria":
                resultados = self.bib.buscar_por_categoria(termino)
            else:
                resultados = self.bib.buscar_similares(termino)
            filas = [(l.codigo, l.titulo, l.autor, l.categoria, l.stock, l.estado.value) for l in resultados]
            self.tabla(contenedor, ("Codigo", "Titulo", "Autor", "Categoria", "Stock", "Estado"), filas, 15)

        boton(form, "Buscar", buscar, BLUE).pack(side=tk.LEFT)

    def mostrar_espera(self):
        self.limpiar()
        self.titulo("Lista de espera", "Cola FIFO para libros no disponibles")
        form = self.panel(fill=tk.X, padx=28, pady=8)
        codigo = tk.Entry(form, width=18, font=("Segoe UI", 10))
        usuario = tk.Entry(form, width=18, font=("Segoe UI", 10))
        self.etiqueta_form(form, "Codigo libro", 0, 0)
        self.etiqueta_form(form, "ID usuario", 0, 1)
        codigo.grid(row=1, column=0, padx=(0, 10), pady=6, ipady=5)
        usuario.grid(row=1, column=1, padx=(0, 10), pady=6, ipady=5)

        def agregar():
            if not codigo.get().strip() or not usuario.get().strip():
                messagebox.showwarning("Datos incompletos", "Ingrese codigo de libro e ID de usuario.")
                return
            ok, msg = self.bib.agregar_a_espera(codigo.get().strip(), usuario.get().strip())
            messagebox.showinfo("Espera", msg) if ok else messagebox.showerror("Error", msg)
            self.mostrar_espera()

        boton(form, "Agregar a cola", agregar, CYAN).grid(row=1, column=2, ipady=3, ipadx=8)
        lista = self.panel(fill=tk.BOTH, expand=True, padx=28, pady=8)
        filas = []
        for codigo_libro, cola in self.bib.colas_espera.items():
            libro = self.bib.obtener_libro(codigo_libro)
            for pos, id_usuario in enumerate(cola, 1):
                usuario_obj = self.bib.obtener_usuario(id_usuario)
                filas.append((codigo_libro, libro.titulo if libro else "", pos, id_usuario,
                              usuario_obj.nombre if usuario_obj else ""))
        self.tabla(lista, ("Libro", "Titulo", "Posicion", "Usuario", "Nombre"), filas, 16)

    def mostrar_estructuras(self):
        self.limpiar()
        self.titulo("Mapa del catalogo", "Asi se organizan los libros para buscarlos mas rapido")
        tarjetas = tk.Frame(self.content, bg=self.t["bg"])
        tarjetas.pack(fill=tk.X, padx=22, pady=(0, 8))
        self.tarjeta_color(tarjetas, "Arbol de busqueda",
                           "Agrupa los codigos para ubicar un libro con menos comparaciones.",
                           BLUE)
        self.tarjeta_color(tarjetas, "Flujo de libros",
                           "Muestra el recorrido del catalogo como una cadena ordenada.",
                           CYAN)
        self.tarjeta_color(tarjetas, "Historial",
                           "Cada registro importante queda guardado como evidencia de trabajo.",
                           GREEN)

        cuerpo = tk.Frame(self.content, bg=self.t["bg"])
        cuerpo.pack(fill=tk.BOTH, expand=True, padx=28, pady=8)
        izq = self.panel(cuerpo, side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        der = self.panel(cuerpo, side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(izq, text="Arbol visual del catalogo", bg=self.t["card"], fg=self.t["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor=tk.W)
        tk.Label(izq, text="Cada nodo representa un libro. El codigo permite ordenar y buscar rapidamente.",
                 bg=self.t["card"], fg=self.t["muted"], font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(2, 10))
        canvas = tk.Canvas(izq, bg=self.t["canvas"], highlightthickness=1,
                           highlightbackground=self.t["border"], height=390)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.bind("<Configure>", lambda _e: self.dibujar_arbol(canvas))

        tk.Label(der, text="Flujo de libros", bg=self.t["card"], fg=self.t["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor=tk.W)
        tk.Label(der, text="El catalogo tambien se recorre libro por libro, como una ruta de lectura.",
                 bg=self.t["card"], fg=self.t["muted"], font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(2, 10))
        flujo = tk.Canvas(der, bg=self.t["canvas"], highlightthickness=1,
                          highlightbackground=self.t["border"], height=220)
        flujo.pack(fill=tk.X)
        flujo.bind("<Configure>", lambda _e: self.dibujar_flujo_catalogo(flujo))

        resumen = tk.Frame(der, bg=self.t["surface"], padx=16, pady=14,
                           highlightthickness=1, highlightbackground=self.t["border"])
        resumen.pack(fill=tk.X, pady=(14, 0))
        tk.Label(resumen, text="Explicacion sencilla", bg=self.t["surface"], fg=self.t["text"],
                 font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        tk.Label(
            resumen,
            text=("El sistema no guarda los libros solo como una lista plana. "
                  "Tambien crea indices para que una busqueda por codigo, titulo o autor sea mas directa. "
                  "Por eso el usuario encuentra informacion rapido aunque el catalogo crezca."),
            bg=self.t["surface"],
            fg=self.t["muted"],
            justify=tk.LEFT,
            wraplength=470,
            font=("Segoe UI", 10),
        ).pack(anchor=tk.W, pady=(8, 0))

        datos = tk.Frame(der, bg=self.t["card"])
        datos.pack(fill=tk.X, pady=(14, 0))
        self.card_metrica(datos, "Nodos", len(self.bib.libros), BLUE)
        self.card_metrica(datos, "Ruta", len(self.bib.recorrer_catalogo_enlazado()), CYAN)
        self.card_metrica(datos, "Acciones", len(self.bib.obtener_historial(50)), GREEN)

    def dibujar_arbol(self, canvas):
        canvas.delete("all")
        libros = sorted(self.bib.listar_libros(), key=lambda libro: libro.codigo)
        if not libros:
            return
        ancho = max(canvas.winfo_width(), 520)
        niveles = []

        def construir(items, nivel=0, x_min=40, x_max=None, padre=None):
            if not items:
                return
            if x_max is None:
                x_max = ancho - 40
            medio = len(items) // 2
            libro = items[medio]
            x = (x_min + x_max) / 2
            y = 58 + nivel * 92
            niveles.append((libro, x, y, padre))
            construir(items[:medio], nivel + 1, x_min, x, (x, y))
            construir(items[medio + 1:], nivel + 1, x, x_max, (x, y))

        construir(libros)
        for _libro, x, y, padre in niveles:
            if padre:
                canvas.create_line(padre[0], padre[1] + 28, x, y - 28, fill="#5b6f91", width=2)
        colores = [BLUE, CYAN, GREEN, ORANGE, PINK, PURPLE]
        for i, (libro, x, y, _padre) in enumerate(niveles):
            color = colores[i % len(colores)]
            canvas.create_oval(x - 36, y - 30, x + 36, y + 30, fill=color, outline="")
            canvas.create_text(x, y - 5, text=libro.codigo, fill="white", font=("Segoe UI", 10, "bold"))
            canvas.create_text(x, y + 12, text=libro.categoria[:10], fill="#eef6ff", font=("Segoe UI", 7, "bold"))

    def dibujar_flujo_catalogo(self, canvas):
        canvas.delete("all")
        libros = self.bib.recorrer_catalogo_enlazado()
        if not libros:
            canvas.create_text(20, 100, anchor=tk.W, text="Catalogo vacio",
                               fill=self.t["muted"], font=("Segoe UI", 10, "bold"))
            return
        ancho = max(canvas.winfo_width(), 420)
        paso = (ancho - 100) / max(len(libros) - 1, 1)
        radio = max(18, min(32, paso / 2 - 6))
        y = 92
        colores = [BLUE, CYAN, GREEN, ORANGE, PINK, PURPLE]
        for i, libro in enumerate(libros):
            x = 44 + i * paso
            if i < len(libros) - 1:
                canvas.create_line(x + radio + 6, y, x + paso - radio - 6, y, fill="#5b6f91", width=3, arrow=tk.LAST)
            color = colores[i % len(colores)]
            canvas.create_oval(x - radio, y - radio, x + radio, y + radio, fill=color, outline="")
            canvas.create_text(x, y - 6, text=libro.codigo, fill="white", font=("Segoe UI", 10, "bold"))
            canvas.create_text(x, y + 12, text=str(i + 1), fill="#eef6ff", font=("Segoe UI", 8, "bold"))
            canvas.create_text(x, y + 52, text=libro.titulo[:14], fill=self.t["muted"],
                               font=("Segoe UI", 8, "bold"))

    def mostrar_reportes(self):
        self.limpiar()
        self.titulo("Reportes", "Libros mas prestados, historial y recomendaciones")
        cuerpo = tk.Frame(self.content, bg=self.t["bg"])
        cuerpo.pack(fill=tk.BOTH, expand=True, padx=28, pady=8)
        top = self.panel(cuerpo, side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        hist = self.panel(cuerpo, side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        tk.Label(top, text="Libros mas prestados", bg=self.t["card"], fg=self.t["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))
        filas = [(l.codigo, l.titulo, l.autor, cantidad) for l, cantidad in self.bib.obtener_libros_mas_prestados(10)]
        self.tabla(top, ("Codigo", "Titulo", "Autor", "Prestamos"), filas, 12)
        tk.Label(hist, text="Historial completo", bg=self.t["card"], fg=self.t["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))
        filas_hist = [(a.timestamp.strftime("%Y-%m-%d %H:%M"), a.tipo, a.descripcion)
                      for a in self.bib.obtener_historial(50)]
        self.tabla(hist, ("Fecha", "Tipo", "Descripcion"), filas_hist, 12)


def main():
    ventana = tk.Tk()
    InterfazBiblioteca(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()