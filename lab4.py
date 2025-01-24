import tkinter as tk
import numpy as np
import cv2
from PIL import Image
from tkinter import messagebox, Toplevel

class MenuBarLab4(tk.Menu):
    """Menu 'Laboratorium 4' zawierające opcje detekcji krawędzi."""

    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=False)
        self.parent = parent
        self.add_command(label="Operacje przetwarzania obrazu", command=lambda: self.image_processing_operations(parent))
        self.add_command(label="Filtr medianowy", command=lambda: self.median_filter(parent))
        self.add_command(label="Detekcja krawędzi (Canny)", command=lambda: self.canny_edge_detection(parent))

    def image_processing_operations(self, parent):
        """Realizuje operacje wygładzania, wyostrzania i detekcji krawędzi."""
        if parent.loaded_image_data:
            img_array = np.array(parent.loaded_image_data[2].convert("L"))  # Convert to grayscale

            def apply_filter(kernel, border_type, constant_value=0):
                """Apply the chosen filter to the image with the specified border handling."""
                if border_type == "BORDER_CONSTANT":
                    result = cv2.filter2D(img_array, -1, kernel, borderType=cv2.BORDER_CONSTANT)
                    result = cv2.copyMakeBorder(result, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=constant_value)
                elif border_type == "BORDER_REFLECT":
                    result = cv2.filter2D(img_array, -1, kernel, borderType=cv2.BORDER_REFLECT)
                else:
                    raise ValueError("Nieznany typ wypełnienia brzegów.")
                return result

            def choose_border_type_and_apply(kernel):
                """Open a window for the user to choose the border handling method."""
                border_window = Toplevel(parent)
                border_window.title("Wybierz typ wypełnienia marginesów")

                tk.Label(border_window, text="Typ wypełnienia brzegów:", font=("Arial", 10)).pack(pady=5)
                border_type = tk.StringVar(value="BORDER_CONSTANT")

                tk.Radiobutton(border_window, text="Stała wartość (BORDER_CONSTANT)", variable=border_type,
                               value="BORDER_CONSTANT").pack()
                tk.Radiobutton(border_window, text="Odbicie (BORDER_REFLECT)", variable=border_type,
                               value="BORDER_REFLECT").pack()

                tk.Label(border_window, text="Stała wartość (tylko dla BORDER_CONSTANT):", font=("Arial", 10)).pack(
                    pady=5)
                constant_value_entry = tk.Entry(border_window)
                constant_value_entry.pack()
                constant_value_entry.insert(0, "0")

                def apply():
                    border = border_type.get()
                    try:
                        constant_value = int(constant_value_entry.get())
                        result = apply_filter(kernel, border, constant_value)
                        if result is not None:
                            result_image = Image.fromarray(result)
                            parent.display_image(result_image, f"Filtered Image")
                        border_window.destroy()
                    except ValueError:
                        messagebox.showerror("Błąd", "Wartość stała musi być liczbą całkowitą.")

                tk.Button(border_window, text="Zastosuj", command=apply).pack(pady=10)

            def smoothing_operations():
                """Perform smoothing using different kernels."""
                kernel_window = Toplevel(parent)
                kernel_window.title("Wybierz maskę wygładzania")

                tk.Label(kernel_window, text="Wygładzanie:", font=("Arial", 12)).pack(pady=5)

                def apply_smoothing(kernel):
                    choose_border_type_and_apply(kernel)

                # Kernels for smoothing
                mean_kernel = np.ones((3, 3), np.float32) / 9
                weighted_mean_kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float32) / 16
                gaussian_kernel = cv2.getGaussianKernel(3, 0.8)
                gaussian_kernel = gaussian_kernel * gaussian_kernel.T

                tk.Button(kernel_window, text="Uśrednienie", command=lambda: apply_smoothing(mean_kernel)).pack(pady=5)
                tk.Button(kernel_window, text="Uśrednienie z wagami",
                          command=lambda: apply_smoothing(weighted_mean_kernel)).pack(pady=5)
                tk.Button(kernel_window, text="Filtr Gaussowski",
                          command=lambda: apply_smoothing(gaussian_kernel)).pack(pady=5)

            def sharpening_operations():
                """Perform sharpening using Laplacian masks."""
                kernel_window = Toplevel(parent)
                kernel_window.title("Wybierz maskę wyostrzania")

                tk.Label(kernel_window, text="Wyostrzanie (Laplasjan):", font=("Arial", 12)).pack(pady=5)

                def apply_sharpening(kernel):
                    choose_border_type_and_apply(kernel)

                # Laplacian kernels
                laplacian_1 = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
                laplacian_2 = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], dtype=np.float32)
                laplacian_3 = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=np.float32)

                tk.Button(kernel_window, text="Laplasjan 1 [0, 1, 0]", command=lambda: apply_sharpening(laplacian_1)).pack(pady=5)
                tk.Button(kernel_window, text="Laplasjan 2 [1, 1, 1]", command=lambda: apply_sharpening(laplacian_2)).pack(pady=5)
                tk.Button(kernel_window, text="Laplasjan 3 [0, -1, 0]", command=lambda: apply_sharpening(laplacian_3)).pack(pady=5)

            def edge_detection_operations():
                """Perform directional edge detection using Sobel masks."""
                kernel_window = Toplevel(parent)
                kernel_window.title("Wybierz kierunkową maskę Sobela")

                tk.Label(kernel_window, text="Detekcja krawędzi (Sobel):", font=("Arial", 12)).pack(pady=5)

                def apply_sobel(kernel):
                    choose_border_type_and_apply(kernel)

                # Sobel kernels for 8 directions
                sobel_kernels = {
                    "Północ": np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32),
                    "Wschód": np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32),
                    "Południe": np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float32),
                    "Zachód": np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]], dtype=np.float32),
                    "Północny Wschód": np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]], dtype=np.float32),
                    "Południowy Wschód": np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]], dtype=np.float32),
                    "Południowy Zachód": np.array([[0, -1, -2], [1, 0, -1], [2, 1, 0]], dtype=np.float32),
                    "Północny Zachód": np.array([[2, 1, 0], [1, 0, -1], [0, -1, -2]], dtype=np.float32),
                }

                for direction, kernel in sobel_kernels.items():
                    tk.Button(kernel_window, text=f"Kierunek {direction}",
                              command=lambda k=kernel: apply_sobel(k)).pack(pady=5)

            def prewitt_operations():
                """Perform edge detection using Prewitt masks."""
                prewitt_window = Toplevel(parent)
                prewitt_window.title("Detekcja krawędzi (Prewitt)")

                tk.Label(prewitt_window, text="Detekcja krawędzi (Prewitt):", font=("Arial", 12)).pack(pady=5)

                def apply_prewitt():
                    prewitt_x = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)
                    prewitt_y = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)
                    result_x = cv2.filter2D(img_array, -1, prewitt_x)
                    result_y = cv2.filter2D(img_array, -1, prewitt_y)
                    result = cv2.addWeighted(result_x, 0.5, result_y, 0.5, 0)
                    result_image = Image.fromarray(result)
                    parent.display_image(result_image, "Prewitt")

                tk.Button(prewitt_window, text="Detekcja Prewitta", command=apply_prewitt).pack(pady=5)

            # Main options
            operation_window = Toplevel(parent)
            operation_window.title("Operacje Przetwarzania Obrazu")

            tk.Button(operation_window, text="Wygładzanie", command=smoothing_operations).pack(pady=5)
            tk.Button(operation_window, text="Wyostrzanie", command=sharpening_operations).pack(pady=5)
            tk.Button(operation_window, text="Detekcja krawędzi (Sobel)", command=edge_detection_operations).pack(
                pady=5)
            tk.Button(operation_window, text="Detekcja krawędzi (Prewitt)", command=prewitt_operations).pack(pady=5)
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać operacje przetwarzania obrazu.")

    def median_filter(self, parent):
        """Realizuje filtrację medianową z wyborem otoczenia i sposobu uzupełniania brzegów."""
        if not parent.loaded_image_data:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        img_array = np.array(parent.loaded_image_data[2].convert("L"))  # Pobieramy obraz w skali szarości

        def apply_median_filter(kernel_size, border_type, constant_value=0):
            """Applies the median filter with specified kernel size and border type."""
            if border_type == "BORDER_CONSTANT":
                result = cv2.medianBlur(img_array, kernel_size)
                result = cv2.copyMakeBorder(result, kernel_size // 2, kernel_size // 2, kernel_size // 2,
                                            kernel_size // 2,
                                            cv2.BORDER_CONSTANT, value=constant_value)
            elif border_type == "BORDER_REFLECT":
                result = cv2.medianBlur(img_array, kernel_size)
            else:
                raise ValueError("Nieznany typ wypełnienia brzegów.")
            return result

        def choose_border_type_and_apply(kernel_size):
            """Opens a window for the user to choose the border handling method."""
            border_window = Toplevel(parent)
            border_window.title("Wybierz typ wypełnienia marginesów")

            tk.Label(border_window, text="Typ wypełnienia brzegów:", font=("Arial", 10)).pack(pady=5)
            border_type = tk.StringVar(value="BORDER_CONSTANT")

            tk.Radiobutton(border_window, text="Stała wartość (BORDER_CONSTANT)", variable=border_type,
                           value="BORDER_CONSTANT").pack()
            tk.Radiobutton(border_window, text="Odbicie (BORDER_REFLECT)", variable=border_type,
                           value="BORDER_REFLECT").pack()

            tk.Label(border_window, text="Stała wartość (tylko dla BORDER_CONSTANT):", font=("Arial", 10)).pack(pady=5)
            constant_value_entry = tk.Entry(border_window)
            constant_value_entry.pack()
            constant_value_entry.insert(0, "0")

            def apply():
                border = border_type.get()
                try:
                    constant_value = int(constant_value_entry.get())
                    result = apply_median_filter(kernel_size, border, constant_value)
                    if result is not None:
                        result_image = Image.fromarray(result)
                        parent.display_image(result_image, f"Median {kernel_size}x{kernel_size}")
                    border_window.destroy()
                except ValueError:
                    messagebox.showerror("Błąd", "Wartość stała musi być liczbą całkowitą.")

            tk.Button(border_window, text="Zastosuj", command=apply).pack(pady=10)

        def choose_kernel_size():
            """Opens a window to choose kernel size."""
            kernel_window = Toplevel(parent)
            kernel_window.title("Wybierz wielkość otoczenia")

            tk.Label(kernel_window, text="Wielkość otoczenia (3x3, 5x5, 7x7, 9x9):", font=("Arial", 12)).pack(pady=5)

            kernel_sizes = [3, 5, 7, 9]
            for size in kernel_sizes:
                tk.Button(kernel_window, text=f"{size}x{size}",
                          command=lambda s=size: choose_border_type_and_apply(s)).pack(pady=5)

        choose_kernel_size()

    def canny_edge_detection(self, parent):
        """Detekcja krawędzi operatorem Canny'ego."""
        if parent.loaded_image_data:
            img_array = np.array(parent.loaded_image_data[2].convert("L"))

            def apply_canny(threshold1, threshold2):
                """Apply Canny edge detection with specified thresholds."""
                edges = cv2.Canny(img_array, threshold1, threshold2)
                return edges

            def show_result():
                """Perform and display the Canny edge detection."""
                try:
                    t1 = int(threshold1_entry.get())
                    t2 = int(threshold2_entry.get())
                    if t1 < 0 or t2 < 0:
                        raise ValueError("Progi muszą być liczbami nieujemnymi.")
                    if t1 >= t2:
                        raise ValueError("Dolny próg musi być mniejszy niż górny próg.")

                    edges = apply_canny(t1, t2)
                    new_image = Image.fromarray(edges)
                    parent.display_image(new_image, f"Canny ({t1}, {t2})")
                except ValueError as ve:
                    messagebox.showerror("Błąd", f"Niepoprawne wartości progów: {ve}")
                except Exception as e:
                    messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

            # Create a new window for threshold input
            canny_window = Toplevel(parent)
            canny_window.title("Detekcja krawędzi - Canny")

            tk.Label(canny_window, text="Dolny próg (threshold1):", font=("Arial", 10)).grid(row=0, column=0, padx=5,
                                                                                             pady=5)
            threshold1_entry = tk.Entry(canny_window)
            threshold1_entry.grid(row=0, column=1, padx=5, pady=5)
            threshold1_entry.insert(0, "50")  # Default lower threshold

            tk.Label(canny_window, text="Górny próg (threshold2):", font=("Arial", 10)).grid(row=1, column=0, padx=5,
                                                                                             pady=5)
            threshold2_entry = tk.Entry(canny_window)
            threshold2_entry.grid(row=1, column=1, padx=5, pady=5)
            threshold2_entry.insert(0, "150")  # Default upper threshold

            tk.Button(canny_window, text="Zastosuj", command=show_result).grid(row=2, columnspan=2, pady=10)
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać detekcję krawędzi.")
