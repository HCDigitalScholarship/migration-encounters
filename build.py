import time 
from fastapi import Request
from main import index, interview,load_data, search
import shutil
from pathlib import Path 

def build_home():
    page = index(Request)
    (site_path / 'index.html').write_bytes(page.body)
    
def build_interviews():
    interviews = load_data()
    for person in interviews:
        page = interview(Request, person.name)
        interviews_path = Path.cwd() / 'site' / 'interview'
        if not interviews_path.exists():
            interviews_path.mkdir(parents=True, exist_ok=True)
        (interviews_path / (person.name +'.html')).write_bytes(page.body)

def build_search():
    page = search(Request)
    (site_path / 'search.html').write_bytes(page.body)

if __name__ == '__main__':
    start_time = time.time()
    # Create site directory
    site_path = Path.cwd() / 'site'
    if not site_path.exists():
        site_path.mkdir(parents=True, exist_ok=True)

    # Copy assets to site directory
    if not (site_path / 'assets').exists():
        shutil.copytree((Path.cwd() / 'assets'), (site_path / 'assets')) 
    else:
        shutil.rmtree((site_path / 'assets'))
        shutil.copytree((Path.cwd() / 'assets'), (site_path / 'assets')) 

    build_home()
    build_interviews()
    build_search()
    print(f"--- {time.time() - start_time} seconds ---")
