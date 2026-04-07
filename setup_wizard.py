import tkinter as tk
from tkinter import messagebox
import os

def run_wizard():
    if os.path.exists("config.py"):
        return

    root = tk.Tk()
    root.title("Настройка Оптика-Бот v2.5")
    root.geometry("400x350")

    tk.Label(root, text="Настройка нового салона", font=("Arial", 14, "bold")).pack(pady=10)
    
    tk.Label(root, text="Введите токен ВК (Группы или Аккаунта):").pack()
    token_entry = tk.Entry(root, width=40)
    token_entry.pack(pady=5)

    tk.Label(root, text="Ваш цифровой ID ВК (для прав админа):").pack()
    admin_entry = tk.Entry(root, width=40)
    admin_entry.pack(pady=5)

    tk.Label(root, text="Название салона:").pack()
    name_entry = tk.Entry(root, width=40)
    name_entry.insert(0, "Оптика Экспресс")
    name_entry.pack(pady=5)

    def save():
        token = token_entry.get()
        admin_id = admin_entry.get()
        s_name = name_entry.get()
        
        if not token or not admin_id:
            messagebox.showerror("Ошибка", "Заполните токен и ID!")
            return

        with open("config.py", "w", encoding="utf-8") as f:
            f.write(f'TOKEN = "{token}"\n')
            f.write(f'ADMIN_ID = {admin_id}\n')
            f.write(f'SALON_NAME = "{s_name}"\n')
        
        messagebox.showinfo("Успех", "Настройки сохранены! Перезапустите бота.")
        root.destroy()
        exit()

    tk.Button(root, text="Завершить установку", command=save, bg="green", fg="white").pack(pady=20)
    root.mainloop()
