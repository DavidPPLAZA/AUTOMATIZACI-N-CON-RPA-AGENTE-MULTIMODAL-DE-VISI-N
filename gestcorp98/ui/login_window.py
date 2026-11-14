import tkinter as tk

from gestcorp98 import config


class LoginFrame(tk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, bg=config.BG_COLOR)
        self._on_success = on_success
        self._build()

    def _build(self) -> None:
        title = tk.Label(
            self,
            text=config.APP_TITLE,
            bg=config.TITLE_BG,
            fg="white",
            font=(config.FONT_FAMILY, 11, "bold"),
            pady=8,
        )
        title.pack(fill="x")

        box = tk.Frame(self, bg=config.BG_COLOR, relief=tk.RIDGE, bd=3)
        box.pack(padx=30, pady=30, fill="both", expand=True)

        tk.Label(box, text="Usuario:", bg=config.BG_COLOR, font=config.FONT).grid(
            row=0, column=0, sticky="e", padx=10, pady=10
        )
        self.user_entry = tk.Entry(box, font=config.FONT)
        self.user_entry.insert(0, config.DEMO_USER)
        self.user_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(box, text="Contraseña:", bg=config.BG_COLOR, font=config.FONT).grid(
            row=1, column=0, sticky="e", padx=10, pady=10
        )
        self.pass_entry = tk.Entry(box, font=config.FONT, show="*")
        self.pass_entry.grid(row=1, column=1, padx=10, pady=10)
        self.pass_entry.bind("<Return>", lambda _event: self._try_login())

        self.error_label = tk.Label(box, text="", fg="red", bg=config.BG_COLOR, font=config.FONT)
        self.error_label.grid(row=2, column=0, columnspan=2)

        login_btn = tk.Button(
            box, text="Entrar", font=config.FONT, width=12, relief=tk.RAISED, bd=2,
            command=self._try_login,
        )
        login_btn.grid(row=3, column=0, columnspan=2, pady=10)

        footer = tk.Label(
            self,
            text="© 1998 GestCorp Soluciones Empresariales",
            bg=config.BG_COLOR,
            font=(config.FONT_FAMILY, 8),
        )
        footer.pack(side="bottom", pady=6)

    def _try_login(self) -> None:
        user = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        if user == config.DEMO_USER and password == config.DEMO_PASS:
            self._on_success()
        else:
            self.error_label.config(text="Usuario o contraseña incorrectos")
