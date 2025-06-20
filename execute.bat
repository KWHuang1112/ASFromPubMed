@echo off
setlocal enabledelayedexpansion

REM Recursively process all PDF files in the current directory
for /R %%f in (*.pdf) do (
    echo Converting: %%f

    REM Output to same path with .txt1 extension
    python pdf2txt.py -t text -o "%%f.txt" "%%f"
)

echo Done!


python Txt2Format.py %%f >result.txt

pause
