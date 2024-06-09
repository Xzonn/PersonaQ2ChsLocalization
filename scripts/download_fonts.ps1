mkdir files/fonts/ -Force
mkdir out/ -Force
Invoke-WebRequest -Uri "https://hyperos.mi.com/font-download/MiSans.zip" -OutFile "out/MiSans.zip"
Expand-Archive -Path "out/MiSans.zip" -DestinationPath "out/"
Copy-Item -Path "out/MiSans/otf/MiSans-Semibold.otf" -Destination "files/fonts/FZFWQingYinTiJWB.ttf" -Force
