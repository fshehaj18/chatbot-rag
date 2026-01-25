import os
import fitz  # PyMuPDF for PDFs
import docx
import json
import pandas as pd

SUPPORTED_EXTENSIONS = {
    "pdf", "txt", "md", "docx", "csv", "json", "yaml", "yml",
    "py", "js", "ts", "html", "css", "java", "cpp", "c", "go",
    "rs", "php", "sh", "sql", "xml", "ini", "cfg", "tf"
}

def read_pdf(path):
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)

def read_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def read_json(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        try:
            data = json.load(f)
            return json.dumps(data, indent=2)
        except Exception:
            return f.read()

def read_csv(path):
    df = pd.read_csv(path)
    return df.to_string()

def read_yaml(path):
    try:
        import yaml
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = yaml.safe_load(f)
            return json.dumps(data, indent=2)
    except Exception as e:
        return f"YAML read error: {e}"

def read_code(path):
    # For code or config files
    return read_text(path)

def load_all_files(data_folder="data", recursive=True):
    """Load text from all supported files in the project folder."""
    all_texts = []

    if not os.path.isdir(data_folder):
        raise ValueError(f"'{data_folder}' is not a valid folder.")

    for root, _, files in os.walk(data_folder):
        for filename in files:
            filepath = os.path.join(root, filename)
            ext = filename.lower().split(".")[-1]

            if ext not in SUPPORTED_EXTENSIONS:
                continue

            try:
                if ext == "pdf":
                    text = read_pdf(filepath)
                elif ext == "docx":
                    text = read_docx(filepath)
                elif ext == "json":
                    text = read_json(filepath)
                elif ext in {"yaml", "yml"}:
                    text = read_yaml(filepath)
                elif ext == "csv":
                    text = read_csv(filepath)
                elif ext in {"py", "js", "ts", "html", "css", "java", "cpp", "c", "go", "rs", "php", "sh", "sql", "xml", "ini", "cfg", "md", "txt"}:
                    text = read_code(filepath)
                else:
                    continue

                all_texts.append((filepath, text))
                print(f"✅ Loaded: {filepath}")
            except Exception as e:
                print(f"❌ Error reading {filepath}: {e}")

        if not recursive:
            break  # stop after first level

    print(f"\n📁 Loaded {len(all_texts)} files total.")
    return all_texts
