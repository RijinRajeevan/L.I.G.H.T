$sourceDir = "d:\Personal Projects\Epoch\Nyaana_vaas\backend\app\data"
$zipFile = "d:\Personal Projects\Epoch\Nyaana_vaas\legal_data.zip"

Write-Host "Compressing datasets..." 

if (Test-Path $zipFile) {
    Remove-Item $zipFile
}

Compress-Archive -Path "$sourceDir\*" -DestinationPath $zipFile

Write-Host "Done! Created legal_data.zip"
Write-Host "Transfer this file to your Ubuntu machine."
