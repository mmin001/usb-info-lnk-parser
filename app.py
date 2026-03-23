import tkinter as tk
import function as fc
from tkinter import ttk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("USB & LNK Analyzer")
        self.geometry("1000x600")
        
        self.rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.top_frame = tk.Frame(self)
        self.top_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.scan_btn = tk.Button(self.top_frame, text="스캔 시작", command=self.insert_data)
        self.scan_btn.pack(side="left", padx=10, pady=5)
        
        self.status_label = tk.Label(self.top_frame)
        self.status_label.pack(side="left", padx=10, pady=5)
        
#usbstor
        self.usb_frame = tk.Frame(self, relief="sunken", bd=2)
        self.usb_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        tk.Label(self.usb_frame, text="USB 연결 기록").pack(anchor="w")

        # 열이름 정의
        usb_cols = ("vendor", "product", "version", "friendly name", "serial", "first install", "last connected", "last removed")
        
        self.usb_tree = ttk.Treeview(self.usb_frame, columns=usb_cols, show="headings")
        
        for col in usb_cols:
            self.usb_tree.heading(col, text=col)
            self.usb_tree.column(col, width=100, anchor="w") 

        self.usb_scroll_y = tk.Scrollbar(self.usb_frame, orient="vertical", command=self.usb_tree.yview)
        self.usb_scroll_x = tk.Scrollbar(self.usb_frame, orient="horizontal", command=self.usb_tree.xview)
        self.usb_tree.configure(yscrollcommand=self.usb_scroll_y.set, xscrollcommand=self.usb_scroll_x.set)

        self.usb_scroll_y.pack(side="right", fill="y")
        self.usb_scroll_x.pack(side="bottom", fill="x")
        self.usb_tree.pack(side="left", fill="both", expand=True)

    #LNK 기록
        self.lnk_frame = tk.Frame(self, relief="sunken", bd=2)
        self.lnk_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        tk.Label(self.lnk_frame, text="최근 파일 접근 흔적 (LNK)").pack(anchor="w")

        lnk_cols = ("user name", "file name", "time", "file path")
        self.lnk_tree = ttk.Treeview(self.lnk_frame, columns=lnk_cols, show="headings")
        
        for col in lnk_cols:
            self.lnk_tree.heading(col, text=col)
            self.lnk_tree.column(col, width=120, anchor="w")

        self.lnk_scroll_y = tk.Scrollbar(self.lnk_frame, orient="vertical", command=self.lnk_tree.yview)
        self.lnk_scroll_x = tk.Scrollbar(self.lnk_frame, orient="horizontal", command=self.lnk_tree.xview)
        self.lnk_tree.configure(yscrollcommand=self.lnk_scroll_y.set, xscrollcommand=self.lnk_scroll_x.set)

        self.lnk_scroll_y.pack(side="right", fill="y")
        self.lnk_scroll_x.pack(side="bottom", fill="x")
        self.lnk_tree.pack(side="left", fill="both", expand=True)

    def insert_data(self):
        self.status_label.config(text="로딩 중")
        self.update()
        for i in self.usb_tree.get_children(): self.usb_tree.delete(i)
        for i in self.lnk_tree.get_children(): self.lnk_tree.delete(i)

        log_path = fc.LOG_PATH
        with open(log_path, "w", encoding="utf-8") as f:
            usb_result = fc.usbstor(f) 
            
        lnk_result = fc.lnk_parser()

        for item in usb_result:
            values = (
                item.get("vendor", ""),
                item.get("name", ""), 
                item.get("version", ""), 
                item.get("friendlyname", ""), 
                item.get("serial", ""), 
                item.get("first_install", ""),
                item.get("last_connect", ""), 
                item.get("last_removed", "")   
            )
            self.usb_tree.insert("", tk.END, values=values)

        for item in lnk_result:
            values = (
                item.get("user", ""),
                item.get("name", ""),  
                item.get("time", ""), 
                item.get("path", "") 
            )
            self.lnk_tree.insert("", tk.END, values=values)

        self.status_label.config(text="스캔 완료")

if __name__ == "__main__":
    app = App()
    app.mainloop()
