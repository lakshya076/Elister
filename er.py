from urllib.request import urlretrieve
import getpass
import subprocess

url = 'https://sourceforge.net/projects/artigence/files/latest/download'

print('File Downloading')

usrname = getpass.getuser()
destination = f'C:\\Users\\{usrname}\\Downloads\\download.exe'

download = urlretrieve(url, destination)


print('File downloaded')
print('Installing now:')


cmd = f'{destination} batch.exe'

returned_value = subprocess.call(cmd, shell=True)  # returns the exit code in unix
print('rVal:', returned_value)
