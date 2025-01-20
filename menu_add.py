from tkinter import filedialog, messagebox
from PIL import Image
import tkinter as tk


class MenuBarFile:
    def load_image(self, parent):
        """
        Otwiera okno dialogowe umożliwiające załadowanie obrazu.
        Obraz jest następnie przechowywany w obiekcie aplikacji oraz wyświetlany w zakładce.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Otwórz obraz przy użyciu PIL
                pil_image = Image.open(file_path)
                parent.loaded_image_data = [file_path, list(pil_image.getdata()), pil_image]
                parent.loaded_image_mode = pil_image.mode
                parent.zoom_level = 1

                # Wyświetl załadowany obraz w zakładce "Original"
                parent.display_image(pil_image, "Original")
                parent.processed_image_data = None
            except Exception as e:
                # Wyświetl komunikat o błędzie, jeśli obraz nie został załadowany
                messagebox.showerror("Error", f"Could not load image: {e}")

    def save_image(self, parent):
        """
        Zapisuje obraz z aktualnie otwartej zakładki na dysk.
        """
        # Pobierz aktualnie wybraną zakładkę
        current_tab = parent.notebook.select()
        if not current_tab:
            messagebox.showwarning("Warning", "No tab selected.")
            return

        # Pobierz obraz przypisany do aktywnej zakładki
        active_frame = parent.notebook.nametowidget(current_tab)
        image_label = active_frame.winfo_children()[0]  # Pierwsze dziecko ramki to widget Label z obrazem
        pil_image = getattr(image_label, 'pil_image', None)
        if pil_image is None:
            messagebox.showwarning("Warning", "No image data found to save.")
            return

        # Otwórz okno dialogowe do zapisu pliku
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("Bitmap files", "*.bmp"),
                ("Tiff files", "*.tiff"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            try:
                # Zapisz obraz w wybranym formacie
                pil_image.save(file_path)
                messagebox.showinfo("Saved", f"Image saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {e}")

    def duplicate_image(self, parent):
        """
        Tworzy kopię aktualnie załadowanego obrazu i wyświetla ją w nowej zakładce.
        """
        if not parent.loaded_image_data:
            messagebox.showwarning("Warning", "No image loaded to duplicate.")
            return

        # Utwórz kopię obrazu za pomocą PIL
        duplicate_image = parent.loaded_image_data[2].copy()

        # Nadaj nowej zakładce unikalną nazwę
        duplicate_title = f"Duplicate {len(parent.notebook.tabs())}"
        parent.display_image(duplicate_image, duplicate_title)

    def close_tab(self, parent):
        """
        Zamyka aktualnie wybraną zakładkę w aplikacji.
        """
        parent.close_current_tab()

    def informacje(self, parent):
        """
        Zawieta informacje o twrórcy aplikacj
        """
        messagebox.showinfo(
            "O Aplikacji",
            (
                "Algorytmy Przetwarzania Obrazów - Project\n"
                "Wersja: 1.0\n"
                "Autor: Karol Polak\n"
                "Indeks: 18540\n"
                "Język: Python\n\n"
                "Opis:\n"
                "To oprogramowanie zostało stworzone w ramach projektu "
                "na zajęciach i oferuje narzędzia do analizy obrazów, "
                "operacji morfologicznych oraz innych funkcji związanych "
                "z przetwarzaniem obrazów."
            ))


class MenuBarAdd(tk.Menu):
    def __init__(self, parent):
        """
        Tworzy menu główne aplikacji z opcjami dotyczącymi plików.
        """
        tk.Menu.__init__(self, parent, tearoff=False)
        self.file_menu = tk.Menu(self, tearoff=0)
        self.menu_bar_file = MenuBarFile()

        # Dodaj opcje do menu "Plik"
        self.file_menu.add_command(label="Otwórz", command=lambda: self.menu_bar_file.load_image(parent))
        self.file_menu.add_command(label="Zapisz", command=lambda: self.menu_bar_file.save_image(parent))
        self.file_menu.add_command(label="Duplikuj", command=lambda: self.menu_bar_file.duplicate_image(parent))
        self.file_menu.add_command(label="Zamknij kartę", command=lambda: self.menu_bar_file.close_tab(parent))
        self.file_menu.add_command(label="Informacje", command=lambda: self.menu_bar_file.informacje(parent))

        # Dodaj menu "Plik" do paska menu
        self.add_cascade(label="Plik", menu=self.file_menu)
