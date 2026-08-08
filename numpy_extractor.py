import soundfile, threading
from tkinter import *
from tkinter import filedialog, ttk

class Window(Tk):
    def __init__(self, screenName = None, baseName = None, className = "Tk", useTk = True, sync = False, use = None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.title("Sound File Extractor")
        self.geometry("600x400")
        self.minsize(600, 400)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        # self.grid_rowconfigure(4, weight=1)

        self._file = None

        self.running = False
        self.thread_event = threading.Event()

        self.ask_filename_button = Button(self, text="Open File", command=self.open_file)
        self.ask_filename_button.grid(row=0, column=0, sticky="ew", padx=(5, 2.5), pady=5)

        self.reset_button = Button(self, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=1, sticky="ew", padx=(2.5, 5), pady=5)

        self.frame1 = Frame(self)
        self.frame1.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.frame1.grid_columnconfigure(0, weight=1)
        self.frame1.grid_rowconfigure(0, weight=1)

        self.text_box = Text(self.frame1, wrap="word")
        self.text_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.scrollbar = Scrollbar(self.frame1, orient="vertical")
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=5, pady=5)

        self.text_box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_box.yview)

        self.sample_rate_label = Label(self, text="Data: Null | Sample Rate: Null")
        self.sample_rate_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.frame2 = Frame(self)
        self.frame2.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.frame2.grid_columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(self.frame2)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.generate_button = Button(self.frame2, text="Generate More", command=lambda: threading.Thread(target=self.generate, daemon=True).start())
        self.generate_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    def open_file(self):
        self._file = filedialog.askopenfilename(title="Open Audio File", filetypes=[
                ("Audio Files", "*.wav *.mp3 *.ogg"),
                ("All Files", "*.*")])

        if not self._file:
            return
        
        data, sample_rate = soundfile.read(self._file)
        self.reset()
        self.text_box.insert(END, f"File: {self._file}\n Array: {data}")
        self.sample_rate_label.config(text=f"Data: {len(data):,} | Sample Rate: {sample_rate:,}")
        self.generate_button.config(state="normal")

    def reset(self):
        def _uiReset():
                    self.text_box.delete("0.0", END)
                    self.sample_rate_label.config(text="Data: Null | Sample Rate: Null")
                    self.generate_button.config(state="disabled")
        if self.running:
            self.thread_event.set()
            self.running = False
            self.after(100, _uiReset)
        else:
            _uiReset()

    def generate(self):
        if not self._file:
            return
        
        self.generate_button.config(state="disabled")
     
        data, sample_rate = soundfile.read(self._file)
        self.reset()
        self.running = True
        self.text_box.insert(END, f"File: {self._file}")
        for progress, i in enumerate(data):
            if not self.running:
                break
            self.text_box.insert(END, f"\n{i}")
            self.sample_rate_label.config(text=f"Data: {progress:,}/{len(data):,} | Sample Rate: {sample_rate:,}")
            self.progress_bar.config(value=(progress/len(data))*100)
            self.after(100, lambda: self.text_box.see(END))

        self.generate_button.config(state="normal")

window = Window()
window.mainloop()
    