import tkinter as tk

from gestcorp98 import config, database, seed_data
from gestcorp98.ui.login_window import LoginFrame
from gestcorp98.ui.main_window import MainWindow


def main() -> None:
    conn = database.get_connection()
    database.init_db(conn)
    seed_data.seed_if_empty(conn)

    root = tk.Tk()
    root.title(config.APP_TITLE)
    root.configure(bg=config.BG_COLOR)
    root.state("zoomed")

    def on_login_success() -> None:
        for widget in root.winfo_children():
            widget.destroy()
        MainWindow(root, conn).pack(fill="both", expand=True)

    LoginFrame(root, on_success=on_login_success).pack(fill="both", expand=True)
    root.mainloop()
    conn.close()


if __name__ == "__main__":
    main()
