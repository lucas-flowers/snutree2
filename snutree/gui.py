import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkf
from pathlib import Path
from . import snutree

class SnutreeGUI(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):

        super().__init__(parent, *args, **kwargs)

        self.root = parent

        self.member_module = None
        self.path_entries = {}

        self.init_gui()

    def init_gui(self):

        self.path_input('Input', 'input_path', row=0, column=0)
        self.path_input('Output', 'output_path', row=1, column=0, save=True)
        self.path_input('Configuration', 'config_path', row=2, column=0)
        self.member_module_select()
        self.execute_button()


    def path_input(self, name, cli_name, row=0, column=0, save=False):

        label = tk.StringVar()
        label.set(name)
        label_container = tk.Label(self.root, textvariable=label)
        label_container.grid(row=row, column=column)

        entry = ttk.Entry(self.root)
        entry['width'] = 60
        entry.grid(row=row, column=column+1)
        self.path_entries[cli_name] = entry

        def command():
            filename = tkf.asksaveasfilename() if save else tkf.askopenfilename()
            self.path_entries[cli_name].delete(0, tk.END)
            self.path_entries[cli_name].insert(0, filename)

        button = ttk.Button(self.root, text='Browse...', command=command)
        button.grid(row=row, column=column+2)

    def member_module_select(self):

        default = tk.StringVar()
        default.set('basic')
        menu = ttk.OptionMenu(self.root, default,
                'basic', 'keyed', 'sigmanu', 'chapter',
                command=self.member_module_validate)
        menu.grid(row=3, column=0)

    def member_module_validate(self, value):
        self.member_module = snutree.get_member_format(value)

    def execute_button(self):

        button = ttk.Button(self.root, text='Execute', command=self.execute)
        button.grid(row=4, column=0)

    def execute(self):

        input_file = Path(self.path_entries['input_path'].get()).open()
        output_path = self.path_entries['output_path'].get()
        config_path = self.path_entries['config_path'].get()

        snutree.generate(
                [input_file],
                output_path,
                None,
                [config_path],
                0,
                False,
                False,
                True,
                self.member_module,
                None,
                )

def main():

    root = tk.Tk()
    root.style = tk.ttk.Style()
    root.style.theme_use('clam')
    SnutreeGUI(root)
    root.mainloop()

