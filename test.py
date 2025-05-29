import subprocess


text = input('command: ')
# text = '!rundocker docker run hello-world'

command = text.split(' ')[1:]
result = subprocess.run(' '.join(command), shell=True, check=True, capture_output=True)

if result.stderr:
    print('Error')
    print(result.stderr.decode())
if result.stdout:
    print('Result')
    print(result.stdout.decode())
