import csv
from tkinter import *
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
from resume_parser import resumeParser

def write_list_to_csv(data_list, filename):
    with open(filename, 'a+', newline='', errors='ignore') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data_list)

def prerec(old):
    file_types = (("PDF files", "*.pdf"), ("All files","*.*"))
    file_path = filedialog.askopenfilenames(filetypes=file_types)
    old.destroy()

    window = tk.Tk()
    table = ttk.Treeview(window)

    # Define the table columns
    table["columns"] = ("File_Name", "Name", "EMail ID", "Mobile Number", "Skills")

    # Format the columns
    table.column("#0", width=0, stretch=tk.NO)
    table.column("File_Name", width=200)
    table.column("Name", width=200)
    table.column("EMail ID", width=250)
    table.column("Mobile Number", width=100)
    table.column("Skills", width=400)

    # Create the table headings
    table.heading("File_Name", text="File_Name")
    table.heading("Name", text="Name")
    table.heading("EMail ID", text="EMail ID")
    table.heading("Mobile Number", text="Mobile Number")
    table.heading("Skills", text="Skills")
        
    for file in file_path:
        # FILES = [[]]
        object = resumeParser()
        X = object.read_file(file)
        # FILES[0].append([str(file.split('/')[-1])])
        # FILES[0].append(X['name'])
        # FILES[0].append(X['email'])
        # FILES[0].append(X['phone'])
        # FILES[0].append(X['skills'])
        # FILES[0].append(["======", "======","======", "======", "======","======","======","======","======","======","======"])
        table.insert("", tk.END, text="1", values=(file.split('/')[-1], X['name'], X['email'], X['phone'], X['skills']))
        # write_list_to_csv(FILES[0], 'FILES_1.csv')

    table.configure(height=16)
    table.pack()
    window.mainloop()
    main()
 
def main():
    message_box = Tk()
    message_box.geometry("500x500")
    message_box.title("Resume Information Extractor")

    button_frame = Frame(message_box)
    yes_button = Button(button_frame, text="Upload Resume", command=lambda:prerec(message_box))
    yes_button.pack(side=LEFT, padx=10, pady=10)
    button_frame.pack()
    message_box.mainloop()

if __name__ == "__main__":
    main()