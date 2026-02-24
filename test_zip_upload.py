import asyncio
import os
import shutil
import pandas as pd
import zipfile
from pathlib import Path
from backend.app.services.question_service import question_service
from backend.app.database import engine
from sqlmodel import Session, select
from backend.app.models import Question

# Mock UploadFile
class MockUploadFile:
    def __init__(self, file_path):
        self.file = open(file_path, "rb")
        self.filename = os.path.basename(file_path)

async def test_zip_upload():
    print("Setting up test data...")
    test_dir = Path("test_zip_data")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Create Question Content
    q_dir = test_dir / "q_test_01"
    os.makedirs(q_dir)
    (q_dir / "question.py").write_text('description="Test Q"\ninitial_sample_code="print(1)"', encoding="utf-8")
    (q_dir / "validator.py").write_text("def validate(): return True", encoding="utf-8")
    (q_dir / "data.csv").write_text("col1,col2\n1,2", encoding="utf-8")
    
    # Create Metadata
    data = {
        "Title": ["Test Zip Question"],
        "Module": ["python_basics"],
        "Difficulty": ["Easy"],
        "Topic": ["Testing"],
        "Tags": ["test, zip"],
        "Folder Name": ["q_test_01"]
    }
    df = pd.DataFrame(data)
    excel_path = test_dir / "metadata.xlsx"
    df.to_excel(excel_path, index=False)
    
    # Zip it
    zip_path = Path("test_upload.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(excel_path, arcname="metadata.xlsx")
        for root, dirs, files in os.walk(q_dir):
            for file in files:
                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(test_dir)
                zipf.write(abs_path, arcname=str(rel_path))
                
    print(f"Created {zip_path}")
    
    # Run Service
    print("Running process_bulk_zip...")
    upload_file = MockUploadFile(zip_path)
    try:
        result = await question_service.process_bulk_zip(upload_file)
        print("Result:", result)
        
        # Verify DB
        with Session(engine) as session:
            statement = select(Question).where(Question.title == "Test Zip Question")
            q = session.exec(statement).first()
            if q:
                print(f"SUCCESS: Question created with ID {q.id} and folder {q.folder_name}")
                # Verify files
                final_path = Path(f"questions/{q.folder_name}")
                if (final_path / "question.py").exists() and (final_path / "data.csv").exists():
                    print("SUCCESS: Files copied correctly.")
                else:
                    print("FAILURE: Files not found in destination.")
            else:
                print("FAILURE: Question not found in DB.")
                
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        upload_file.file.close()
        if test_dir.exists():
            shutil.rmtree(test_dir)
        if zip_path.exists():
            os.remove(zip_path)

if __name__ == "__main__":
    asyncio.run(test_zip_upload())
