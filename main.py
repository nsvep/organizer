import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
import json
from ttkthemes import ThemedStyle

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizer")
        self.style = ThemedStyle(self.root)
        self.style.set_theme("arc")

        self.tasks = self.load_tasks()
        self.create_widgets()
        self.refresh_task_list()

    def create_widgets(self):
        tk.Label(self.root, text="Название задачи:", font=("Arial", 12)).pack()
        self.entry_task_name = tk.Entry(self.root, font=("Arial", 12))
        self.entry_task_name.pack()

        tk.Label(self.root, text="Дедлайн:", font=("Arial", 12)).pack()
        self.cal = Calendar(self.root, selectmode='day', date_pattern='dd/MM/yyyy', font=("Arial", 12))
        self.cal.pack()

        tk.Label(self.root, text="Приоритет:", font=("Arial", 12)).pack()
        self.combo = ttk.Combobox(self.root, values=["Низкий", "Средний", "Высокий"], font=("Arial", 12))
        self.combo.pack()

        tk.Button(self.root, text="Добавить задачу", command=self.add_task, font=("Arial", 12)).pack()

        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        scroll = ttk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")

        self.task_list = tk.Listbox(frame, width=50, height=15, font=("Arial", 12), yscrollcommand=scroll.set)
        self.task_list.pack(side="left", fill="both")
        scroll.config(command=self.task_list.yview)

        tk.Button(self.root, text="Отметить как выполненное", command=self.mark_as_completed, font=("Arial", 12)).pack()
        tk.Button(self.root, text="Удалить выполненные задачи", command=self.delete_completed, font=("Arial", 12)).pack()
        tk.Button(self.root, text="Редактировать задачу", command=self.edit_task, font=("Arial", 12)).pack()

    def save_tasks(self):
        with open('tasks.json', 'w') as f:
            json.dump(self.tasks, f, indent=4, default=str)

    def load_tasks(self):
        # Путь к файлу задач.
        tasks_file = 'tasks.json'
        try:
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
            return tasks
        except FileNotFoundError:
            # Если файл не найден, вернуть пустой список
            return []
        except json.JSONDecodeError:
            messagebox.showerror('Ошибка', 'Ошибка чтения файла задач. Файл с задачами повреждён.')
            return []

    def refresh_task_list(self):
        self.task_list.delete(0, tk.END)
        for task in self.tasks:
            status = '✓' if task['completed'] else ' '
            self.task_list.insert(tk.END,
                                  f"{status} {task['name']} - Дедлайн: {task['deadline']} Приоритет: {task['priority']}")

    def add_task(self):
        name = self.entry_task_name.get()
        deadline_str = self.cal.get_date()
        try:
            deadline = datetime.strptime(deadline_str, '%d/%m/%Y').strftime('%d.%m.%Y')
        except ValueError as e:
            messagebox.showerror('Неверный формат даты', 'Неверный формат даты, должен быть dd/mm/yyyy')
            return
        priority = self.combo.get()
        if name and deadline and priority:
            self.tasks.append({"name": name, "deadline": deadline, "priority": priority, "completed": False})
            self.refresh_task_list()
            self.save_tasks()
        else:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")

    def mark_as_completed(self):
        selected = self.task_list.curselection()
        if selected:
            self.tasks[selected[0]]["completed"] = True
            self.refresh_task_list()
            self.save_tasks()

    def delete_completed(self):
        self.tasks = [task for task in self.tasks if not task["completed"]]
        self.refresh_task_list()
        self.save_tasks()

    def edit_task(self):
        selected = self.task_list.curselection()
        if selected:
            self.selected_task_index = selected[0]
            task = self.tasks[self.selected_task_index]

            self.edit_window = tk.Toplevel(self.root)
            self.edit_window.title("Редактировать задачу")

            label_task_name = tk.Label(self.edit_window, text="Название задачи:")
            label_task_name.pack()
            self.entry_task_name_edit = tk.Entry(self.edit_window)
            self.entry_task_name_edit.insert(tk.END, task["name"])
            self.entry_task_name_edit.pack()

            label_deadline = tk.Label(self.edit_window, text="Дедлайн:")
            label_deadline.pack()

            self.cal_edit = Calendar(self.edit_window, selectmode='day',
                                     year=int(task["deadline"][6:10]),
                                     month=int(task["deadline"][3:5]),
                                     day=int(task["deadline"][0:2]), date_pattern='dd/MM/yyyy')
            self.cal_edit.pack()

            label_priority = tk.Label(self.edit_window, text="Приоритет:")
            label_priority.pack()
            self.combo_edit = ttk.Combobox(self.edit_window, values=["Низкий", "Средний", "Высокий"])
            self.combo_edit.set(task["priority"])
            self.combo_edit.pack()

            btn_save_changes = tk.Button(self.edit_window, text="Сохранить изменения", command=self.save_changes)
            btn_save_changes.pack()

        else:
            messagebox.showerror("Ошибка", "Выберите задачу для редактирования")

    def save_changes(self):
        selected = self.task_list.curselection()
        if selected and self.selected_task_index is not None:
            updated_task = {
                "name": self.entry_task_name_edit.get(),
                "deadline": self.cal_edit.get_date(),
                "priority": self.combo_edit.get(),
                "completed": self.tasks[self.selected_task_index]['completed']
            }

            self.tasks[self.selected_task_index] = updated_task
            self.refresh_task_list()
            self.save_tasks()
            self.edit_window.destroy()
        else:
            messagebox.showerror("Ошибка", "Ошибка при попытке сохранить изменения задачи.")

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы хотите выйти и сохранить изменения?"):
            self.save_tasks()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    task_manager = TaskManager(root)
    root.protocol("WM_DELETE_WINDOW", task_manager.on_closing)
    root.mainloop()