import os
import json
import random
from functools import partial
from tkinter import *
from tkinter.messagebox import *


CURR_DIR = os.path.dirname(os.path.realpath(__file__))


class Task:
    def __init__(self, id, level, done, name, desc):
        self.id = id
        self.level = level
        self.done = done
        self.name = name
        self.desc = desc


class Data:
    file = os.path.join(CURR_DIR, "data.json")

    @staticmethod
    def hide_done():
        with open(Data.file, 'r+', encoding='utf-8') as file:
            return json.load(file)["hide_done"]

    @staticmethod
    def done(id):
        data = {}
        
        with open(Data.file, 'r+', encoding='utf-8') as file:
            data = json.load(file)
        
        for task in data["todo"]:
            if task["id"] == id:
                task["done"] = not task["done"]

        with open(Data.file, 'w+', encoding='utf-8') as file:
            json.dump(data, file)

    @staticmethod
    def remove(id):
        data = {}
        
        with open(Data.file, 'r+', encoding='utf-8') as file:
            data = json.load(file)
        
        for t, task in enumerate(data["todo"]):
            if task["id"] == id:
                data["todo"].pop(t)

        with open(Data.file, 'w+', encoding='utf-8') as file:
            json.dump(data, file)

    @staticmethod
    def get_tasks():
        with open(Data.file, 'r+', encoding='utf-8') as file:
            tasks = []
            
            for task_dict in json.load(file)["todo"]:
                tasks.append( Task(
                    task_dict["id"],
                    task_dict["level"],
                    task_dict["done"],
                    task_dict["name"],
                    task_dict["desc"]
                ) )
            
            return tasks

    @staticmethod
    def add_task(level, name, desc):
        data = {}
        
        with open(Data.file, 'r+', encoding='utf-8') as file:
            data = json.load(file)
        
        random_id = 0
        valid_id = False
        while not valid_id:
            random_id = random.randrange(0, 999999)
            valid_id = True

            for task in data["todo"]:
                if task["id"] == random_id:
                    valid_id = False


        data["todo"].append({
            "id": random_id,
            "level": level,
            "done": False,
            "name": name,
            "desc": desc
        })

        with open(Data.file, 'w+', encoding='utf-8') as file:
            json.dump(data, file)


class shm:
    background      = "#282a36"
    current_line    = "#44475a"
    selection       = "#44475a"
    foreground      = "#f8f8f2"
    comment         = "#6272a4"
    aqua            = "#8be9fd"
    green           = "#50fa7b"
    orange          = "#ffb86c"
    blue            = "#ff79c6"
    purple          = "#bd93f9"
    red             = "#ff5555"
    yellow          = "#f1fa8c"


class DoneCallback:
    def __init__(self, id, refresh_func):
        self.id = id
        self.refresh_func = refresh_func

    def __call__(self):
        Data.done(self.id)
        self.refresh_func()


class App:
    def __init__(self):
        # WINDOW
        self.tk = Tk()

        # VARIABLES
        self.size = 360, 400
        self.gap = 22, 4
        
        # SETUP
        self.tk.title("TODO")
        self.tk.resizable(False, False)

        self.tk.geometry(
            f"{self.size[0]}x{self.size[1]}" +
            f"+{self.tk.winfo_screenwidth() - self.size[0] - self.gap[0]}" +
            f"+{20 + self.gap[1]}"
        )

        self.tk.attributes("-topmost", True)
        self.tk.config(bg=shm.background)

        # EVENT
        self.tk.bind_all("<FocusOut>", lambda _: self.tk.destroy())
        self.tk.bind_all("<Escape>", lambda _: self.tk.destroy())

        self.tk.bind_all("<a>", self.add_task_cmd)
        
        # WIDGETS
        self.title_l = Label(self.tk,
            text="Things TODO", font=("Ubuntu", 18),
            fg=shm.foreground, bg=shm.background)
        self.title_l.place(x=15, y=10)

        self.add_b = Button(self.tk,
            text="+", font=("Ubuntu", 18),
            relief='flat',
            activebackground=shm.selection,
            activeforeground=shm.foreground,
            fg=shm.foreground, bg=shm.background,
            bd=0, highlightthickness=0,
            command=self.add_task_cmd)
        self.add_b.place(x=self.size[0] - 50, y=10)

        self.main_f = Frame(self.tk, bg=shm.background)

        main_f_gaps = (55, 10, 52, 10)  # (55, 10, 10, 10)  # t, r, b, l
        self.main_f.place(
            x=main_f_gaps[3], y=main_f_gaps[0],
            width=self.size[0] - main_f_gaps[1] - main_f_gaps[3],
            height=self.size[1] - main_f_gaps[0] - main_f_gaps[2]
        )

        # New entry frame
        self.new_task_f = Frame(self.tk, bg=shm.yellow)
        self.new_task_f_height = 26
        self.new_task_f_gaps = (10, 10, 14, 10)  # t, r, b, l
        self.adding_new_task = False

        self.up_b = Button( self.new_task_f,
                    text="<", font=("Ubuntu", 10),
                    activebackground=shm.selection,
                    activeforeground=shm.foreground,
                    bd=0, highlightthickness=0,
                    fg=shm.foreground, bg=shm.current_line,
                    command=lambda: self.add_to_temp_lvl(1) )
        self.up_b.grid(row=0, column=0, sticky='w')

        self.temp_task_lvl = 1
        self.new_task_level_l = Label(self.new_task_f,
                    text="1", font=("Ubuntu Mono", 16),
                    fg=shm.foreground, bg=shm.current_line)
        self.new_task_level_l.grid(row=0, column=1, sticky='w')

        self.down_b = Button( self.new_task_f,
                    text=">", font=("Ubuntu", 10),
                    activebackground=shm.selection,
                    activeforeground=shm.foreground,
                    bd=0, highlightthickness=0,
                    fg=shm.foreground, bg=shm.current_line,
                    command=lambda: self.add_to_temp_lvl(-1) )
        self.down_b.grid(row=0, column=2, sticky='w')

        self.task_name_var = StringVar()
        self.task_name_e = Entry(
            self.new_task_f, font=("Ubuntu", 14),
            width=21, relief='flat',
            bd=1, highlightthickness=0,
            textvariable=self.task_name_var,
            fg=shm.foreground, bg=shm.current_line)
        self.task_name_e.grid(row=0, column=3, sticky='w')

        self.valid_task_b = Button( self.new_task_f,
                    text="^", font=("Ubuntu", 10),
                    activebackground=shm.selection,
                    activeforeground=shm.foreground,
                    bd=0, highlightthickness=0,
                    fg=shm.foreground, bg=shm.current_line,
                    command=self.finish_add_task )
        self.valid_task_b.grid(row=0, column=4, sticky='e')

        self.ids, self.dones, self.levels, self.names, self.desc = [], [], [], [], []

        self.done_i = PhotoImage(file=os.path.join(CURR_DIR, "res/done.png"))
        self.not_done_i = PhotoImage(file=os.path.join(CURR_DIR, "res/not_done.png"))

        # Navigate and delete tasks
        self.selected_task = 0
        # TODO: bind keys to navigate the task and delete them
        self.tk.bind_all("<Up>", lambda e: self.move_selected(-1))
        self.tk.bind_all("<Down>", lambda e: self.move_selected(1))
        self.tk.bind_all("<KP_Up>", lambda e: self.move_selected(-1))
        self.tk.bind_all("<KP_Down>", lambda e: self.move_selected(1))

        self.tk.bind_all("<Return>", self.done_curr_selected)
        self.tk.bind_all("<Delete>", self.del_curr_selected)

        self.refresh()
        # MAIN LOOP
        self.tk.mainloop()

    def done_curr_selected(self, evt=None):
        Data.done(self.ids[self.selected_task])
        self.refresh()

    def del_curr_selected(self, evt=None):
        self.tk.bind_all("<FocusOut>", lambda e: None)
        self.tk.bind_all("<Escape>", lambda e: None)

        confirmed = askyesno(title="Are you sure you want to delete this task ?", message="After deleting this task you will not be able to have it back, do you want to procced ?")

        if confirmed:
            Data.remove(self.ids[self.selected_task])
            self.refresh()
        
        self.tk.bind_all("<FocusOut>", lambda _: self.tk.destroy())
        self.tk.bind_all("<Escape>", lambda _: self.tk.destroy())

    def move_selected(self, amount):
        self.selected_task = max( min(self.selected_task + amount, len(self.dones) - 1), -1 )
        self.color_selected()

    def color_selected(self):
        if self.selected_task == -1:
            return
        
        if self.selected_task > len(self.dones) - 1:
            self.selected_task = len(self.dones) - 1

        for t, task in enumerate(self.dones):
            if t == self.selected_task:
                color = shm.current_line
            else:
                color = shm.background

            task.config(bg=color)
            self.levels[t].config(bg=color)
            self.names[t].config(bg=color)
            # self.desc[t].config(bg=color)


    def finish_add_task(self, evt=None):
        Data.add_task(self.temp_task_lvl, self.task_name_var.get(), "no-desc")

        self.end_task_adding()
        self.refresh()

    def add_to_temp_lvl(self, x):
        self.temp_task_lvl = min(9, max(1, x + self.temp_task_lvl))
        self.new_task_level_l.config(text=str(self.temp_task_lvl))

    def add_task_cmd(self, evt=None):
        if not self.adding_new_task:
            self.new_task_f.place(
                x=self.new_task_f_gaps[3],
                y=self.size[1] - self.new_task_f_height - self.new_task_f_gaps[2],
                width=self.size[0] - self.new_task_f_gaps[1] - self.new_task_f_gaps[3],
                height=self.new_task_f_height
            )

            self.task_name_e.focus_set()
            self.temp_task_lvl = 1
            self.new_task_level_l.config(text=str(self.temp_task_lvl))

            self.adding_new_task = True
            self.tk.bind_all("<FocusOut>", lambda e: None)
            self.tk.bind_all("<Escape>", self.end_task_adding)

            self.tk.bind_all("<Return>", self.finish_add_task)
            self.tk.bind_all("<Delete>", lambda e: None)
            self.tk.bind_all("<a>", lambda e: None)

            self.tk.bind_all("<Up>", lambda e: self.add_to_temp_lvl(1))
            self.tk.bind_all("<Down>", lambda e: self.add_to_temp_lvl(-1))
            self.tk.bind_all("<KP_Up>", lambda e: self.add_to_temp_lvl(1))
            self.tk.bind_all("<KP_Down>", lambda e: self.add_to_temp_lvl(-1))
            
            self.task_name_var.set("")
            self.temp_task_lvl = 1

    def end_task_adding(self, evt=None):
        if self.adding_new_task:
            self.adding_new_task = False
            self.tk.bind_all("<FocusOut>", lambda _: self.tk.destroy())
            self.tk.bind_all("<Escape>", lambda _: self.tk.destroy())

            self.tk.bind_all("<Return>", self.done_curr_selected)
            self.tk.bind_all("<Delete>", self.del_curr_selected)
            self.tk.bind_all("<a>", self.add_task_cmd)

            self.tk.bind_all("<Up>", lambda e: self.move_selected(-1))
            self.tk.bind_all("<Down>", lambda e: self.move_selected(1))
            self.tk.bind_all("<KP_Up>", lambda e: self.move_selected(-1))
            self.tk.bind_all("<KP_Down>", lambda e: self.move_selected(1))

            self.new_task_f.place_forget()

    def refresh(self):
        for wdg in self.dones:
            wdg.grid_remove()
        for wdg in self.levels:
            wdg.grid_remove()
        for wdg in self.names:
            wdg.grid_remove()
        for wdg in self.desc:
            wdg.grid_remove()

        self.ids, self.dones, self.levels, self.names, self.desc = [], [], [], [], []

        # Generate all tasks
        tasks = sorted(Data.get_tasks(), key=lambda x: x.level, reverse=True)
        hide_done = Data().hide_done()

        for id, task in enumerate(tasks):
            if not (hide_done and task.done):
                self.ids.append(task.id)

                # generate the level of the task
                self.dones.append( Button( self.main_f,
                    image=self.done_i if task.done else self.not_done_i, font=("Ubuntu Mono", 11),
                    width=24, height=24,
                    activebackground=shm.selection,
                    activeforeground=shm.foreground,
                    bd=0, highlightthickness=0,
                    fg=shm.foreground, bg=shm.background,
                    command=DoneCallback(task.id, self.refresh) ))
                self.dones[-1].grid(row=id, column=0, padx=0, pady=2, sticky='e')

                self.levels.append( Label( self.main_f,
                    text=str(task.level), font=("Ubuntu Mono", 16),
                    fg=shm.foreground, bg=shm.background) )
                self.levels[-1].grid(row=id, column=1, padx=8, pady=2, sticky='e')

                self.names.append( Label(self.main_f,
                    text=task.name, font=("Ubuntu", 14),
                    fg=shm.foreground, bg=shm.background) )
                self.names[-1].grid(row=id, column=2, padx=0, pady=2, sticky='w')

                # self.desc.append( Label(self.main_f,
                #     text=task.desc, font=("Ubuntu", 14),
                #     fg=shm.foreground, bg=shm.red) )
                # self.desc[-1].grid(row=id, column=3, padx=8, pady=2, sticky='w')

        self.color_selected()


if __name__ == '__main__':
    App()
    # Data.add_task(1, "try polybar", "no-desk")
