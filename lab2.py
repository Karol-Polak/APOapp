import tkinter as tk
import numpy as np
from tkinter import messagebox, Toplevel


def linear_stretch(img, with_clipping=False, clip_percent=5):
    """Liniowe rozciąganie histogramu z opcją przesycenia pikseli."""
    if len(img.shape) == 3:  # Obrazy kolorowe
        result = np.dstack([linear_stretch(img[:, :, i], with_clipping, clip_percent)[0] for i in range(3)])
        histograms = [np.histogram(result[:, :, i].flatten(), bins=256, range=(0, 256))[0] for i in range(3)]
        return result, histograms

    if with_clipping: #rozciąganie z przesyceniem
        p_low, p_high = np.percentile(img, [clip_percent, 100 - clip_percent])
        img = np.clip(img, p_low, p_high)
        min_val, max_val = p_low, p_high
    else:#rozciąganie bez przesycenia
        min_val, max_val = img.min(), img.max()

    #normalizacja wartości intensywności do zakresu [0-255]
    stretched_img = ((img - min_val) / (max_val - min_val) * 255).astype(np.uint8)
    histogram = np.histogram(stretched_img.flatten(), bins=256, range=(0, 256))[0]

    return stretched_img, histogram


def histogram_equalization(img):
    """Wyrównanie histogramu przez ewualizację."""
    if len(img.shape) == 3:  # Color image
        result = np.dstack([histogram_equalization(img[:, :, i])[0] for i in range(3)])
        histograms = [np.histogram(result[:, :, i].flatten(), bins=256, range=(0, 256))[0] for i in range(3)]
        return result, histograms

    #obliczanie histogramu i skumulowanej fukcji rozkładu
    hist, bins = np.histogram(img.flatten(), 256, [0, 256])
    cdf = hist.cumsum()  # Cumulative distribution function
    cdf_normalized = (cdf - cdf.min()) / (cdf.max() - cdf.min()) * 255
    cdf_normalized = cdf_normalized.astype(np.uint8)

    #mapowanie pikseli na nowy zakres
    equalized_img = cdf_normalized[img]
    histogram = np.histogram(equalized_img.flatten(), bins=256, range=(0, 256))[0]

    return equalized_img, histogram

def negate_image(img):
    """Neguje poziomy szarości w obrazie."""
    return 255 - img

def reduce_gray_levels(img, num_levels):
    """Redukuje liczbę poziomów szarości."""
    if num_levels < 2 or num_levels > 256:
        raise ValueError("Liczba poziomów szarości musi być w przedziale 2-256.")
    factor = 256 // num_levels
    return (img // factor) * factor

def binary_threshold(img, threshold):
    """Promowanie binarne z progiem."""
    return np.where(img >= threshold, 255, 0).astype(np.uint8)

def gray_level_threshold(img, threshold):
    """Progowanie z zachowaniem poziomów szarości."""
    return np.where(img >= threshold, img, 0).astype(np.uint8)


class MenuBarLab2(tk.Menu):
    """Menu 'Laboratorium 2' zawierające funkcje generowania histogramu z funkcją hover."""
    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=False)
        self.parent = parent
        self.add_command(label="Histogram (Obraz źródłowy)",
                         command=lambda: self.generate_histogram(parent, use_processed=False))
        self.add_command(label="Histogram (Obraz wynikowy)",
                         command=lambda: self.generate_histogram(parent, use_processed=True))
        self.add_command(label="Liniowe rozciąganie (bez przesycenia)",
                         command=lambda: self.apply_transformation(parent, "linear_stretch", False))
        self.add_command(label="Liniowe rozciąganie (z przesyceniem 5%)",
                         command=lambda: self.apply_transformation(parent, "linear_stretch", True))
        self.add_command(label="Wyrównanie histogramu",
                         command=lambda: self.apply_transformation(parent, "equalization"))
        self.add_command(label="Negacja", command=lambda: self.apply_point_operation(parent, "negate"))
        self.add_command(label="Redukcja poziomów szarości",
                         command=lambda: self.apply_point_operation_with_input(parent, "reduce_gray"))
        self.add_command(label="Promowanie binarne",
                         command=lambda: self.apply_point_operation_with_input(parent, "binary_threshold"))
        self.add_command(label="Progowanie z zachowaniem poziomów szarości",
                         command=lambda: self.apply_point_operation_with_input(parent, "gray_threshold"))

    def generate_histogram(self, parent, use_processed=False):
        """Generuje histogram dla obrazów binarnych, szarych lub RGB."""
        if use_processed:
            if parent.processed_image_data:
                img = np.array(parent.processed_image_data[2])  # Obraz wynikowy
                print("processed image")
            else:
                messagebox.showwarning("Brak obrazu wynikowego", "Najpierw wykonaj operację przekształcenia.")
                return
        elif parent.loaded_image_data:
            img = np.array(parent.loaded_image_data[2])  # Obraz źródłowy
            print("loadaed image")
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wygenerować histogram.")
            return

        # Analizujemy format obrazu i generujemy odpowiedni histogram
        if len(img.shape) == 2:  # Grayscale or binary image
            unique_values = np.unique(img)
            if set(unique_values).issubset({0, 255}):  # Binary image
                self.generate_binary_histogram(img, parent)
            else:  # Grayscale image
                self.generate_grayscale_histogram(img, parent)
        elif len(img.shape) == 3:  # RGB image
            if img.shape[2] == 3:  # RGB
                self.generate_rgb_histogram(img, parent)
            elif img.shape[2] == 4:  # RGBA
                self.generate_rgb_histogram(img[:, :, :3], parent)
        else:
            messagebox.showerror("Błąd", "Nieobsługiwany format obrazu.")

    def add_hover_feature(self, canvas, figure, ax, bars):
        """Dodaje funkcję hover (wyświetlanie wartości słupków po najechaniu na wykresie słupokowym)"""
        hover_label = tk.Label(canvas.get_tk_widget().master, text="", font=("Arial", 10), fg="red")
        hover_label.pack()

        annotation = ax.annotate("", xy=(0, 0), xytext=(0, 0), textcoords="offset points",
                                 ha="center", va="bottom", fontsize=8, color="red")

        def on_hover(event):
            """Obsługa zdarzenia hover nad słupkami histogramu"""
            if event.inaxes == ax:
                for bar in bars:
                    if bar.contains(event)[0]:
                        x_value = int(bar.get_x() + 0.5)  # Pixel value
                        y_value = int(bar.get_height())   # Count
                        annotation.set_position((bar.get_x() + bar.get_width() / 2, y_value))
                        annotation.set_text(f"{y_value}")
                        annotation.set_visible(True)
                        canvas.draw()
                        hover_label.config(text=f"Intensywność: {x_value}, Wartość: {y_value}")
                        return
            annotation.set_visible(False)
            canvas.draw()
            hover_label.config(text="")

        canvas.mpl_connect("motion_notify_event", on_hover)

    def add_statistics_to_histogram(self, statistics, parent):
        """Dodaje statystyki obrazu do okna histogramu, wyśrodkowane w układzie."""
        # Tworzenie ramki na statystyki
        stats_frame = tk.Frame(parent)
        stats_frame.pack(side="bottom", fill="x", pady=10)

        # Nagłówek statystyk
        tk.Label(stats_frame, text="Statystyki Obrazu", font=("Arial", 12, "bold"), anchor="center").pack(pady=5)

        # Dodawanie każdej statystyki w nowym wierszu, wyśrodkowane
        for key, value in statistics.items():
            stat_label = tk.Label(stats_frame, text=f"{key}: {value}", font=("Arial", 11, "bold"))
            stat_label.pack(anchor="center")  # Wyśrodkowanie etykiety


    def generate_binary_histogram(self, img, parent):
        """Generuje histogram dla obrazów binarnych."""
        histogram = np.histogram(img, bins=[0, 1, 256])[0]

        histogram_window = Toplevel(parent)
        histogram_window.title("Histogram Obrazu Binarnego")

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        figure = Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)

        bars = ax.bar(["0 (Czarny)", "255 (Biały)"], histogram, color=["black", "white"], edgecolor="black")
        ax.set_title("Histogram Obrazu Binarnego")
        ax.set_xlabel("Wartość pikseli")
        ax.set_ylabel("Liczba pikseli")

        canvas = FigureCanvasTkAgg(figure, histogram_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.add_hover_feature(canvas, figure, ax, bars)
        canvas.draw()

        statistics = {
            "Czarny (0)": histogram[0],
            "Biały (255)": histogram[1],
            "Liczba pikseli": histogram.sum()
        }
        self.add_statistics_to_histogram(statistics, histogram_window)

    def generate_grayscale_histogram(self, img, parent):
        """Generuje histogram dla obrazów w odcieniach szarości."""
        histogram, _ = np.histogram(img.flatten(), bins=256, range=(0, 256))

        histogram_window = Toplevel(parent)
        histogram_window.title("Histogram Obrazu Szarego")

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        figure = Figure(figsize=(8, 4), dpi=100)
        ax = figure.add_subplot(111)

        bars = ax.bar(range(256), histogram, color="gray", edgecolor="black", width=1.0)
        ax.set_title("Histogram Obrazu w Odcieniach Szarości")
        ax.set_xlabel("Wartość pikseli (0-255)")
        ax.set_ylabel("Liczba pikseli")

        canvas = FigureCanvasTkAgg(figure, histogram_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.add_hover_feature(canvas, figure, ax, bars)
        canvas.draw()

        statistics = {
            "Średnia": round(np.mean(img), 2),
            "Mediana": int(np.median(img)),
            "Wariancja": round(np.var(img), 2),
            "Odchylenie standardowe": round(np.std(img), 2),
            "Liczba pikseli": img.size
        }
        self.add_statistics_to_histogram(statistics, histogram_window)

    def generate_rgb_histogram(self, img, parent):
        """Generuje histogram RGB z możliwością wyboru kanałów."""
        histograms = {
            "Red": np.histogram(img[:, :, 0].flatten(), bins=256, range=(0, 256))[0],
            "Green": np.histogram(img[:, :, 1].flatten(), bins=256, range=(0, 256))[0],
            "Blue": np.histogram(img[:, :, 2].flatten(), bins=256, range=(0, 256))[0],
        }

        histogram_window = Toplevel(parent)
        histogram_window.title("Histogram RGB")

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        figure = Figure(figsize=(8, 4), dpi=100)
        ax = figure.add_subplot(111)
        bars = []

        def update_histogram():
            ax.clear()
            bars.clear()
            if red_var.get():
                bars.extend(ax.bar(range(256), histograms["Red"], color="red", alpha=0.5, label="Red", width=1.0))
            if green_var.get():
                bars.extend(ax.bar(range(256), histograms["Green"], color="green", alpha=0.5, label="Green", width=1.0))
            if blue_var.get():
                bars.extend(ax.bar(range(256), histograms["Blue"], color="blue", alpha=0.5, label="Blue", width=1.0))
            ax.legend()
            canvas.draw()

        red_var, green_var, blue_var = tk.BooleanVar(value=True), tk.BooleanVar(value=True), tk.BooleanVar(value=True)
        control_frame = tk.Frame(histogram_window)
        control_frame.pack()
        tk.Checkbutton(control_frame, text="Red", variable=red_var, command=update_histogram).pack(side="left")
        tk.Checkbutton(control_frame, text="Green", variable=green_var, command=update_histogram).pack(side="left")
        tk.Checkbutton(control_frame, text="Blue", variable=blue_var, command=update_histogram).pack(side="left")

        canvas = FigureCanvasTkAgg(figure, histogram_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        update_histogram()
        self.add_hover_feature(canvas, figure, ax, bars)

        statistics = {
            "Średnia R": round(np.mean(img[:, :, 0]), 2),
            "Średnia G": round(np.mean(img[:, :, 1]), 2),
            "Średnia B": round(np.mean(img[:, :, 2]), 2),
            "Mediana R": int(np.median(img[:, :, 0])),
            "Mediana G": int(np.median(img[:, :, 1])),
            "Mediana B": int(np.median(img[:, :, 2])),
            "Liczba pikseli": img[:, :, 0].size,
            "Średnia": round(np.mean(img), 2),
            "Mediana": int(np.median(img)),
            "Wariancja": round(np.var(img), 2),
            "Odchylenie standardowe": round(np.std(img), 2),
        }
        self.add_statistics_to_histogram(statistics, histogram_window)

    def apply_transformation(self, parent, method, *args):
        """Stosuje wybraną transformację histogramu."""
        if not parent.loaded_image_data:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        img = np.array(parent.loaded_image_data[2])  # Załaduj obraz jako macierz NumPy

        if method == "linear_stretch":
            result_img, result_hist = linear_stretch(img, *args)
        elif method == "equalization":
            result_img, result_hist = histogram_equalization(img)
        else:
            messagebox.showerror("Błąd", "Nieznana metoda przekształcenia.")
            return

        # Zapisujemy wynikowy obraz w processed_image_data
        from PIL import Image
        result_pil = Image.fromarray(result_img)
        parent.processed_image_data = [None, None, result_pil]  # Aktualizuj processed_image_data

        # Wyświetlamy wynikowy obraz w nowej zakładce
        parent.display_image(result_pil, f"Histogram ({method})")

        # Wyświetlamy histogram wynikowy
        self.display_result_histogram(result_hist, parent)

    def display_result_histogram(self, hist, parent):
        """Wyświetla histogram wynikowy."""
        histogram_window = Toplevel(parent)
        histogram_window.title("Wynikowy Histogram")

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        figure = Figure(figsize=(8, 4), dpi=100)
        ax = figure.add_subplot(111)

        # Jeśli histogram RGB
        if isinstance(hist, list):  # RGB image
            colors = ['red', 'green', 'blue']
            for h, color in zip(hist, colors):
                ax.bar(range(256), h, color=color, alpha=0.5, label=color.capitalize())
            ax.legend()
        else:  # Grayscale image
            ax.bar(range(256), hist, color="gray", edgecolor="black", width=1.0)

        ax.set_title("Histogram Wynikowy")
        ax.set_xlabel("Wartość pikseli (0-255)")
        ax.set_ylabel("Liczba pikseli")

        canvas = FigureCanvasTkAgg(figure, histogram_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
    # def display_result_histogram(self, hist, parent):
    #     """Wyświetla histogram wynikowy jako wykres słupkowy z przezroczystością."""
    #     histogram_window = Toplevel(parent)
    #     histogram_window.title("Wynikowy Histogram")
    #
    #     from matplotlib.figure import Figure
    #     from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    #
    #     figure = Figure(figsize=(8, 4), dpi=100)
    #     ax = figure.add_subplot(111)
    #
    #     # Dane dla kanałów RGB
    #     if isinstance(hist, list):  # Jeśli obraz RGB
    #         colors = ['red', 'green', 'blue']
    #         labels = ['Red', 'Green', 'Blue']
    #         bars = []
    #
    #         def update_histogram():
    #             """Aktualizuje histogram na podstawie aktywnych kanałów."""
    #             ax.clear()
    #             bars.clear()
    #
    #             for i, (h, color, label, var) in enumerate(zip(hist, colors, labels, [red_var, green_var, blue_var])):
    #                 if var.get():
    #                     bars.extend(ax.bar(range(256), h, color=color, alpha=0.5, label=label, width=1.0))
    #
    #             ax.legend()
    #             ax.set_title("Histogram Wynikowy")
    #             ax.set_xlabel("Wartość pikseli (0-255)")
    #             ax.set_ylabel("Liczba pikseli")
    #             canvas.draw()
    #
    #         # Tworzenie kontrolek do włączania i wyłączania kanałów
    #         red_var, green_var, blue_var = tk.BooleanVar(value=True), tk.BooleanVar(value=True), tk.BooleanVar(
    #             value=True)
    #         control_frame = tk.Frame(histogram_window)
    #         control_frame.pack()
    #         tk.Checkbutton(control_frame, text="Red", variable=red_var, command=update_histogram).pack(side="left")
    #         tk.Checkbutton(control_frame, text="Green", variable=green_var, command=update_histogram).pack(side="left")
    #         tk.Checkbutton(control_frame, text="Blue", variable=blue_var, command=update_histogram).pack(side="left")
    #
    #     else:  # Dla obrazów monochromatycznych
    #         ax.bar(range(256), hist, color="gray", edgecolor="black", width=1.0)
    #         ax.set_title("Histogram Wynikowy")
    #         ax.set_xlabel("Wartość pikseli (0-255)")
    #         ax.set_ylabel("Liczba pikseli")
    #
    #     canvas = FigureCanvasTkAgg(figure, histogram_window)
    #     canvas.get_tk_widget().pack(fill="both", expand=True)
    #
    #     if isinstance(hist, list):  # Aktualizacja tylko dla obrazów RGB
    #         update_histogram()
    #     else:
    #         canvas.draw()

    """Zadanie 2 kolejne operacje"""



    def apply_point_operation(self, parent, operation):
        """Stosuje jednoargumentową operację punktową na obrazie."""
        if not parent.loaded_image_data:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        img = np.array(parent.loaded_image_data[2])

        if len(img.shape) != 2:
            messagebox.showerror("Błąd", "Operacje punktowe są dostępne tylko dla obrazów w odcieniach szarości.")
            return

        if operation == "negate":
            result_img = negate_image(img)
        else:
            messagebox.showerror("Błąd", f"Nieznana operacja: {operation}")
            return

        # aktualizacja processed_image_data
        from PIL import Image
        result_pil = Image.fromarray(result_img)
        parent.processed_image_data = [None, None, result_pil]

        # Wyświetl wynikowy obraz w nowej karcie
        parent.display_image(result_pil, f"Operacja ({operation})")

    def apply_point_operation_with_input(self, parent, operation):
        """Stosuje operację punktową, wymagającą dodatkowego parametru od użytkownika."""
        if not parent.loaded_image_data:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return

        img = np.array(parent.loaded_image_data[2])

        if len(img.shape) != 2:
            messagebox.showerror("Błąd", "Operacje punktowe są dostępne tylko dla obrazów w odcieniach szarości.")
            return

        def on_submit():
            try:
                param = int(entry.get())
                if operation == "reduce_gray":
                    result_img = reduce_gray_levels(img, param)
                elif operation == "binary_threshold":
                    result_img = binary_threshold(img, param)
                elif operation == "gray_threshold":
                    result_img = gray_level_threshold(img, param)
                else:
                    messagebox.showerror("Błąd", f"Nieznana operacja: {operation}")
                    return

                # Wyświetl wynikowy obraz w nowej zakładce
                from PIL import Image
                result_pil = Image.fromarray(result_img)
                parent.display_image(result_pil, f"Operacja ({operation})")

                input_window.destroy()
            except Exception as e:
                messagebox.showerror("Błąd", str(e))

        # Tworzenie okna wejściowego dla użytkownika
        input_window = Toplevel(parent)
        input_window.title(f"Parametr dla {operation}")
        tk.Label(input_window, text="Podaj wartość:").pack(pady=5)
        entry = tk.Entry(input_window)
        entry.pack(pady=5)
        tk.Button(input_window, text="OK", command=on_submit).pack(pady=5)