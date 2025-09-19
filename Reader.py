import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# --- Essayer PyMuPDF (fortement recommandé) ---
PDF_ENGINE = None
try:
    import fitz  # PyMuPDF
    PDF_ENGINE = "pymupdf"
except Exception:
    pass

def extraire_texte_pdf(chemin):
    if PDF_ENGINE is None:
        raise RuntimeError(
            "Aucun moteur PDF trouvé. Installe d’abord:\n"
            "    pip install pymupdf\n"
            "ou  pip install pypdf2"
        )

    if PDF_ENGINE == "pymupdf":
        with fitz.open(chemin) as doc:
            textes = []
            for page in doc:
                # "text" = extraction en texte brut
                textes.append(page.get_text("text"))
            return "\n".join(textes).strip()

    # Fallback PyPDF2
    textes = []
    with open(chemin, "rb") as f:
        lecteur = PyPDF2.PdfReader(f)
        if lecteur.is_encrypted:
            # Essai de déverrouillage sans mot de passe (certains PDFs le permettent)
            try:
                lecteur.decrypt("")
            except Exception:
                pass
        for i, page in enumerate(lecteur.pages):
            try:
                textes.append(page.extract_text() or "")
            except Exception as e:
                textes.append(f"\n[Erreur extraction page {i+1}: {e}]\n")
    return "\n".join(textes).strip()

# --- Interface ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF → Text")
        self.geometry("900x600")

        top_bar = tk.Frame(self)
        top_bar.pack(fill=tk.X, padx=8, pady=8)

        self.btn_ouvrir = tk.Button(top_bar, text="📄 PDF Offnen", command=self.ouvrir_pdf)
        self.btn_ouvrir.pack(side=tk.LEFT, padx=4)

        self.btn_enregistrer = tk.Button(top_bar, text="💾 Text Speichern", command=self.enregistrer_texte)
        self.btn_enregistrer.pack(side=tk.LEFT, padx=4)

        self.btn_effacer = tk.Button(top_bar, text="🧹", command=self.effacer)
        self.btn_effacer.pack(side=tk.LEFT, padx=4)

        moteur_lbl = {
            "pymupdf": "PyMuPDF (recommandé)",
            "pypdf2": "PyPDF2 (secours)",
            None: "Aucun (installe pymupdf)"
        }[PDF_ENGINE]
        self.lbl_engine = tk.Label(top_bar, text=f"Moteur: {moteur_lbl}")
        self.lbl_engine.pack(side=tk.RIGHT, padx=4)

        self.texte = ScrolledText(self, wrap=tk.WORD, font=("Consolas", 11))
        self.texte.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def ouvrir_pdf(self):
        chemin = filedialog.askopenfilename(
            title="PDF",
            filetypes=[("Fichiers PDF", "*.pdf")]
        )
        if not chemin:
            return
        try:
            self.texte.delete("1.0", tk.END)
            self.texte.insert(tk.END, "⏳...\n")
            self.update_idletasks()

            contenu = extraire_texte_pdf(chemin)
            if not contenu:
                contenu = "[Aucun texte extrait (peut-être un PDF scanné / image).]"

            self.texte.delete("1.0", tk.END)
            self.texte.insert(tk.END, contenu)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def enregistrer_texte(self):
        contenu = self.texte.get("1.0", tk.END).strip()
        if not contenu:
            messagebox.showinfo("Info", "Rien à enregistrer.")
            return
        chemin = filedialog.asksaveasfilename(
            title="Enregistrer sous",
            defaultextension=".txt",
            filetypes=[("Texte", "*.txt")]
        )
        if not chemin:
            return
        try:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(contenu)
            messagebox.showinfo("Succès", "Texte enregistré.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def effacer(self):
        self.texte.delete("1.0", tk.END)

if __name__ == "__main__":
    App().mainloop()
