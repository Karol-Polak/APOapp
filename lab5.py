import tkinter as tk
import numpy as np
import cv2
from PIL import Image
from tkinter import messagebox, Toplevel

class MenuBarLab5(tk.Menu):
    """Menu 'Laboratorium 5' zawierające opcje segmentacji obrazów."""

    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=False)
        self.parent = parent
        self.add_command(label="Progowanie z dwoma progami", command=lambda: self.double_threshold(parent))
        self.add_command(label="Progowanie metodą Otsu", command=lambda: self.otsu_threshold(parent))
        self.add_command(label="Progowanie adaptacyjne", command=lambda: self.adaptive_threshold(parent))
        self.add_command(label="Szkieletyzacja obiektu", command=lambda: self.skeletonize(parent))
        self.add_command(label="Operacje morfologiczne", command=lambda: self.morphology_operations(parent))

    def double_threshold(self, parent):
        """Segmentacja obrazu metodą progowania z dwoma progami."""
        if parent.loaded_image_data:
            # Zapytaj użytkownika o progi
            thresholds_window = Toplevel(parent)
            thresholds_window.title("Wybierz progi")

            tk.Label(thresholds_window, text="Dolny próg:").grid(row=0, column=0)
            tk.Label(thresholds_window, text="Górny próg:").grid(row=1, column=0)

            lower_entry = tk.Entry(thresholds_window)
            upper_entry = tk.Entry(thresholds_window)
            lower_entry.grid(row=0, column=1)
            upper_entry.grid(row=1, column=1)

            def apply_threshold():
                try:
                    lower = int(lower_entry.get())
                    upper = int(upper_entry.get())

                    if 0 <= lower <= 255 and 0 <= upper <= 255 and lower < upper:
                        img_array = np.array(parent.loaded_image_data[2].convert("L"))
                        segmented = np.where((img_array >= lower) & (img_array <= upper), 255, 0).astype(np.uint8)
                        new_image = Image.fromarray(segmented)
                        parent.display_image(new_image, "Progowanie 2 progi")
                        thresholds_window.destroy()
                    else:
                        messagebox.showerror("Błąd", "Progi muszą być w zakresie 0-255 i dolny próg < górny próg.")
                except ValueError:
                    messagebox.showerror("Błąd", "Progi muszą być liczbami całkowitymi.")

            tk.Button(thresholds_window, text="Zastosuj", command=apply_threshold).grid(row=2, columnspan=2)
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać progowanie.")

    def otsu_threshold(self, parent):
        """Segmentacja obrazu metodą progowania Otsu."""
        if parent.loaded_image_data:
            img_array = np.array(parent.loaded_image_data[2].convert("L"))
            # Obliczenie progu metodą Otsu
            histogram, bin_edges = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
            total_pixels = img_array.size
            current_max, threshold = 0, 0
            sum_total = np.sum(bin_edges[:-1] * histogram)
            sum_background, weight_background = 0, 0

            for i in range(256):
                weight_background += histogram[i]
                if weight_background == 0:
                    continue
                weight_foreground = total_pixels - weight_background
                if weight_foreground == 0:
                    break
                sum_background += i * histogram[i]
                mean_background = sum_background / weight_background
                mean_foreground = (sum_total - sum_background) / weight_foreground
                between_class_variance = weight_background * weight_foreground * (
                            mean_background - mean_foreground) ** 2
                if between_class_variance > current_max:
                    current_max = between_class_variance
                    threshold = i

            segmented = np.where(img_array > threshold, 255, 0).astype(np.uint8)
            new_image = Image.fromarray(segmented)
            parent.display_image(new_image, "Progowanie Otsu")
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać progowanie.")

    def adaptive_threshold(self, parent):
        """Segmentacja obrazu metodą progowania adaptacyjnego."""
        if parent.loaded_image_data:
            img_array = np.array(parent.loaded_image_data[2].convert("L"))

            def adaptive_method(block_size, c_value):
                padded = np.pad(img_array, pad_width=block_size // 2, mode='constant', constant_values=255)
                adaptive_result = np.zeros_like(img_array)
                for i in range(img_array.shape[0]):
                    for j in range(img_array.shape[1]):
                        local_region = padded[i:i + block_size, j:j + block_size]
                        local_threshold = local_region.mean() - c_value
                        adaptive_result[i, j] = 255 if img_array[i, j] > local_threshold else 0
                return adaptive_result

            # Okno wyboru parametrów
            adaptive_window = Toplevel(parent)
            adaptive_window.title("Parametry adaptacyjne")

            tk.Label(adaptive_window, text="Rozmiar bloku:").grid(row=0, column=0)
            tk.Label(adaptive_window, text="Stała C:").grid(row=1, column=0)

            block_entry = tk.Entry(adaptive_window)
            block_entry.grid(row=0, column=1)
            block_entry.insert(0, "15")  # Domyślny rozmiar bloku

            c_entry = tk.Entry(adaptive_window)
            c_entry.grid(row=1, column=1)
            c_entry.insert(0, "10")  # Domyślna wartość C

            def apply_adaptive_threshold():
                try:
                    block_size = int(block_entry.get())
                    c_value = float(c_entry.get())

                    if block_size % 2 == 0 or block_size < 3:
                        messagebox.showerror("Błąd", "Rozmiar bloku musi być nieparzysty i >= 3.")
                        return

                    segmented = adaptive_method(block_size, c_value)
                    new_image = Image.fromarray(segmented.astype(np.uint8))
                    parent.display_image(new_image, "Progowanie Adaptacyjne")
                    adaptive_window.destroy()
                except ValueError:
                    messagebox.showerror("Błąd", "Wprowadź poprawne liczby.")

            tk.Button(adaptive_window, text="Zastosuj", command=apply_adaptive_threshold).grid(row=2, columnspan=2)
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać progowanie.")

    def skeletonize(self, parent):
        """Szkieletyzacja obiektu na mapie binarnej."""
        if parent.loaded_image_data:
            img_array = np.array(parent.loaded_image_data[2].convert("L"))

            # Ensure the input image is binary
            binary_map = np.where(img_array > 127, 255, 0).astype(np.uint8)

            def skeletonize_image(binary_image):
                """Perform skeletonization using OpenCV."""
                skeleton = np.zeros_like(binary_image)
                element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
                temp = np.zeros_like(binary_image)

                while True:
                    eroded = cv2.erode(binary_image, element)
                    opened = cv2.dilate(eroded, element)
                    temp = cv2.subtract(binary_image, opened)
                    skeleton = cv2.bitwise_or(skeleton, temp)
                    binary_image = eroded.copy()
                    if cv2.countNonZero(binary_image) == 0:
                        break
                return skeleton

            try:
                skeleton = skeletonize_image(binary_map)
                new_image = Image.fromarray(skeleton)
                parent.display_image(new_image, "Szkieletyzacja")
            except Exception as e:
                messagebox.showerror(
                    "Błąd",
                    f"Podczas szkieletyzacji wystąpił błąd:\n{e}"
                )
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać szkieletyzację.")

    def morphology_operations(self, parent):
        """Podstawowe operacje morfologiczne: erozja, dylacja, otwarcie, zamknięcie."""
        if parent.loaded_image_data:
            img_array = np.array(parent.loaded_image_data[2].convert("L"))

            # Ensure the input image is binary
            binary_map = np.where(img_array > 127, 255, 0).astype(np.uint8)

            def apply_morphology(operation, kernel_shape, iterations):
                """Apply the chosen morphological operation with the given kernel shape and iterations."""
                if kernel_shape == "cross":
                    struct_elem = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
                elif kernel_shape == "rectangle":
                    struct_elem = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                else:
                    raise ValueError("Unsupported kernel shape")

                if operation == "erosion":
                    result = cv2.erode(binary_map, struct_elem, iterations=iterations)
                elif operation == "dilation":
                    result = cv2.dilate(binary_map, struct_elem, iterations=iterations)
                elif operation == "opening":
                    result = cv2.morphologyEx(binary_map, cv2.MORPH_OPEN, struct_elem, iterations=iterations)
                elif operation == "closing":
                    result = cv2.morphologyEx(binary_map, cv2.MORPH_CLOSE, struct_elem, iterations=iterations)
                else:
                    raise ValueError("Unsupported operation")

                return result

            def show_result(operation, kernel_shape):
                """Perform and display the morphological operation with user-specified iterations."""
                try:
                    iterations = int(iterations_entry.get())
                    if iterations < 1:
                        raise ValueError("Number of iterations must be at least 1.")

                    result = apply_morphology(operation, kernel_shape, iterations)
                    operation_name = f"{operation.capitalize()} ({kernel_shape}, {iterations}x)"
                    new_image = Image.fromarray(result)
                    parent.display_image(new_image, operation_name)
                except ValueError as ve:
                    messagebox.showerror("Błąd", f"Niepoprawna wartość iteracji: {ve}")
                except Exception as e:
                    messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

            # Create a new window for selecting operations
            morph_window = Toplevel(parent)
            morph_window.title("Operacje morfologiczne")

            # Iterations entry
            tk.Label(morph_window, text="Liczba iteracji:", font=("Arial", 10)).pack(pady=5)
            iterations_entry = tk.Entry(morph_window)
            iterations_entry.pack(pady=5)
            iterations_entry.insert(0, "1")  # Default iterations

            # Buttons for operations and kernel shapes
            tk.Label(morph_window, text="Wybierz operację i kształt elementu strukturalnego:", font=("Arial", 12)).pack(pady=10)
            for operation in ["erosion", "dilation", "opening", "closing"]:
                frame = tk.Frame(morph_window)
                frame.pack(pady=5)
                tk.Label(frame, text=operation.capitalize(), width=12).pack(side="left")
                tk.Button(frame, text="Krzyż", command=lambda op=operation, ks="cross": show_result(op, ks)).pack(side="left", padx=5)
                tk.Button(frame, text="Prostokąt", command=lambda op=operation, ks="rectangle": show_result(op, ks)).pack(side="left", padx=5)
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać operacje morfologiczne.")
