#ftp server 
$exe7z="C:\Program Files\7-Zip\7z.exe"
Set-Alias 7zip $exe7z

$ftp = "ftp://ftp.cfl.scf.rncan.gc.ca/regniere" 
$user = "anonymous" 
$pass = "anonymous"
$SetType = "bin"  
$dailyFiles = @("Canada-USA_1900-1950.zip", "Canada-USA_1950-1980.zip", "Canada-USA_1980-2020.zip")
$dailyLatest = @("Canada-USA_2020-2021.zip")
$gribsFiles = @("CanUS_20200101.tif", "CanUS_20200102.tif")
$normalsPast = @("Canada-USA_1941-1970.zip", "Canada-USA_1951-1980.zip", "Canada-USA_1961-1990.zip", "Canada-USA_1971-2000.zip")
$normalsFiles = @("Canada-USA_1981-2010.zip")
$normalsClimateChange = @("Canada-USA_1991-2100_CCC_GCM4-ESM2.7z", "Canada-USA_1991-2100_CCC_RCM4-ESM2.7z", "Canada-USA_1991-2100_Hadley_GEM2-ES.7z")
$demFiles = @("Monde_30s(SRTM30).tif")
$layerFiles = @("Shore.ann")

$webclient = New-Object System.Net.WebClient 
$tempDir = "./temp/"
$webclient.Credentials = New-Object System.Net.NetworkCredential($user,$pass) 

# Create temp folders and destination folder
New-Item -ItemType Directory -Force -Path $tempDir

# Daily
foreach($item in $dailyFiles){ 
    $uri = New-Object System.Uri($ftp + "/Data11/Weather/Daily/" +$item) 
    Write-Host "#001: Downloading $uri to $tempDir"
    $webclient.DownloadFile($uri, $tempDir + $item)
    Expand-Archive -Path "$tempDir$item" -Force ./biosim/data/Weather/Daily/
}

# Daily Latest
foreach($item in $dailyLatest){ 
    $uri = New-Object System.Uri($ftp + "/Data11/Weather/Daily/" +$item) 
    Write-Host "#002: Downloading $uri to $tempDir"
    $webclient.DownloadFile($uri, $tempDir + $item)
    Expand-Archive -Path "$tempDir$item" -Force ./biosim/data/Weather/DailyLatest/
}

# Gribs
$gribsDir="./biosim/data/Weather/Gribs/"
foreach($item in $gribsFiles){ 
    $uri = New-Object System.Uri($ftp + "/Data11/Weather/Gribs/Daily/2020/01/" +$item) 
    Write-Host "#003: Downloading $uri"
    $webclient.DownloadFile($uri, $gribsDir + $item)
}

# Normals
foreach($item in $normalsFiles){ 
    $uri = New-Object System.Uri($ftp + "/Data11/Weather/Normals/" +$item) 
    Write-Host "#004: Downloading $uri to $tempDir"
    $webclient.DownloadFile($uri, $tempDir + $item)
    Expand-Archive -Path "$tempDir$item" -Force ./biosim/data/Weather/Normals/
}

# Normals Past
foreach($item in $normalsPast){ 
    $uri = New-Object System.Uri($ftp + "/Data11/Weather/Normals/past/" +$item) 
    Write-Host "#005: Downloading $uri to $tempDir"
    $webclient.DownloadFile($uri, $tempDir + $item)
    Expand-Archive -Path "$tempDir$item" -Force ./biosim/data/Weather/Normals/
}

# Normal Climate Change
foreach($item in $normalsClimateChange){ 
    $uri = New-Object System.Uri($ftp + "/Data11/Weather/Normals/ClimateChange/" +$item) 
    Write-Host "#006: Downloading $uri to $tempDir"
    $webclient.DownloadFile($uri, $tempDir + $item)
    Invoke-Expression -Command "7zip x $tempDir$item -otemp/normals "
}
Get-ChildItem -Path temp -Recurse -File|Foreach-Object {
    write-host "#007: Moving item $_.fullname"
    Move-Item -Force -Path $_.fullname -Destination ./biosim/data/Weather/Normals/
}

# DEM
foreach($item in $demFiles){ 
    $uri = New-Object System.Uri($ftp + "/Data11/DEM/" +$item) 
    Write-Host "#004: Downloading $uri"
    $webclient.DownloadFile($uri, "biosim/data/DEM/" + $item)
}

# Layers
foreach($item in $demFiles){ 
    $uri = New-Object System.Uri($ftp + "/Data11/DEM/" +$item) 
    Write-Host "#004: Downloading $uri"
    $webclient.DownloadFile($uri, "biosim/data/DEM/" + $item)
}

# Remove temp
Remove-Item $tempDir -Recurse
