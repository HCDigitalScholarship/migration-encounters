from pathlib import Path
import shutil 
from fabric import Connection
from utils.secrets import HOST, PORT, USERNAME, PASSWORD

zip_path = Path.cwd() / 'site'
if zip_path.exists():
    shutil.make_archive(str(zip_path), 'zip', str(zip_path))
    print('made zip file')
    zip_file = str(zip_path).split('/')[-1]+'.zip'
    with Connection('{}@{}:{}'.format(USERNAME,HOST, PORT), connect_kwargs=dict(password=PASSWORD)) as c:
        c.put(str(zip_path)+'.zip', '/srv/migrantvoices/')
        #c.run('chmod 0777 /srv/migrantvoices/site.zip')
        #c.run('unzip -o /srv/migrantvoices/{} -d /srv/migrantvoices/'.format(zip_file))
        #c.run('chmod -R 0775 /srv/migrantvoices/')
        #c.run('rm /srv/migrantvoices/site.zip')
