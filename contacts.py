import json
import re
from tkinter import *
from tkinter import messagebox, font

class Contact:
    def __init__(self, name, phone, email):
        self.name = name
        self.phone = phone
        self.email = email

class ContactManager:
    def __init__(self, filename):
        self.contacts = []
        self.filename = filename

    def add_contact(self, contact):
        self.contacts.append(contact)
        self.save_contacts()

    def is_duplicate(self, new_contact):
        for contact in self.contacts:
            if new_contact.name == contact.name and new_contact.phone == contact.phone:
                return True
        return False

    def is_duplicate_name(self, name):
        for contact in self.contacts:
            if name == contact.name:
                return True
        return False

    def delete_contact(self, index):
        del self.contacts[index]
        self.save_contacts()

    def update_contact(self, index, new_contact):
        self.contacts[index] = new_contact
        self.save_contacts()

    def search_contact(self, keyword):
        results = []
        for contact in self.contacts:
            if keyword.lower() in contact.name.lower() or keyword in contact.phone:
                results.append(contact)
        return results

    def save_contacts(self):
        with open(self.filename, 'w') as f:
            json.dump([vars(contact) for contact in self.contacts], f)

    def load_contacts(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.contacts = [Contact(**contact) for contact in data]
        except FileNotFoundError:
            pass  # If file does not exist, simply initialize an empty list
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Unable to load contacts from '{self.filename}'. The file contains invalid JSON data.")

class ContactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("700x700")
        self.root.configure(bg="#F2F2F2")
        self.center_window()

        self.contact_manager = ContactManager("contacts.json")
        self.contact_manager.load_contacts()

        self.font_bold = font.Font(family="Arial", size=12, weight="bold")
        self.font_normal = font.Font(family="Arial", size=12)

        self.name_label = Label(root, text="Name:", font=self.font_bold, bg="#F2F2F2")
        self.name_label.grid(row=0, column=0, sticky=W, padx=10, pady=5)
        self.name_entry = Entry(root, font=self.font_normal, bg="white", fg="black")
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        self.phone_label = Label(root, text="Phone:", font=self.font_bold, bg="#F2F2F2")
        self.phone_label.grid(row=1, column=0, sticky=W, padx=10, pady=5)
        self.phone_entry = Entry(root, font=self.font_normal, bg="white", fg="black")
        self.phone_entry.grid(row=1, column=1, padx=10, pady=5)

        self.email_label = Label(root, text="Email:", font=self.font_bold, bg="#F2F2F2")
        self.email_label.grid(row=2, column=0, sticky=W, padx=10, pady=5)
        self.email_entry = Entry(root, font=self.font_normal, bg="white", fg="black")
        self.email_entry.grid(row=2, column=1, padx=10, pady=5)

        self.add_button = Button(root, text="Add Contact", command=self.add_contact, font=self.font_bold, bg="#4CAF50", fg="white", bd=0)
        self.add_button.grid(row=3, column=0, padx=10, pady=5, sticky=E+W)

        self.delete_button = Button(root, text="Delete Contact", command=self.delete_contact, font=self.font_bold, bg="#f44336", fg="white", bd=0)
        self.delete_button.grid(row=3, column=1, padx=10, pady=5, sticky=E+W)

        self.search_label = Label(root, text="Search:", font=self.font_bold, bg="#F2F2F2")
        self.search_label.grid(row=4, column=0, sticky=W, padx=10, pady=5)
        self.search_entry = Entry(root, font=self.font_normal, bg="white", fg="black")
        self.search_entry.grid(row=4, column=1, padx=10, pady=5, sticky=E+W)
        self.search_button = Button(root, text="Search", command=self.search_contact, font=self.font_bold, bg="#2196F3", fg="white", bd=0)
        self.search_button.grid(row=4, column=2, padx=5, pady=5, sticky=E+W)

        self.contact_listbox = Listbox(root, width=50, font=self.font_normal, bg="white", fg="black", selectbackground="#2196F3", selectforeground="white")
        self.contact_listbox.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky=E+W)

        self.populate_contact_list()

        self.contact_listbox.bind("<Double-Button-1>", self.on_contact_select)

        root.grid_rowconfigure(5, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)

    def populate_contact_list(self):
        self.contact_listbox.delete(0, END)
        for contact in self.contact_manager.contacts:
            self.contact_listbox.insert(END, f"{contact.name} - {contact.phone} - {contact.email}")

    def add_contact(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()

        if name and phone:
            if not self.is_valid_phone(phone):
                messagebox.showerror("Error", "Invalid phone number. Phone number should have 10 digits.")
                return

            if not self.is_valid_email(email):
                messagebox.showerror("Error", "Invalid email address.")
                return

            original_name = name
            contact_number = 1
            while self.contact_manager.is_duplicate_name(name):
                name = f"{original_name} ({contact_number})"
                contact_number += 1

            contact = Contact(name, phone, email)
            if self.contact_manager.is_duplicate(contact):
                messagebox.showinfo("Duplicate Contact", "This contact already exists. Do you want to merge?")
                self.contact_manager.merge_contacts(contact)
            else:
                self.contact_manager.add_contact(contact)
                self.populate_contact_list()
                messagebox.showinfo("Success", "Contact added successfully.")
                self.clear_fields()
        else:
            messagebox.showerror("Error", "Name and Phone are required.")

    def delete_contact(self):
        selected_index = self.contact_listbox.curselection()
        if selected_index:
            contact_index = selected_index[0]
            self.contact_manager.delete_contact(contact_index)
            self.populate_contact_list()
            messagebox.showinfo("Success", "Contact deleted successfully.")
        else:
            messagebox.showerror("Error", "Please select a contact to delete.")

    def search_contact(self):
        keyword = self.search_entry.get()
        if keyword:
            results = self.contact_manager.search_contact(keyword)
            self.contact_listbox.delete(0, END)
            for contact in results:
                self.contact_listbox.insert(END, f"{contact.name} - {contact.phone} - {contact.email}")
        else:
            self.populate_contact_list()

    def on_contact_select(self, event):
        selected_index = self.contact_listbox.curselection()
        if selected_index:
            contact_index = selected_index[0]
            selected_contact = self.contact_manager.contacts[contact_index]
            messagebox.showinfo("Contact Info", f"Name: {selected_contact.name}\nPhone: {selected_contact.phone}\nEmail: {selected_contact.email}")

    def clear_fields(self):
        self.name_entry.delete(0, END)
        self.phone_entry.delete(0, END)
        self.email_entry.delete(0, END)

    def is_valid_email(self, email):
        return bool(re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email))

    def is_valid_phone(self, phone):
        return len(phone) == 10 and phone.isdigit()

    def center_window(self):
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2

        self.root.geometry("+{}+{}".format(x_coordinate, y_coordinate))

root = Tk()
app = ContactApp(root)
root.mainloop()
