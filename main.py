import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.getenv("SMARTCAT_ACCOUNT_ID")
API_KEY = os.getenv("SMARTCAT_API_KEY")
BASE_URL = os.getenv("SMARTCAT_BASE_URL")

print(f"Account ID: {ACCOUNT_ID}")
print(f"API Key: {API_KEY[:10]}...")
print(f"Base URL: {BASE_URL}")

def get_auth():
    return (ACCOUNT_ID, API_KEY)

def create_project(name, source_lang, target_langs):
    print(f"\n📁 Creating project: {name}")
    url = f"{BASE_URL}/api/integration/v1/project/create"
    data = {
        "model": f'{{"name": "{name}", "sourceLanguage": "{source_lang}", "targetLanguages": {target_langs}}}'
    }
    response = requests.post(url, auth=get_auth(), data=data)
    print(f"   Status code: {response.status_code}")
    print(f"   Response: {response.text}")
    project = response.json()
    print(f"✅ Project created: {project['id']}")
    return project['id']

def upload_document(project_id, file_path):
    print(f"\n📄 Uploading document: {file_path}")
    url = f"{BASE_URL}/api/integration/v1/project/document?projectId={project_id}"
    with open(file_path, 'rb') as f:
        response = requests.post(
            url,
            auth=get_auth(),
            files=[
                ('', (os.path.basename(file_path), f, 'text/plain')),
                ('', ('blob', '[{}]', 'application/json')),
            ]
        )
    print(f"   Status code: {response.status_code}")
    print(f"   Response: {response.text}")
    if not response.text.strip():
        print("❌ Empty response")
        return []
    documents = response.json()
    doc_ids = [doc['id'] for doc in documents]
    print(f"✅ Uploaded: {doc_ids}")
    return doc_ids
def poll_status(project_id):
    print(f"\n⏳ Polling project status...")
    url = f"{BASE_URL}/api/integration/v1/project/{project_id}"
    while True:
        response = requests.get(url, auth=get_auth())
        project = response.json()
        status = project['status']
        docs = project.get('documents', [])
        all_assembled = all(
            d.get('documentDisassemblingStatus') == 'success'
            for d in docs
        )
        print(f"   Status: {status} | Disassembling: {'done' if all_assembled else 'in progress'}")
        if all_assembled and len(docs) > 0:
            print(f"✅ Documents ready — {docs[0]['wordsCount']} words")
            return [d['id'] for d in docs]
        time.sleep(3)

def request_export(doc_ids):
    print(f"\n📦 Requesting export...")
    ids_param = ",".join(doc_ids)
    url = f"{BASE_URL}/api/integration/v1/document/export?documentIds={ids_param}"
    response = requests.post(url, auth=get_auth())
    task_id = response.json()['id']
    print(f"✅ Export task ID: {task_id}")
    return task_id

def download_translation(task_id, output_path):
    print(f"\n⬇️  Downloading translated file...")
    url = f"{BASE_URL}/api/integration/v1/document/export/{task_id}"
    response = requests.get(url, auth=get_auth())
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"✅ Saved to: {output_path}")

def run_pipeline(file_path, project_name, source_lang, target_langs):
    print("\n🚀 Starting Smartcat Translation Pipeline")
    print("=" * 45)

    # Step 1 — Create project
    project_id = create_project(project_name, source_lang, str(target_langs).replace("'", '"'))

    # Step 2 — Upload document
    upload_document(project_id, file_path)

    # Step 3 — Poll until ready
    doc_ids = poll_status(project_id)

    # Step 4 — Request export
    task_id = request_export(doc_ids)

    # Step 5 — Download
    output_path = "translated_output.zip"
    download_translation(task_id, output_path)

    print("\n🎉 Pipeline complete!")
    print(f"   Project ID : {project_id}")
    print(f"   Output file: {output_path}")
    print("=" * 45)

if __name__ == "__main__":
    run_pipeline(
        file_path="input.txt",
        project_name="Pipeline Test",
        source_lang="en",
        target_langs=["fr", "de"]
    )