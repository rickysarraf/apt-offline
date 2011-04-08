@echo pypt-offline Test Cases

python.exe apt-offline --fetch-update C:\update.uris --threads 5 --zip -d C:\test
rmdir /q /s C:\test
ping -n 10 localhost 1>null

python.exe apt-offline --fetch-update C:\update.uris --threads 5 --zip
rmdir /q /s pypt-downloads
ping -n 10 localhost 1>null

python.exe apt-offline --fetch-update C:\update.uris --threads 5
rmdir /q /s pypt-downloads
ping -n 10 localhost 1>null

python.exe apt-offline --fetch-update C:\update.uris --zip
rmdir /q /s pypt-downloads
ping -n 10 localhost 1>null

python.exe apt-offline --fetch-update C:\update.uris --threads 5 -d C:\test
rmdir /q /s C:\test
ping -n 10 localhost 1>null

python.exe apt-offline --fetch-upgrade C:\upgrade.uris --threads 5 --zip -d C:\test
rmdir /q /s C:\test
ping -n 10 localhost 1>null

python.exe apt-offline --fetch-upgrade C:\upgrade.uris --threads 5 --zip -d C:\test --fetch-bug-reports
rmdir /q /s C:\test
ping -n 10 localhost 1>null
