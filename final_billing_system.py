# final_billing_system.py
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import random, os, re, webbrowser
from datetime import datetime
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ----------------- Helpers -----------------
def sanitize_filename(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[\\/*?<>:|\"']", "", s)         
    s = re.sub(r"\s+", "_", s)                 
    return s[:120] if len(s) > 120 else s

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# ----------------- App -----------------
root = tk.Tk()
root.title("Billing — Customer & Purchase")
root.geometry("1120x720")
root.resizable(False, False)

# ----------------- State variables -----------------
bill_no_var = tk.StringVar(value=str(random.randint(1000, 9999)))
bill_type_var = tk.StringVar(value="Customer")  
party_name_var = tk.StringVar()
phone_var = tk.StringVar()
item_var = tk.StringVar()
rate_var = tk.StringVar()
qty_var = tk.IntVar(value=1)
items = []  

# Default save folder
save_folder = os.path.join(os.getcwd(), "Bills")
ensure_folder(save_folder)

# ----------------- Fruits list -----------------
FRUITS = [
    "Mango","Banana","Apple","Orange","Grapes","Papaya","Watermelon","Guava","Pineapple",
    "Pomegranate","Litchi","Sapota","Custard Apple","Strawberry","Blueberry",
    "Muskmelon","Coconut","Dragon Fruit","Kiwi","Fig","Pear","Peach","Plum","Cherry",
    "Apricot","Jackfruit","Jujube","Starfruit"
]

# ----------------- UI Layout -----------------
header = Label(root, text="Billing System — Customer & Purchase", bg="#1f6f8b", fg="white",
               font=("Helvetica", 18, "bold"))
header.pack(fill=X)

top_frame = Frame(root, pady=8, padx=10)
top_frame.pack(fill=X)

Label(top_frame, text="Bill No:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky=W, padx=6)
Entry(top_frame, textvariable=bill_no_var, state="readonly", width=12, font=("Arial", 11)).grid(row=0, column=1, padx=6)

Label(top_frame, text="Bill Type:", font=("Arial", 11, "bold")).grid(row=0, column=2, sticky=W, padx=6)
bill_type_cb = ttk.Combobox(top_frame, textvariable=bill_type_var, values=["Customer", "Purchase"], state="readonly", width=14)
bill_type_cb.grid(row=0, column=3, padx=6)

party_label = Label(top_frame, text="Customer Name:", font=("Arial", 11, "bold"))
party_label.grid(row=0, column=4, sticky=W, padx=6)
Entry(top_frame, textvariable=party_name_var, width=30, font=("Arial", 11)).grid(row=0, column=5, padx=6)

Label(top_frame, text="Phone (optional):", font=("Arial", 11, "bold")).grid(row=0, column=6, sticky=W, padx=6)
Entry(top_frame, textvariable=phone_var, width=18, font=("Arial", 11)).grid(row=0, column=7, padx=6)

def on_bill_type_change(event=None):
    if bill_type_var.get() == "Customer":
        party_label.config(text="Customer Name:")
    else:
        party_label.config(text="Supplier Name:")

bill_type_cb.bind("<<ComboboxSelected>>", on_bill_type_change)

# ----------------- Product Frame -----------------
prod_frame = LabelFrame(root, text="Add Item", padx=10, pady=10, font=("Arial", 12, "bold"))
prod_frame.place(x=10, y=90, width=520, height=260)

Label(prod_frame, text="Item (select):", font=("Arial", 11)).grid(row=0, column=0, sticky=W, padx=6, pady=6)
item_cb = ttk.Combobox(prod_frame, textvariable=item_var, values=FRUITS, width=36)
item_cb.grid(row=0, column=1, padx=6, pady=6)

def filter_fruits(event=None):
    typed = item_var.get().lower()
    filtered = [f for f in FRUITS if f.lower().startswith(typed)]
    item_cb['values'] = filtered

item_cb.bind("<KeyRelease>", filter_fruits)

Label(prod_frame, text="Rate (per unit):", font=("Arial", 11)).grid(row=1, column=0, sticky=W, padx=6, pady=6)
Entry(prod_frame, textvariable=rate_var, width=38, font=("Arial", 11)).grid(row=1, column=1, padx=6, pady=6)

Label(prod_frame, text="Quantity:", font=("Arial", 11)).grid(row=2, column=0, sticky=W, padx=6, pady=6)
Entry(prod_frame, textvariable=qty_var, width=20, font=("Arial", 11)).grid(row=2, column=1, sticky=W, padx=6, pady=6)

def add_item():
    name = item_var.get().strip()
    if not name:
        messagebox.showerror("Error", "Select or type an item name.")
        return
    try:
        rate = float(rate_var.get())
    except:
        messagebox.showerror("Error", "Enter a valid numeric rate.")
        return
    try:
        qty = int(qty_var.get())
    except:
        messagebox.showerror("Error", "Enter a valid integer quantity.")
        return
    if qty <= 0 or rate <= 0:
        messagebox.showerror("Error", "Rate & Quantity must be positive.")
        return
    amount = rate * qty
    items.append((name, qty, rate, amount))
    refresh_preview()
    item_var.set("")
    rate_var.set("")
    qty_var.set(1)

Button(prod_frame, text="Add Item", command=add_item, bg="#2b7a78", fg="white", width=16).grid(row=3, column=1, sticky=E, padx=6, pady=8)
Button(prod_frame, text="Remove Last", command=lambda: (items.pop() if items else None, refresh_preview()), bg="#c44536", fg="white", width=12).grid(row=3, column=0, padx=6, pady=8)

# ----------------- Bill Preview -----------------
preview_frame = LabelFrame(root, text="Bill Preview", padx=6, pady=6, font=("Arial", 12, "bold"))
preview_frame.place(x=540, y=90, width=560, height=520)

scrollbar = Scrollbar(preview_frame, orient=VERTICAL)
text_preview = Text(preview_frame, yscrollcommand=scrollbar.set, font=("Courier", 11))
scrollbar.pack(side=RIGHT, fill=Y)
scrollbar.config(command=text_preview.yview)
text_preview.pack(fill=BOTH, expand=1)

# Company name fixed
COMPANY_NAME = "STAR FRUITS COMPANY"

def refresh_preview():
    text_preview.delete(1.0, END)
    text_preview.insert(END, COMPANY_NAME.center(64) + "\n")
    now_str = datetime.now().strftime('%d-%m-%Y %I:%M %p')
    text_preview.insert(END, ("Bill No: " + bill_no_var.get()).ljust(30) + ("Date & Time: " + now_str).rjust(34) + "\n")
    phone_str = phone_var.get().strip()
    party_str = party_name_var.get().strip()
    if party_str:
        line = f"{'Customer' if bill_type_var.get()=='Customer' else 'Supplier'}: {party_str}"
        if phone_str:
            line += f"      Phone: {phone_str}"
        text_preview.insert(END, line + "\n")
    text_preview.insert(END, "-"*64 + "\n")
    text_preview.insert(END, f"{'Item':28}{'Qty':>6}{'Rate':>12}{'Amount':>12}\n")
    text_preview.insert(END, "-"*64 + "\n")
    total = 0.0
    for name, qty, rate, amt in items:
        text_preview.insert(END, f"{name:28}{qty:>6}{rate:>12.2f}{amt:>12.2f}\n")
        total += amt
    text_preview.insert(END, "-"*64 + "\n")
    text_preview.insert(END, f"{'Total Bill:':>50}{total:>14.2f}\n")
    text_preview.insert(END, "-"*64 + "\n")

# ----------------- Bottom operations -----------------
ops_frame = Frame(root, padx=10, pady=10, bd=2, relief=RIDGE)
ops_frame.place(x=10, y=360, width=520, height=250)

def generate_preview():
    if not party_name_var.get().strip():
        messagebox.showerror("Error", "Enter customer/supplier name before generating bill.")
        return
    if not items:
        messagebox.showerror("Error", "Add at least one item to generate bill.")
        return
    refresh_preview()
    messagebox.showinfo("Success", "Bill preview generated successfully!")

def save_as_txt():
    if not party_name_var.get().strip() or not items:
        messagebox.showerror("Error", "Generate bill preview first.")
        return
    
    party = sanitize_filename(party_name_var.get())
    bill_no = bill_no_var.get()
    filename = f"Bill_{bill_no}_{party}.txt"
    filepath = filedialog.asksaveasfilename(
        initialdir=save_folder,
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    
    if filepath:
        try:
            with open(filepath, 'w') as f:
                f.write(text_preview.get(1.0, END))
            messagebox.showinfo("Success", f"Bill saved as: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

def save_as_pdf():
    if not REPORTLAB_AVAILABLE:
        messagebox.showerror("Error", "PDF functionality requires reportlab library.\nInstall with: pip install reportlab")
        return
        
    if not party_name_var.get().strip() or not items:
        messagebox.showerror("Error", "Generate bill preview first.")
        return
    
    party = sanitize_filename(party_name_var.get())
    bill_no = bill_no_var.get()
    filename = f"Bill_{bill_no}_{party}.pdf"
    filepath = filedialog.asksaveasfilename(
        initialdir=save_folder,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    if filepath:
        try:
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            y = height - 50
            
            # Company name
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, y, COMPANY_NAME)
            y -= 40
            
            # Bill details
            c.setFont("Helvetica", 12)
            now_str = datetime.now().strftime('%d-%m-%Y %I:%M %p')
            c.drawString(50, y, f"Bill No: {bill_no_var.get()}")
            c.drawRightString(width-50, y, f"Date & Time: {now_str}")
            y -= 25
            
            # Party details
            party_str = party_name_var.get().strip()
            phone_str = phone_var.get().strip()
            if party_str:
                line = f"{'Customer' if bill_type_var.get()=='Customer' else 'Supplier'}: {party_str}"
                if phone_str:
                    line += f"      Phone: {phone_str}"
                c.drawString(50, y, line)
                y -= 30
            
            # Table header
            c.line(50, y, width-50, y)
            y -= 20
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Item")
            c.drawString(300, y, "Qty")
            c.drawString(380, y, "Rate")
            c.drawString(460, y, "Amount")
            y -= 15
            c.line(50, y, width-50, y)
            y -= 15
            
            # Items
            c.setFont("Helvetica", 10)
            total = 0.0
            for name, qty, rate, amt in items:
                c.drawString(50, y, name)
                c.drawString(300, y, str(qty))
                c.drawString(380, y, f"{rate:.2f}")
                c.drawString(460, y, f"{amt:.2f}")
                total += amt
                y -= 20
            
            # Total
            c.line(50, y, width-50, y)
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(width-50, y, f"Total: {total:.2f}")
            
            c.save()
            messagebox.showinfo("Success", f"PDF saved as: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")

def clear_all():
    global items
    items = []
    party_name_var.set("")
    phone_var.set("")
    item_var.set("")
    rate_var.set("")
    qty_var.set(1)
    bill_no_var.set(str(random.randint(1000, 9999)))
    refresh_preview()

def open_folder():
    try:
        webbrowser.open(save_folder)
    except:
        messagebox.showerror("Error", "Cannot open folder.")

# Operation buttons
Label(ops_frame, text="Operations:", font=("Arial", 12, "bold")).pack(anchor=W, pady=(0,10))

btn_frame1 = Frame(ops_frame)
btn_frame1.pack(fill=X, pady=5)
Button(btn_frame1, text="Generate Preview", command=generate_preview, bg="#2b7a78", fg="white", width=20).pack(side=LEFT, padx=5)
Button(btn_frame1, text="Clear All", command=clear_all, bg="#c44536", fg="white", width=15).pack(side=LEFT, padx=5)

btn_frame2 = Frame(ops_frame)
btn_frame2.pack(fill=X, pady=5)
Button(btn_frame2, text="Save as TXT", command=save_as_txt, bg="#4a90e2", fg="white", width=20).pack(side=LEFT, padx=5)
Button(btn_frame2, text="Save as PDF", command=save_as_pdf, bg="#f39c12", fg="white", width=15).pack(side=LEFT, padx=5)

btn_frame3 = Frame(ops_frame)
btn_frame3.pack(fill=X, pady=5)
Button(btn_frame3, text="Open Bills Folder", command=open_folder, bg="#8e44ad", fg="white", width=20).pack(side=LEFT, padx=5)

# Status bar
status_frame = Frame(root, bd=1, relief=SUNKEN)
status_frame.pack(side=BOTTOM, fill=X)
Label(status_frame, text=f"Save Location: {save_folder}", anchor=W).pack(side=LEFT, padx=5)

# Initialize preview
refresh_preview()

# Start the application
if __name__ == "__main__":
    root.mainloop()