import tkinter as tk
import numpy as np
import cv2
import pandas as pd
from PIL import Image
from tkinter import messagebox, Toplevel, filedialog

class MenuBarLab6(tk.Menu):
    """Menu 'Laboratorium 6' zawierające funkcje wyznaczania cech obiektów binarnych."""
    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=False)
        self.parent = parent
        self.add_command(label="Wyznacz cechy obiektu", command=lambda: self.calculate_features(parent))
        self.add_command(label="Inpainting", command=lambda: self.inpainting(parent))

    def calculate_features(self, parent):
        """Wyznacza momenty, pole powierzchni, obwód oraz współczynniki kształtu obiektu binarnego."""
        if parent.loaded_image_data:
            img_array = np.array(parent.loaded_image_data[2].convert("L"))

            # Ensure the image is binary
            binary_map = np.where(img_array > 127, 255, 0).astype(np.uint8)

            # Find contours
            contours, _ = cv2.findContours(binary_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) == 0:
                messagebox.showwarning("Brak konturów", "Nie wykryto obiektów w obrazie.")
                return

            # Calculate features for each contour
            results = []
            for i, contour in enumerate(contours):
                # Moments
                moments = cv2.moments(contour)

                # Area and Perimeter
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)

                # Shape Descriptors
                x, y, w, h = cv2.boundingRect(contour)  # Bounding box
                aspect_ratio = float(w) / h if h > 0 else 0
                extent = float(area) / (w * h) if w * h > 0 else 0

                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0

                equivalent_diameter = np.sqrt(4 * area / np.pi) if area > 0 else 0

                # Append results
                results.append({
                    "Contour": f"Object {i + 1}",
                    "Moments": moments,
                    "Area": area,
                    "Perimeter": perimeter,
                    "AspectRatio": aspect_ratio,
                    "Extent": extent,
                    "Solidity": solidity,
                    "EquivalentDiameter": equivalent_diameter
                })

            # Display results in a new window
            self.show_results_window(results, parent)

            # Save results to a text file
            self.save_results(results)
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby obliczyć cechy obiektu.")

    def show_results_window(self, results, parent):
        """Displays the results in a new window."""
        results_window = Toplevel(parent)
        results_window.title("Wyniki analizy")

        text_box = tk.Text(results_window, wrap="none", height=30, width=100)
        text_box.pack(expand=True, fill="both")

        for result in results:
            text_box.insert("end", f"{result['Contour']}:\n")
            text_box.insert("end", f"  Area: {result['Area']}\n")
            text_box.insert("end", f"  Perimeter: {result['Perimeter']}\n")
            text_box.insert("end", f"  AspectRatio: {result['AspectRatio']:.2f}\n")
            text_box.insert("end", f"  Extent: {result['Extent']:.2f}\n")
            text_box.insert("end", f"  Solidity: {result['Solidity']:.2f}\n")
            text_box.insert("end", f"  EquivalentDiameter: {result['EquivalentDiameter']:.2f}\n\n")
        text_box.configure(state="disabled")

    def save_results(self, results):
        """Zapisuje wyniki do pliku w wybranym formacie (txt lub xlsx)."""
        # Okno dialogowe dla wyboru formatu zapisu
        save_window = Toplevel(self.parent)
        save_window.title("Wybierz format zapisu")

        tk.Label(save_window, text="Wybierz format zapisu wyników:", font=("Arial", 10)).pack(pady=5)
        file_format = tk.StringVar(value="txt")

        tk.Radiobutton(save_window, text="Plik tekstowy (.txt)", variable=file_format, value="txt").pack(anchor="w")
        tk.Radiobutton(save_window, text="Plik Excel (.xlsx)", variable=file_format, value="xlsx").pack(anchor="w")

        def save_to_file():
            """Zapisuje wyniki w wybranym formacie."""
            selected_format = file_format.get()
            if selected_format == "txt":
                self.save_results_to_text(results)
            elif selected_format == "xlsx":
                self.save_results_to_excel(results)
            save_window.destroy()

        tk.Button(save_window, text="Zapisz", command=save_to_file).pack(pady=10)

    def save_results_to_text(self, results):
        """Zapisuje wyniki do pliku tekstowego."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w") as f:
                for result in results:
                    f.write(f"{result['Contour']}:\n")
                    f.write(f"  Area: {result['Area']}\n")
                    f.write(f"  Perimeter: {result['Perimeter']}\n")
                    f.write(f"  AspectRatio: {result['AspectRatio']:.2f}\n")
                    f.write(f"  Extent: {result['Extent']:.2f}\n")
                    f.write(f"  Solidity: {result['Solidity']:.2f}\n")
                    f.write(f"  EquivalentDiameter: {result['EquivalentDiameter']:.2f}\n\n")
            messagebox.showinfo("Zapisano", f"Wyniki zostały zapisane do pliku: {file_path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać wyników: {e}")

    def save_results_to_excel(self, results):
        """Zapisuje wyniki do pliku Excel."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            data = {
                "Object": [res["Contour"] for res in results],
                "Area": [res["Area"] for res in results],
                "Perimeter": [res["Perimeter"] for res in results],
                "AspectRatio": [res["AspectRatio"] for res in results],
                "Extent": [res["Extent"] for res in results],
                "Solidity": [res["Solidity"] for res in results],
                "EquivalentDiameter": [res["EquivalentDiameter"] for res in results],
            }
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Zapisano", f"Wyniki zostały zapisane do pliku Excel: {file_path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać wyników: {e}")

    def inpainting(self, parent):
        """Perform inpainting for a loaded image with auto-generated mask."""
        if parent.loaded_image_data:
            # Load the original image
            img = np.array(parent.loaded_image_data[2])

            def generate_mask(image):
                """
                Generate a binary mask from the damaged image.
                Detect pixels with a specific value (e.g., 0 or white spots).
                """
                # Create a mask where pixel values are close to 0 (e.g., black spots)
                mask = np.where(image <= 10, 255, 0).astype(np.uint8)  # Adjust threshold as needed
                return mask

            def apply_inpainting(image, mask):
                """
                Apply inpainting using OpenCV's inpainting methods.
                Ensure correct color handling between RGB and BGR formats.
                """
                try:
                    if len(image.shape) == 3:  # Color image
                        # Convert RGB to BGR for OpenCV compatibility
                        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                        # Perform inpainting
                        inpainted_bgr = cv2.inpaint(image_bgr, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
                        # Convert back from BGR to RGB
                        inpainted_image = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)
                    else:  # Grayscale image
                        inpainted_image = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

                    return inpainted_image
                except Exception as e:
                    messagebox.showerror("Błąd", f"Podczas inpaintingu wystąpił błąd: {e}")
                    return None

            try:
                # Generate mask
                gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
                mask = generate_mask(gray_image)

                # Perform inpainting
                result = apply_inpainting(img, mask)

                # Display the result
                if result is not None:
                    if len(img.shape) == 2:  # Grayscale image
                        result_image = Image.fromarray(result)
                    else:  # Color image
                        result_image = Image.fromarray(result)


                    parent.display_image(result_image, "Inpainting (Color-Corrected)")
            except Exception as e:
                messagebox.showerror("Błąd", f"Podczas inpaintingu wystąpił błąd: {e}")
        else:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz, aby wykonać inpainting.")

