import tkinter as tk
import numpy as np
from tkinter import messagebox, Toplevel

class MenuBarLab1(tk.Menu):
    """Menu 'Laboratorium 1' zawierające funkcjonalność tworzenia tablicy LUT."""
    def __init__(self, parent):
        """
        Inicjalizuje menu dla Laboratorium 1, zawierające funkcję do generowania tablicy LUT.
        """
        tk.Menu.__init__(self, parent, tearoff=False)
        self.parent = parent
        self.add_command(label="Twórz tablicę LUT", command=lambda: self.create_lut(parent))

    def create_lut(self, parent):
        """
        Tworzy tablicę LUT (Look-Up Table) dla obrazu załadowanego w aplikacji.
        Obsługuje zarówno obrazy monochromatyczne, jak i kolorowe.
        """
        if parent.loaded_image_data:
            img = np.array(parent.loaded_image_data[2])  # Wczytanie obrazu jako tablicy NumPy

            def generate_grayscale_lut():
                """
                Generuje tablicę LUT dla obrazów w odcieniach szarości lub binarnych.
                LUT zawiera liczbę wystąpień każdej wartości intensywności.
                """
                lut = np.zeros(256, dtype=np.int32)  # Inicjalizacja tablicy LUT dla 256 poziomów intensywności
                unique_values, counts = np.unique(img.flatten(), return_counts=True)
                for value, count in zip(unique_values, counts):
                    lut[value] = count
                return lut

            def generate_color_lut():
                """
                Generuje tablice LUT dla obrazów kolorowych.
                Każdy kanał (R, G, B) otrzymuje osobną tablicę LUT.
                """
                luts = {}
                for i, color in enumerate(["Blue", "Green", "Red"]):
                    channel = img[:, :, i]
                    lut = np.zeros(256, dtype=np.int32)  # Inicjalizacja tablicy LUT dla 256 poziomów intensywności
                    unique_values, counts = np.unique(channel.flatten(), return_counts=True)
                    for value, count in zip(unique_values, counts):
                        lut[value] = count
                    luts[color] = lut
                return luts

            def display_lut(lut, is_color=False):
                """
                Wyświetla tablicę LUT w nowym oknie.
                Obsługuje zarówno tablice dla obrazów w odcieniach szarości, jak i dla kanałów RGB.
                """
                lut_window = Toplevel(parent)
                lut_window.title("Tablica LUT")

                # Tworzy pole tekstowe do wyświetlania wartości LUT
                text_box = tk.Text(lut_window, wrap="none", height=30, width=50)
                text_box.pack(pady=10, fill="both", expand=True)
                if is_color:
                    # Wyświetla tablice LUT dla kanałów RGB
                    text_box.insert("end", "Intensity |   Blue   |   Green   |   Red\n")
                    text_box.insert("end", "-" * 40 + "\n")
                    for i in range(256):
                        blue = lut["Blue"][i]
                        green = lut["Green"][i]
                        red = lut["Red"][i]
                        text_box.insert("end", f"{i:9d} | {blue:8d} | {green:8d} | {red:8d}\n")
                else:
                    # Wyświetla tablicę LUT dla obrazów w odcieniach szarości
                    text_box.insert("end", f"LUT:\n")
                    for i, value in enumerate(lut):
                        text_box.insert("end", f"{i}: {value}\n")

                text_box.configure(state="disabled")  # Zabezpieczenie tekstu przed edycją

            # Sprawdza, czy obraz jest monochromatyczny czy kolorowy, i generuje odpowiednią tablicę LUT
            if len(img.shape) == 2:  # Obraz w odcieniach szarości
                lut = generate_grayscale_lut()
                display_lut(lut, is_color=False)
            elif len(img.shape) == 3 and img.shape[2] == 3:  # Obraz kolorowy (RGB)
                luts = generate_color_lut()
                display_lut(luts, is_color=True)
            else:
                # Wyświetla komunikat o błędzie w przypadku nieobsługiwanego formatu obrazu
                messagebox.showerror("Błąd", "Nieobsługiwany format obrazu.")
        else:
            # Wyświetla komunikat ostrzegawczy, jeśli obraz nie został załadowany
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby utworzyć tablicę LUT.")
