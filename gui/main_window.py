import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from core.engine import AetherEngine

class AetherHideGUI(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkDnDVersion = TkinterDnD._require(self)
        self.engine = AetherEngine()
        self.selected_file = None
        self.extract_file_path = None
        
        # Window Setup
        self.title("AetherHide v1.0 | Professional Steganography")
        self.geometry("750x620")
        ctk.set_appearance_mode("dark")
        
        self.grid_columnconfigure(0, weight=1)
        
        # Header UI
        self.header = ctk.CTkLabel(self, text="AETHER HIDE", font=("Consolas", 32, "bold"), text_color="#1f6aa5")
        self.header.grid(row=0, column=0, pady=(30, 5))
        self.sub_header = ctk.CTkLabel(self, text="ADVANCED EOF DATA OBFUSCATOR", font=("Consolas", 11), text_color="gray")
        self.sub_header.grid(row=1, column=0, pady=(0, 20))

        # Tabs
        self.tabview = ctk.CTkTabview(self, width=650, height=420)
        self.tabview.grid(row=2, column=0, padx=20, pady=10)
        self.tabview.add("INJECT")
        self.tabview.add("EXTRACT")

        self._setup_inject_tab()
        self._setup_extract_tab()

    def _setup_inject_tab(self):
        tab = self.tabview.tab("INJECT")
        
        # Drop Zone Frame
        self.drop_frame = ctk.CTkFrame(tab, width=550, height=100, border_width=2)
        self.drop_frame.pack(pady=20, padx=20)
        self.drop_frame.pack_propagate(False)
        
        self.file_label = ctk.CTkLabel(self.drop_frame, text="DRAG & DROP FILE HERE\nOR CLICK TO BROWSE", font=("Segoe UI", 12))
        self.file_label.pack(expand=True)
        
        # Events for Drag & Drop
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_frame.bind("<Button-1>", lambda e: self.select_file())
        self.file_label.bind("<Button-1>", lambda e: self.select_file())

        self.msg_box = ctk.CTkTextbox(tab, width=550, height=100, border_width=1)
        self.msg_box.insert("0.0", "Enter your secret message here...")
        self.msg_box.pack(pady=10)

        self.pass_inject = ctk.CTkEntry(tab, placeholder_text="Encryption Password", show="*", width=550, height=40)
        self.pass_inject.pack(pady=10)

        self.btn_run = ctk.CTkButton(tab, text="PROTECT & SAVE", font=("Segoe UI", 14, "bold"), 
                                     width=250, height=45, command=self.run_injection)
        self.btn_run.pack(pady=20)

    def _setup_extract_tab(self):
        tab = self.tabview.tab("EXTRACT")
        
        self.btn_select_ext = ctk.CTkButton(tab, text="SELECT SECURED FILE", fg_color="#333333", 
                                            width=550, height=50, command=self.select_file_extract)
        self.btn_select_ext.pack(pady=25)

        self.pass_extract = ctk.CTkEntry(tab, placeholder_text="Security Password", show="*", width=550, height=40)
        self.pass_extract.pack(pady=10)

        self.btn_recover = ctk.CTkButton(tab, text="EXTRACT MESSAGE", font=("Segoe UI", 14, "bold"), 
                                         width=250, height=45, command=self.run_extraction)
        self.btn_recover.pack(pady=15)

        self.result_box = ctk.CTkTextbox(tab, width=550, height=100, border_width=1)
        self.result_box.pack(pady=10)

    # UI Logic Methods
    def handle_drop(self, event):
        path = event.data.strip('{}')
        self.selected_file = path
        self.file_label.configure(text=f"SELECTED: {os.path.basename(path)}", text_color="#1f6aa5")

    def select_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.selected_file = path
            self.file_label.configure(text=f"SELECTED: {os.path.basename(path)}", text_color="#1f6aa5")

    def select_file_extract(self):
        path = filedialog.askopenfilename()
        if path:
            self.extract_file_path = path
            self.btn_select_ext.configure(text=f"FILE: {os.path.basename(path)}")

    def run_injection(self):
        try:
            msg = self.msg_box.get("1.0", "end-1c")
            pwd = self.pass_inject.get()
            if not self.selected_file or pwd == "":
                raise ValueError("Incomplete data: File and Password required.")
            
            output = self.engine.protect_file(self.selected_file, msg, pwd)
            messagebox.showinfo("Success", f"Protected file saved at:\n{output}")
        except Exception as e:
            messagebox.showerror("Injection Error", str(e))

    def run_extraction(self):
        try:
            pwd = self.pass_extract.get()
            if not self.extract_file_path:
                raise ValueError("Please select a file first.")
                
            result = self.engine.recover_data(self.extract_file_path, pwd)
            self.result_box.delete("1.0", "end")
            self.result_box.insert("1.0", result)
            messagebox.showinfo("Success", "Decryption Successful!")
        except Exception as e:
            messagebox.showerror("Recovery Error", str(e))