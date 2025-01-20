import tkinter as tk
import numpy as np
import cv2
from PIL import Image
from tkinter import messagebox, Toplevel

class MenuBarProjekt(tk.Menu):
    """Menu 'Projekt' zawierające narzędzie do ekstrakcji linii pionowych i poziomych."""
    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=False)
        self.parent = parent
        self.add_command(label="Ekstrakcja linii", command=lambda: self.extract_lines(parent))

    def extract_lines(self, parent):
        """Ekstrakcja linii pionowych i poziomych z obrazu."""
        if not parent.loaded_image_data:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby przeprowadzić ekstrakcję linii.")
            return

        img = np.array(parent.loaded_image_data[2].convert("L"))  # Konwersja do skali szarości

        # Konwersja do obrazu binarnego (dla lepszych wyników progowanie adaptacyjne)
        binary_img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -2)

        def perform_extraction(selected_option):
            """Wykonuje operacje morfologiczne w celu ekstrakcji linii."""
            try:
                kernel_size = int(kernel_size_entry.get())
                if kernel_size <= 0 or kernel_size % 2 == 0:
                    raise ValueError("Rozmiar maski musi być liczbą nieparzystą i większą od zera.")

                results = {}

                # Ekstrakcja linii pionowych
                if selected_option in ["Pionowe", "Obie"]:
                    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_size))
                    vertical_lines = cv2.erode(binary_img, vertical_kernel)
                    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel)
                    results["Linie pionowe"] = vertical_lines

                # Ekstrakcja linii poziomych
                if selected_option in ["Poziome", "Obie"]:
                    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, 1))
                    horizontal_lines = cv2.erode(binary_img, horizontal_kernel)
                    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel)
                    results["Linie poziome"] = horizontal_lines

                # Wyświetlenie wyników
                for title, lines_img in results.items():
                    lines_image = Image.fromarray(lines_img)
                    parent.display_image(lines_image, title)

                extraction_window.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", f"Operacja nie powiodła się: {e}")

        # Tworzenie okna do ustawienia parametrów
        extraction_window = Toplevel(parent)
        extraction_window.title("Ekstrakcja Linii")

        tk.Label(extraction_window, text="Rozmiar maski (nieparzysta):", font=("Arial", 10)).pack(pady=5)
        kernel_size_entry = tk.Entry(extraction_window)
        kernel_size_entry.pack(pady=5)
        kernel_size_entry.insert(0, "15")  # Domyślny rozmiar maski

        tk.Label(extraction_window, text="Wybierz rodzaj linii do ekstrakcji:", font=("Arial", 10)).pack(pady=5)
        line_type = tk.StringVar(value="Obie")
        tk.Radiobutton(extraction_window, text="Pionowe", variable=line_type, value="Pionowe").pack()
        tk.Radiobutton(extraction_window, text="Poziome", variable=line_type, value="Poziome").pack()
        tk.Radiobutton(extraction_window, text="Obie", variable=line_type, value="Obie").pack()

        tk.Button(extraction_window, text="Wykonaj", command=lambda: perform_extraction(line_type.get())).pack(pady=10)