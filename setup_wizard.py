import tkinter as tk
from tkinter import messagebox
import os, sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def run_wizard():
    config_file = os.path.join(get_base_path(), "config.py")
    if os.path.exists(config_file):
        return

    root = tk.Tk()
    root.title("Настройка Оптика-Бот")
    root.geometry("400x350")

    tk.Label(root, text="Первоначальная настройка", font=("Arial", 12, "bold")).pack(pady=10)
    
    tk.Label(root, text="Токен ВК:").pack()
    token_entry = tk.Entry(root, width=40)
    token_entry.pack(pady=5)

    tk.Label(root, text="Ваш цифровой ID ВК (админ):").pack()
    admin_entry = tk.Entry(root, width=40)
    admin_entry.pack(pady=5)

    tk.Label(root, text="Название салона:").pack()
    name_entry = tk.Entry(root, width=40)
    name_entry.insert(0, "Оптика")
    name_entry.pack(pady=5)

    def save():
        token = token_entry.get()
        admin_id = admin_entry.get()
        s_name = name_entry.get()
        if not token or not admin_id:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(f'TOKEN = "{token}"\n')
            f.write(f'ADMIN_ID = {admin_id}\n')
            f.write(f'SALON_NAME = "{s_name}"\n')
        messagebox.showinfo("Успех", "Настройки сохранены! Перезапустите бота.")
        root.destroy()
        sys.exit()

    tk.Button(root, text="Сохранить и выйти", command=save, bg="green", fg="white").pack(pady=20)
    root.mainloop()