
import pandas as pd
import zipfile
import os
from pathlib import Path

def generate_sample_zip():
    base_dir = Path("c:/Users/User/Practice_Room/backend/app/static/sample_template")
    output_zip = Path("c:/Users/User/Practice_Room/backend/app/static/sample_questions.zip")
    
    # 1. Convert CSV metadata to Excel
    csv_path = base_dir / "metadata_source.csv"
    xlsx_path = base_dir / "metadata.xlsx"
    
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df.to_excel(xlsx_path, index=False)
        print(f"Generated {xlsx_path}")
    
    # 2. Create ZIP
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add metadata.xlsx
        if xlsx_path.exists():
            zipf.write(xlsx_path, "metadata.xlsx")
        
        # Add question folders
        for folder in ["example_q1", "example_q2"]:
            folder_path = base_dir / folder
            if folder_path.exists():
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        full_path = Path(root) / file
                        arcname = folder / full_path.relative_to(folder_path)
                        zipf.write(full_path, arcname)
                        
    print(f"Generated {output_zip}")

if __name__ == "__main__":
    generate_sample_zip()
