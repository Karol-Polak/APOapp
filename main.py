import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from lab1 import MenuBarLab1
from lab2 import MenuBarLab2
from lab3 import MenuBarLab3
from lab4 import MenuBarLab4
from lab5 import MenuBarLab5
from lab6 import MenuBarLab6
from projekt import MenuBarProjekt
from menu_add import MenuBarAdd

class ApoProjectCore(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Apo Project")
        self.geometry("800x600")
        self.loaded_image_data = None
        self.loaded_image_mode = None
        self.zoom_level = 1
        self.image_label = None
        self.display_text = tk.StringVar()

        # Menu główne - dodanie opcji menu z różnych labów
        self.menu = MenuBarAdd(self)
        self.config(menu=self.menu)

        # Dodanie menu z poszczególnych labo
        self.lab1_menu = MenuBarLab1(self)
        self.menu.add_cascade(label="Laboratorium 1", menu=self.lab1_menu)

        self.lab2_menu = MenuBarLab2(self)
        self.menu.add_cascade(label="Laboratorium 2", menu=self.lab2_menu)

        self.lab3_menu = MenuBarLab3(self)
        self.menu.add_cascade(label="Laboratorium 3", menu=self.lab3_menu)

        self.lab4_menu = MenuBarLab4(self)
        self.menu.add_cascade(label="Laboratorium 4", menu=self.lab4_menu)

        self.lab5_menu = MenuBarLab5(self)
        self.menu.add_cascade(label="Laboratorium 5", menu=self.lab5_menu)

        self.lab6_menu = MenuBarLab6(self)
        self.menu.add_cascade(label="Laboratorium 6", menu=self.lab6_menu)

        self.projekt_menu = MenuBarProjekt(self)
        self.menu.add_cascade(label="Projekt", menu=self.projekt_menu)

        #notebook dla kart z obrazami (obsługa wielu zakładek)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.update_display_text)

        # Informacje o formacie obrazu
        self.info_frame = tk.Frame(self)
        self.info_frame.place(x=10, y=10)

        self.info_label = tk.Label(self.info_frame, textvariable=self.display_text, font=("Arial", 10))
        self.info_label.pack(side="left")

        # Przyciski zoom (powiększanie obrazu)
        zoom_in_button = tk.Button(self.info_frame, text="+", command=self.zoom_in)
        zoom_in_button.pack(side="left", padx=5)

        zoom_out_button = tk.Button(self.info_frame, text="-", command=self.zoom_out)
        zoom_out_button.pack(side="left", padx=5)

        reset_button = tk.Button(self.info_frame, text="R", command=self.reset_zoom)
        reset_button.pack(side="left", padx=5)

        #pozycja startowa dla przesuwania obrazu
        self.start_x = 0
        self.start_y = 0

    #dodawanie zakładek w nootebook
    def add_tab(self, title):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        image_label = tk.Label(frame)
        image_label.pack(fill="both", expand=True)

        # Dodajemy obsługę zdarzeń myszy (przesuwanie obrazu)
        image_label.bind("<Button-1>", self.start_move)
        image_label.bind("<B1-Motion>", self.move_image)

        return image_label

    #wyświetlanie obrazu w określonej zakładce nootebooka
    #tworzenie zakładki jeśli ta nie istnieje
    def display_image(self, pil_image, tab_name="Original"):
        """
        Wyświetla obraz w zakładce o podanej nazwie. Jeśli zakładka nie istnieje, tworzy nową.
        """
        # Skaluje obraz zgodnie z poziomem zoomu
        width, height = pil_image.size
        width, height = int(width * self.zoom_level), int(height * self.zoom_level)
        resized_image = pil_image.resize((width, height), Image.LANCZOS)
        image_tk = ImageTk.PhotoImage(resized_image)

        # Pobierz lub utwórz zakładkę
        existing_tabs = self.notebook.tabs()
        tab_index = next((i for i, tab in enumerate(existing_tabs) if self.notebook.tab(tab, "text") == tab_name), None)

        if tab_index is None:
            self.image_label = self.add_tab(tab_name)
        else:
            frame = self.notebook.winfo_children()[tab_index]
            self.image_label = frame.winfo_children()[0]

        # Ustaw obraz w etykiecie i dodaj odniesienie do obiektu PIL
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk
        self.image_label.pil_image = pil_image  # Przypisz oryginalny obraz PIL

        # Aktualizuj tekst wyświetlany w informacji
        self.update_display_text()

    #inicjalizacja przesuwania obrazu za pomocą myszy
    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    #obsługa przesuwania obrazu w zakładce
    def move_image(self, event):
        x = event.x - self.start_x
        y = event.y - self.start_y
        self.image_label.place(x=self.image_label.winfo_x() + x, y=self.image_label.winfo_y() + y)

    #powiększanie obrazu o współczynnik
    def zoom_in(self):
        self.zoom_level *= 1.1
        self.update_displayed_image()

    #pomniejszanie obrazu o współczynnik
    def zoom_out(self):
        self.zoom_level /= 1.1
        self.update_displayed_image()

    #reset powiększenia obrazu do wartości początkowej
    #reset pozwala cofnąć też zmiany które zaszły na obrazie (reset fabryczny)
    def reset_zoom(self):
        self.zoom_level = 1
        self.update_displayed_image()

    #aktualizacja obrazu zgodnie z powiększeniem
    def update_displayed_image(self):
        if self.loaded_image_data:
            self.display_image(self.loaded_image_data[2], self.notebook.tab(self.notebook.select(), "text"))

    #aktualizacja tekstu na zakładkach (poziom zoom)
    def update_display_text(self, event=None):
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        zoom_text = "Standard" if self.zoom_level == 1 else f"Zoom {self.zoom_level:.1f}x"
        self.display_text.set(f"{tab_name} - {zoom_text}")

    #zamykanie aktualnie wybranej karty nootebooka
    def close_current_tab(self):
        """Zamyka aktualnie wybraną kartę."""
        current_tab = self.notebook.select()
        if current_tab:
            self.notebook.forget(current_tab)
        else:
            messagebox.showwarning("Brak kart", "Nie ma otwartych kart do zamknięcia.")

if __name__ == "__main__":
    app = ApoProjectCore()
    app.mainloop()


#created by: Karol Polak