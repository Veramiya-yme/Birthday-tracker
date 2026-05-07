from tkinter import *
from tkinter import messagebox
from datetime import date, datetime
import json
import os

FILENAME = "birthdays.json"
birthday_list = []

# --- Data Persistence ---
def save_data():
    serializable_list = []
    for person in birthday_list:
        serializable_list.append({
            "name": person["name"],
            "birthday": person["birthday"].strftime("%Y-%m-%d"),
            "created": person.get("created", date.today().strftime("%Y-%m-%d")),
            "updated": person.get("updated", date.today().strftime("%Y-%m-%d"))
        })
    with open(FILENAME, "w") as f:
        json.dump(serializable_list, f)

def load_data():
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r") as f:
                data = json.load(f)
                birthday_list.clear()
                for item in data:
                    birthday_list.append({
                        "name": item["name"],
                        "birthday": datetime.strptime(item["birthday"], "%Y-%m-%d").date(),
                        "created": item.get("created", "Unknown"),
                        "updated": item.get("updated", "Unknown")
                    })
            update_listbox()
        except Exception as e:
            print(f"Error loading file: {e}")

# --- Search & Refresh ---
def update_listbox(filter_text=""):
    name_listbox.delete(0, END)
    for person in birthday_list:
        if filter_text.lower() in person["name"].lower():
            name_listbox.insert(END, person["name"])

def on_search_change(event):
    update_listbox(search_entry.get())

# --- Logic Functions ---
def add_birthday():
    name = name_entry.get().strip()
    b_day_str = date_entry.get().strip()
    today_str = date.today().strftime("%Y-%m-%d")

    if not name or not b_day_str:
        status_label.config(text="Error: Fill in both fields!", fg="#b30000")
        return

    # STRICT NAME CHECK: No numbers allowed
    if not all(x.isalpha() or x.isspace() for x in name):
        status_label.config(text="Invalid Name! Use letters only.", fg="#b30000")
        return

    try:
        b_date = datetime.strptime(b_day_str, "%Y-%m-%d").date()
        if b_date.year > 2026:
            status_label.config(text="Invalid Year! 2026 or earlier.", fg="#b30000")
            return

        birthday_list.append({
            "name": name, 
            "birthday": b_date,
            "created": today_str,
            "updated": today_str
        })
        update_listbox()
        save_data()
        
        name_entry.delete(0, END)
        date_entry.delete(0, END)
        status_label.config(text=f"Success: Saved {name}!", fg="#006400")
    except ValueError:
        status_label.config(text="Error: Use YYYY-MM-DD", fg="#b30000")

def open_details():
    try:
        selected_index = name_listbox.curselection()[0]
        selected_name = name_listbox.get(selected_index)
        person = next(p for p in birthday_list if p["name"] == selected_name)
        
        detail_win = Toplevel(window)
        detail_win.title(f"Details: {person['name']}")
        detail_win.geometry("300x400")
        detail_win.config(bg="#fef9e7")

        Label(detail_win, text=f"Info for {person['name']}", font=("Arial", 12, "bold"), bg="#fef9e7").pack(pady=10)
        Label(detail_win, text=f"Created: {person['created']}", bg="#fef9e7").pack()
        Label(detail_win, text=f"Last Updated: {person['updated']}", bg="#fef9e7").pack(pady=5)

        Label(detail_win, text="Change Birthday (YYYY-MM-DD):", bg="#fef9e7").pack(pady=10)
        new_date_entry = Entry(detail_win)
        new_date_entry.insert(0, person["birthday"].strftime("%Y-%m-%d"))
        new_date_entry.pack()

        def update_record():
            try:
                new_date = datetime.strptime(new_date_entry.get(), "%Y-%m-%d").date()
                person["birthday"] = new_date
                person["updated"] = date.today().strftime("%Y-%m-%d")
                save_data()
                detail_win.destroy()
                status_label.config(text="Updated successfully!", fg="#006400")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format!")

        Button(detail_win, text="Save Changes", command=update_record, bg="#d4efdf").pack(pady=20)
    except IndexError:
        status_label.config(text="Select a name first!", fg="#b30000")

def delete_person():
    try:
        selected_index = name_listbox.curselection()[0]
        selected_name = name_listbox.get(selected_index)
        global birthday_list
        birthday_list = [p for p in birthday_list if p["name"] != selected_name]
        update_listbox()
        save_data()
        status_label.config(text="Deleted successfully!", fg="#006400")
    except IndexError:
        status_label.config(text="Select a name to delete!", fg="#b30000")

def check_birthdays():
    today = date.today()
    results = []
    for p in birthday_list:
        if p["birthday"].month == today.month and p["birthday"].day == today.day:
            age = today.year - p["birthday"].year
            results.append(f"It's {p['name']}'s birthday today! They are {age}!")
    
    display_label.config(text="\n".join(results) if results else "It's no one's birthday today :(.")

# --- UI Setup ---
window = Tk()
window.geometry("900x600")
window.title("Birthday Tracker")
bg_color = "#9ab5e2" 
tint_white = "#fffff0"
window.config(background=bg_color)

main_frame = Frame(window, bg=bg_color)
main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

# --- Left Side (Entry) ---
left_frame = Frame(main_frame, bg=bg_color)
left_frame.pack(side=LEFT, fill=Y, padx=20)

Label(left_frame, text="Birthday Tracker", font=("Ravie", 18), bg=bg_color, fg="white").pack(pady=10)

Label(left_frame, text="Name:", bg=bg_color, fg="white", font=("Arial", 10, "bold")).pack(anchor=W)
name_entry = Entry(left_frame, width=30, font=("Arial", 12), bg=tint_white)
name_entry.pack(pady=5)

Label(left_frame, text="Birthday (YYYY-MM-DD):", bg=bg_color, fg="white", font=("Arial", 10, "bold")).pack(anchor=W)
date_entry = Entry(left_frame, width=30, font=("Arial", 12), bg=tint_white)
date_entry.pack(pady=5)

Button(left_frame, text="Add to List", command=add_birthday, width=20, bg=tint_white, font=("Arial", 10, "bold")).pack(pady=10)
status_label = Label(left_frame, text="", bg=bg_color, font=("Arial", 10, "italic", "bold"))
status_label.pack()

Button(left_frame, text="CHECK TODAY'S BIRTHDAYS", command=check_birthdays, bg="#fbedae", font=("Arial", 10, "bold"), height=2).pack(pady=20)
display_label = Label(left_frame, text="", bg=bg_color, fg="white", font=("Arial", 12, "bold"), wraplength=350)
display_label.pack()

# --- Right Side (List & Search) ---
right_frame = Frame(main_frame, bg=bg_color)
right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=20)

Label(right_frame, text="Search People:", bg=bg_color, fg="white", font=("Ravie", 12)).pack(pady=5)
search_entry = Entry(right_frame, font=("Arial", 12), bg=tint_white)
search_entry.pack(fill=X, pady=5)
search_entry.bind("<KeyRelease>", on_search_change)

name_listbox = Listbox(right_frame, font=("Arial", 12), bg=tint_white, borderwidth=0, highlightthickness=0)
name_listbox.pack(fill=BOTH, expand=True, pady=10)

btn_frame = Frame(right_frame, bg=bg_color)
btn_frame.pack(fill=X)

Button(btn_frame, text="View Details / Edit", command=open_details, bg="#a9d1f1", font=("Arial", 10, "bold")).pack(side=LEFT, expand=True, fill=X, padx=2)
Button(btn_frame, text="Delete Selected", command=delete_person, bg="#f1a9a9", font=("Arial", 10, "bold")).pack(side=LEFT, expand=True, fill=X, padx=2)

load_data()
window.mainloop()