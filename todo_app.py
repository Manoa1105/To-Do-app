import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk # Import ttk for themed widgets

DATABASE_NAME = 'tasks.db'

def get_db_connection():
    """Établit une connexion à la base de données."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise la base de données en créant la table tasks."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL, -- Format AAAA-MM-JJ
            status INTEGER NOT NULL DEFAULT 0 -- 0 pour non fait, 1 pour fait
        )
    ''')
    conn.commit()
    conn.close()

# --- Fonctions CRUD (modifiées pour interagir avec Tkinter) ---

def add_task_to_db(name, description, date):
    """Ajoute une nouvelle tâche à la base de données."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tasks (name, description, date, status) VALUES (?, ?, ?, ?)",
                       (name, description, date, 0))
        conn.commit()
        return True # Succès
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ajout de la tâche : {e}")
        return False # Échec
    finally:
        conn.close()

def get_all_tasks():
    """Récupère toutes les tâches de la base de données."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, date, status FROM tasks ORDER BY date, id")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task_status_in_db(task_id, new_status):
    """Met à jour le statut (fait/non fait) d'une tâche."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        if cursor.rowcount > 0:
            return True # Succès
        else:
            messagebox.showwarning("Attention", f"Aucune tâche trouvée avec l'ID {task_id}.")
            return False
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du statut : {e}")
        return False
    finally:
        conn.close()

# --- Interface graphique Tkinter ---

class TodoApp:
    def __init__(self, master):
        self.master = master
        master.title("Mon Emploi du Temps")
        master.geometry("600x500") # Taille de la fenêtre

        self.create_widgets()
        self.load_tasks() # Charge les tâches au démarrage de l'app

    def create_widgets(self):
        # Cadre pour l'ajout de tâches
        add_frame = tk.LabelFrame(self.master, text="Ajouter une Tâche", padx=10, pady=10)
        add_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(add_frame, text="Nom:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = tk.Entry(add_frame, width=40)
        self.name_entry.grid(row=0, column=1, pady=2)

        tk.Label(add_frame, text="Description (opt.):").grid(row=1, column=0, sticky="w", pady=2)
        self.desc_entry = tk.Entry(add_frame, width=40)
        self.desc_entry.grid(row=1, column=1, pady=2)

        tk.Label(add_frame, text="Date (AAAA-MM-JJ):").grid(row=2, column=0, sticky="w", pady=2)
        self.date_entry = tk.Entry(add_frame, width=40)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d')) # Date d'aujourd'hui par défaut
        self.date_entry.grid(row=2, column=1, pady=2)

        tk.Button(add_frame, text="Ajouter Tâche", command=self.add_task_gui).grid(row=3, column=0, columnspan=2, pady=5)

        # Cadre pour l'affichage des tâches (Treeview pour une meilleure présentation)
        tasks_frame = tk.LabelFrame(self.master, text="Liste des Tâches", padx=10, pady=10)
        tasks_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(tasks_frame, columns=("ID", "Nom", "Description", "Date", "Statut"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Statut", text="Statut")

        # Ajuster la largeur des colonnes (optionnel)
        self.tree.column("ID", width=30, anchor="center")
        self.tree.column("Nom", width=120)
        self.tree.column("Description", width=150)
        self.tree.column("Date", width=80, anchor="center")
        self.tree.column("Statut", width=60, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        # Barre de défilement pour le Treeview
        scrollbar = ttk.Scrollbar(tasks_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Boutons d'action pour les tâches
        actions_frame = tk.Frame(self.master)
        actions_frame.pack(pady=5)

        tk.Button(actions_frame, text="Marquer FAIT/NON FAIT", command=self.toggle_task_status_gui).pack(side="left", padx=5)
        tk.Button(actions_frame, text="Rafraîchir", command=self.load_tasks).pack(side="left", padx=5)


    def add_task_gui(self):
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        date = self.date_entry.get().strip()

        if not name or not date:
            messagebox.showwarning("Entrée Manquante", "Le nom et la date de la tâche sont obligatoires.")
            return

        try:
            datetime.strptime(date, '%Y-%m-%d') # Valide le format de la date
        except ValueError:
            messagebox.showwarning("Format Invalide", "Le format de la date doit être AAAA-MM-JJ.")
            return

        if add_task_to_db(name, description, date):
            messagebox.showinfo("Succès", f"Tâche '{name}' ajoutée pour le {date}.")
            self.name_entry.delete(0, tk.END) # Efface les champs après ajout
            self.desc_entry.delete(0, tk.END)
            self.load_tasks() # Rafraîchit la liste

    def load_tasks(self):
        # Efface les éléments existants dans le Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        tasks = get_all_tasks()
        for task in tasks:
            status_text = "FAIT" if task['status'] == 1 else "NON FAIT"
            self.tree.insert("", "end", values=(task['id'], task['name'], task['description'], task['date'], status_text))

    def toggle_task_status_gui(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner une tâche dans la liste.")
            return

        # Récupérer l'ID de la tâche sélectionnée
        task_id = self.tree.item(selected_item[0], 'values')[0]
        current_status_text = self.tree.item(selected_item[0], 'values')[4] # Récupère le texte du statut

        new_status = 1 if current_status_text == "NON FAIT" else 0

        if update_task_status_in_db(task_id, new_status):
            messagebox.showinfo("Succès", f"Statut de la tâche {task_id} mis à jour.")
            self.load_tasks() # Rafraîchit la liste

if __name__ == '__main__':
    init_db() # S'assure que la base de données est prête
    root = tk.Tk() # Crée la fenêtre principale Tkinter
    app = TodoApp(root) # Instancie l'application
    root.mainloop() # Lance la boucle principale de Tkinter (l'application tourne)