import tkinter as tk
from tkinter import ttk, filedialog
import requests
import csv
from urllib.parse import urlparse
import threading
import pandas as pd

class URLStatusChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Status Checker")

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create and configure text area for URLs
        self.url_label = ttk.Label(self.main_frame, text="Enter URLs (one per line):")
        self.url_label.grid(row=0, column=0, sticky=tk.W, pady=(0,5))

        self.url_text = tk.Text(self.main_frame, height=10, width=50)
        self.url_text.grid(row=1, column=0, columnspan=2, pady=(0,10))

        # Create check button
        self.check_button = ttk.Button(self.main_frame, text="Check Status", command=self.check_urls)
        self.check_button.grid(row=2, column=0, sticky=tk.W, pady=(0,10))

        # Create export button
        self.export_button = ttk.Button(self.main_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_button.grid(row=2, column=1, sticky=tk.E, pady=(0,10))
        self.export_button.state(['disabled'])

        # Create treeview for results
        self.tree = ttk.Treeview(self.main_frame, columns=('URL', 'Status'), show='headings')
        self.tree.heading('URL', text='URL')
        self.tree.heading('Status', text='Status')
        self.tree.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add scrollbar to treeview
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.results = []

    def check_url_status(self, url):
        try:
            response = requests.get(url.strip(), timeout=5)
            return response.status_code
        except requests.RequestException:
            return "Error"

    def check_urls(self):
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.results = []

        # Get URLs from text area
        urls = self.url_text.get("1.0", tk.END).splitlines()
        urls = [url.strip() for url in urls if url.strip()]

        self.check_button.state(['disabled'])

        def process_urls():
            for url in urls:
                status = self.check_url_status(url)
                self.results.append((url, status))
                self.tree.insert('', tk.END, values=(url, status))

            self.check_button.state(['!disabled'])
            self.export_button.state(['!disabled'])

        # Run URL checking in a separate thread
        thread = threading.Thread(target=process_urls)
        thread.start()

    def export_to_csv(self):
        if not self.results:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            df = pd.DataFrame(self.results, columns=['URL', 'Status'])
            df.to_csv(file_path, index=False)

def main():
    root = tk.Tk()
    app = URLStatusChecker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
