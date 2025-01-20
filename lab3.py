import tkinter as tk
import numpy as np
import cv2
from PIL import Image
from tkinter import messagebox, Toplevel, filedialog


def stretch_histogram(img, p1, p2, q3, q4):
    """
    Rozciąga histogram obrazu w zakresie (p1, p2) do zakresu (q3, q4).

    :param img: Obraz źródłowy w odcieniach szarości jako macierz NumPy.
    :param p1: Minimalna wartość zakresu w obrazie źródłowym.
    :param p2: Maksymalna wartość zakresu w obrazie źródłowym.
    :param q3: Minimalna wartość zakresu w obrazie wynikowym.
    :param q4: Maksymalna wartość zakresu w obrazie wynikowym.
    :return: Obraz wynikowy po rozciągnięciu histogramu.
    """
    # Stosujemy transformację zgodnie z opisanym algorytmem
    result = np.zeros_like(img, dtype=np.float32)
    result[img < p1] = q3
    result[img > p2] = q4
    mask = (img >= p1) & (img <= p2)
    result[mask] = q3 + ((img[mask] - p1) / (p2 - p1)) * (q4 - q3)

    # Klipowanie do przedziału [0, 255] i konwersja do uint8
    return np.clip(result, 0, 255).astype(np.uint8)

class MenuBarLab3(tk.Menu):
    """Menu 'Laboratorium 3' zawierające funkcje operacji punktowych wieloargumentowych na obrazach monochromatycznych."""
    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=False)
        self.parent = parent
        self.add_command(label="Operacje punktowe", command=lambda: self.point_operations(parent))
        self.add_command(label="Operacje logiczne", command=lambda: self.logical_operations(parent))
        self.add_command(label="Rozciąganie histogramu", command=lambda: self.apply_histogram_stretch(parent))

    def point_operations(self, parent):
        """Realizuje operacje punktowe na obrazach monochromatycznych."""
        if parent.loaded_image_data:
            img1 = np.array(parent.loaded_image_data[2].convert("L"))

            def load_second_image():
                """Load a second grayscale image for two-operand operations."""
                file_path = filedialog.askopenfilename(
                    filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
                )
                if file_path:
                    try:
                        img2 = np.array(Image.open(file_path).convert("L"))
                        if img1.shape != img2.shape:
                            messagebox.showerror("Błąd", "Obrazy muszą mieć takie same rozmiary.")
                            return None
                        return img2
                    except Exception as e:
                        messagebox.showerror("Błąd", f"Nie udało się wczytać obrazu: {e}")
                        return None

            def validate_and_perform_operation(operation, value=None, img2=None, saturation=True):
                """Validate inputs and perform the selected operation."""
                try:
                    if value is not None:
                        value = int(value)

                    if img2 is not None and img1.shape != img2.shape:
                        raise ValueError("Obrazy muszą mieć takie same rozmiary.")

                    # Perform operation
                    if operation == "add":
                        result = img1 + img2 if saturation else cv2.add(img1 // 2, img2 // 2)
                    elif operation == "absolute_difference":
                        result = cv2.absdiff(img1, img2)
                    elif operation == "add_scalar":
                        result = img1 + value
                    elif operation == "multiply_scalar":
                        result = img1 * value
                    elif operation == "divide_scalar":
                        result = img1 // value if value != 0 else img1
                    else:
                        raise ValueError("Nieznana operacja.")

                    # Apply saturation
                    if saturation:
                        result = np.clip(result, 0, 255)

                    return result.astype(np.uint8)
                except Exception as e:
                    messagebox.showerror("Błąd", f"Operacja nie powiodła się: {e}")
                    return None

            def perform_operation_with_second_image(operation, saturation):
                """Load a second image and perform the operation."""
                img2 = load_second_image()
                if img2 is None:
                    return
                result = validate_and_perform_operation(operation, img2=img2, saturation=saturation)
                if result is not None:
                    result_image = Image.fromarray(result)
                    parent.display_image(result_image, f"{operation.capitalize()} {'(Saturation)' if saturation else '(No Saturation)'}")

            def perform_scalar_operation(operation, saturation):
                """Perform operations with a scalar value."""
                scalar_window = Toplevel(parent)
                scalar_window.title(f"{operation.capitalize()} przez liczbę całkowitą")

                tk.Label(scalar_window, text="Podaj wartość skalaru:", font=("Arial", 10)).pack(pady=5)
                scalar_entry = tk.Entry(scalar_window)
                scalar_entry.pack(pady=5)
                scalar_entry.insert(0, "10")

                def apply_operation():
                    scalar_value = scalar_entry.get()
                    result = validate_and_perform_operation(operation, value=scalar_value, saturation=saturation)
                    if result is not None:
                        result_image = Image.fromarray(result)
                        parent.display_image(result_image, f"{operation.capitalize()} {scalar_value} {'(Saturation)' if saturation else '(No Saturation)'}")
                    scalar_window.destroy()

                tk.Button(scalar_window, text="Zastosuj", command=apply_operation).pack(pady=10)

            # Create a window for operations
            operation_window = Toplevel(parent)
            operation_window.title("Operacje Punktowe")

            # Add operations with two images
            tk.Label(operation_window, text="Operacje na dwóch obrazach:", font=("Arial", 12)).pack(pady=5)
            tk.Button(operation_window, text="Dodawanie (z wysyceniem)", command=lambda: perform_operation_with_second_image("add", True)).pack(pady=5)
            tk.Button(operation_window, text="Dodawanie (bez wysycenia)", command=lambda: perform_operation_with_second_image("add", False)).pack(pady=5)
            tk.Button(operation_window, text="Różnica bezwzględna", command=lambda: perform_operation_with_second_image("absolute_difference", True)).pack(pady=5)

            # Add scalar operations
            tk.Label(operation_window, text="Operacje ze skalarem:", font=("Arial", 12)).pack(pady=5)
            tk.Button(operation_window, text="Dodawanie (z wysyceniem)", command=lambda: perform_scalar_operation("add_scalar", True)).pack(pady=5)
            tk.Button(operation_window, text="Dodawanie (bez wysycenia)", command=lambda: perform_scalar_operation("add_scalar", False)).pack(pady=5)
            tk.Button(operation_window, text="Mnożenie (z wysyceniem)", command=lambda: perform_scalar_operation("multiply_scalar", True)).pack(pady=5)
            tk.Button(operation_window, text="Dzielenie (z wysyceniem)", command=lambda: perform_scalar_operation("divide_scalar", True)).pack(pady=5)

        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać operacje punktowe.")

    def logical_operations(self, parent):
        """Realizuje operacje logiczne na obrazach monochromatycznych i binarnych."""
        if parent.loaded_image_data:
            img1 = np.array(parent.loaded_image_data[2].convert("L"))

            def load_second_image():
                """Load a second image for two-operand operations."""
                file_path = filedialog.askopenfilename(
                    filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
                )
                if file_path:
                    try:
                        img2 = np.array(Image.open(file_path).convert("L"))
                        if img1.shape != img2.shape:
                            messagebox.showerror("Błąd", "Obrazy muszą mieć takie same rozmiary.")
                            return None
                        return img2
                    except Exception as e:
                        messagebox.showerror("Błąd", f"Nie udało się wczytać obrazu: {e}")
                        return None

            def validate_and_convert_to_binary(img):
                """Convert a grayscale image to binary."""
                return (img > 127).astype(np.uint8) * 255

            def validate_and_convert_to_grayscale(img):
                """Convert a binary mask to an 8-bit grayscale mask."""
                return (img > 0).astype(np.uint8) * 255

            def validate_images_and_perform(operation, img2=None):
                """Validate images and perform the logical operation."""
                try:
                    if img2 is not None and img1.shape != img2.shape:
                        raise ValueError("Obrazy muszą mieć takie same rozmiary.")

                    # Convert images to binary for logical operations
                    binary1 = validate_and_convert_to_binary(img1)
                    binary2 = validate_and_convert_to_binary(img2) if img2 is not None else None

                    # Perform logical operations
                    if operation == "not":
                        result = cv2.bitwise_not(binary1)
                    elif operation == "and":
                        result = cv2.bitwise_and(binary1, binary2)
                    elif operation == "or":
                        result = cv2.bitwise_or(binary1, binary2)
                    elif operation == "xor":
                        result = cv2.bitwise_xor(binary1, binary2)
                    else:
                        raise ValueError("Nieznana operacja logiczna.")

                    return result.astype(np.uint8)
                except Exception as e:
                    messagebox.showerror("Błąd", f"Operacja logiczna nie powiodła się: {e}")
                    return None

            def perform_operation_with_second_image(operation):
                """Load a second image and perform the logical operation."""
                img2 = load_second_image()
                if img2 is None:
                    return
                result = validate_images_and_perform(operation, img2=img2)
                if result is not None:
                    result_image = Image.fromarray(result)
                    parent.display_image(result_image, f"{operation.upper()}")

            def perform_not_operation():
                """Perform the NOT operation."""
                result = validate_images_and_perform("not")
                if result is not None:
                    result_image = Image.fromarray(result)
                    parent.display_image(result_image, "NOT")

            def toggle_image_type():
                """Convert between binary and grayscale masks."""
                toggle_window = Toplevel(parent)
                toggle_window.title("Konwersja Maska-Binary")

                tk.Label(toggle_window, text="Wybierz kierunek konwersji:", font=("Arial", 10)).pack(pady=5)

                def convert_to_binary():
                    binary_img = validate_and_convert_to_binary(img1)
                    result_image = Image.fromarray(binary_img)
                    parent.display_image(result_image, "Binary Mask")
                    toggle_window.destroy()

                def convert_to_grayscale():
                    grayscale_img = validate_and_convert_to_grayscale(img1)
                    result_image = Image.fromarray(grayscale_img)
                    parent.display_image(result_image, "Grayscale Mask")
                    toggle_window.destroy()

                tk.Button(toggle_window, text="Do binarnej (Binary)", command=convert_to_binary).pack(pady=5)
                tk.Button(toggle_window, text="Do szarości (Grayscale)", command=convert_to_grayscale).pack(pady=5)

            # Create a window for logical operations
            operation_window = Toplevel(parent)
            operation_window.title("Operacje Logiczne")

            # Add NOT operation
            tk.Label(operation_window, text="Operacje na jednym obrazie:", font=("Arial", 12)).pack(pady=5)
            tk.Button(operation_window, text="NOT", command=perform_not_operation).pack(pady=5)
            tk.Button(operation_window, text="Konwersja Maska <-> 8 bitów", command=toggle_image_type).pack(pady=5)

            # Add operations with two images
            tk.Label(operation_window, text="Operacje na dwóch obrazach:", font=("Arial", 12)).pack(pady=5)
            tk.Button(operation_window, text="AND", command=lambda: perform_operation_with_second_image("and")).pack(
                pady=5)
            tk.Button(operation_window, text="OR", command=lambda: perform_operation_with_second_image("or")).pack(
                pady=5)
            tk.Button(operation_window, text="XOR", command=lambda: perform_operation_with_second_image("xor")).pack(
                pady=5)
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać operacje logiczne.")



    def apply_histogram_stretch(self, parent):
        """Stosuje rozciąganie histogramu na obrazie w odcieniach szarości."""
        if not parent.loaded_image_data:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        img = np.array(parent.loaded_image_data[2])  # Pobieramy obraz źródłowy
        if len(img.shape) != 2:  # Upewniamy się, że obraz jest w odcieniach szarości
            messagebox.showerror("Błąd", "Rozciąganie histogramu działa tylko dla obrazów w odcieniach szarości.")
            return

        def on_submit():
            try:
                p1 = int(p1_entry.get())
                p2 = int(p2_entry.get())
                q3 = int(q3_entry.get())
                q4 = int(q4_entry.get())

                if not (0 <= p1 <= 255 and 0 <= p2 <= 255 and 0 <= q3 <= 255 and 0 <= q4 <= 255):
                    raise ValueError("Wszystkie wartości muszą być w przedziale 0-255.")
                if p1 >= p2 or q3 >= q4:
                    raise ValueError("Warunek: p1 < p2 oraz q3 < q4 musi być spełniony.")

                result_img = stretch_histogram(img, p1, p2, q3, q4)

                # Wyświetlamy wynikowy obraz w nowej zakładce
                result_pil = Image.fromarray(result_img)
                parent.display_image(result_pil, f"Rozciąganie ({p1}-{p2}) → ({q3}-{q4})")

                input_window.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

        # Tworzenie okna dialogowego
        input_window = Toplevel(parent)
        input_window.title("Rozciąganie histogramu")

        tk.Label(input_window, text="Zakres wejściowy (p1 - p2):", font=("Arial", 10)).pack(pady=5)
        p1_entry = tk.Entry(input_window)
        p1_entry.pack(pady=2)
        p1_entry.insert(0, "0")  # Domyślna wartość p1
        p2_entry = tk.Entry(input_window)
        p2_entry.pack(pady=2)
        p2_entry.insert(0, "255")  # Domyślna wartość p2

        tk.Label(input_window, text="Zakres wyjściowy (q3 - q4):", font=("Arial", 10)).pack(pady=5)
        q3_entry = tk.Entry(input_window)
        q3_entry.pack(pady=2)
        q3_entry.insert(0, "0")  # Domyślna wartość q3
        q4_entry = tk.Entry(input_window)
        q4_entry.pack(pady=2)
        q4_entry.insert(0, "255")  # Domyślna wartość q4

        tk.Button(input_window, text="Zastosuj", command=on_submit).pack(pady=10)