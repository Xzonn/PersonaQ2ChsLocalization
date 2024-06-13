$cpkmakec = "bin\CRI_File_System_Tools_v2.40.13.0\cpkmakec.exe"
$pq2helper = "bin\PersonaQ2ChsLocalizationHelper\PersonaQ2ChsLocalizationHelper\bin\Release\net8.0\publish\PersonaQ2ChsLocalizationHelper.exe"

# Clean output folder
if (Test-Path -Path "out\" -PathType "Container") {
  Remove-Item -Recurse -Force "out\"
}
if (Test-Path -Path "temp\" -PathType "Container") {
  Remove-Item -Recurse -Force "temp\"
}

# Prepare for tools
dotnet publish -c Release --framework net8.0 "bin\PersonaQ2ChsLocalizationHelper\PersonaQ2ChsLocalizationHelper\PersonaQ2ChsLocalizationHelper.csproj"

# Unpack/extract original files
& $cpkmakec "original_files\patch102.cpk" -extract="temp\patch102"
& $pq2helper export -i "original_files\unpacked" -o "temp\export"
python scripts\export_code_bin.py

# Convert texts and create a character table
python scripts\remove_duplicate_files.py
python scripts\convert_msg_to_json.py
python scripts\import_csv_to_json.py
python scripts\generate_char_table.py
python scripts\convert_json_to_msg.py
python scripts\copy_duplicate_files.py

# Import texts
python scripts\import_code_bin.py
& $pq2helper import -i "original_files\unpacked" -j "temp\import" -o "temp\patch102"

# Create new font
New-Item -ItemType Directory -Path "temp\font" -Force
Push-Location "temp\font"
python ..\..\bin\3dstools\bcfnt.py -a -x -y -f ..\..\original_files\unpacked\font\seurapro_12_12.bcfnt
python ..\..\bin\3dstools\bcfnt.py -a -x -y -f ..\..\original_files\unpacked\font\seurapro_13_13.bcfnt
Pop-Location
python scripts\create_new_font.py
New-Item -ItemType Directory -Path "temp\patch102\font" -Force
Push-Location "temp\new_font"
python ..\..\bin\3dstools\bcfnt.py -c -y -f ..\patch102\font\seurapro_12_12.bcfnt
python ..\..\bin\3dstools\bcfnt.py -c -y -f ..\patch102\font\seurapro_13_13.bcfnt
Pop-Location

# FIXME: Remove top.arc to avoid the game crash
Remove-Item "temp\patch102\facility\pack\top.arc" -Force

# Repack cpk
& $cpkmakec "temp\patch102" "out\00040000001CBE00\romfs\patch102.cpk" -mode=FILENAME -forcecompress
