@echo pypt-offline Test Cases

python.exe apt-offline get C:\signature.uris --threads 5 -d C:\test
rmdir /q /s C:\test
ping -n 10 localhost 1>null

python.exe apt-offline get C:\signature.uris --threads 5 --bundle C:\apt-offline-bundle.zip
rmdir /q /s C:\apt-offline-bundle.zip
ping -n 10 localhost 1>null

python.exe apt-offline get C:\signature.uris --threads 5
ping -n 10 localhost 1>null

python.exe apt-offline get C:\signature.uris --bundle C:\apt-offline-bundle.zip
rmdir /q /s C:\apt-offline-bundle.zip
ping -n 10 localhost 1>null

python.exe apt-offline get C:\signature.uris -d C:\test
rmdir /q /s C:\test
ping -n 10 localhost 1>null

python.exe apt-offline get C:\signature.uris --threads 5 --bug-reports --download C:\test
rmdir /q /s C:\test
ping -n 10 localhost 1>null
