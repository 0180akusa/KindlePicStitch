# KindlePicStitch
To stitch the `.azw` files downloaded from Kindle through [Calibre](https://calibre-ebook.com/ja/download_windows) converted images.

![IMG_0_sample](/0_sample.jpg1)

## GET `.azw` from Kindle

### 1. Download elder versions of the Kindle
Be sure to download the [KindleForPC-installer.exe](/Software) software before version 1.24.51068.

SHA-256:`c7a1a93763d102bca0fed9c16799789ae18c3322b1b3bdfbe8c00422c32f83d7`

After decompression, you can run this command at the executable's location to check the file:
```console
certutil -hashfile KindleForPC-installer-1.24.51068.exe SHA256
```

### 2. Preventing Kindle Automatic Updates

Find the **hosts** file located in the `C:\Windows\System32\drivers\etc` folder.

Copy the **hosts** file to the `desktop` and add a line at the end of the file:
 
```text
127.0.0.1   kindleforpc.s3.amazonaws.com
``` 
Replace the original **hosts** file with the edited **hosts** file.

Cancel automatic updates and close the KindleforPC.

### 3. Make sure the download format is `.azw` 

Disable the use of new `KFX/KCR` formats, run this command in `Windows PowerShell`:
``` console
ren $env:localappdata\Amazon\Kindle\application\renderer-test.exe renderer-test.xxx
```

Or run this command in `CMD`:
```console
ren %localappdata%\Amazon\Kindle\application\renderer-test.exe renderer-test.xxx
```
### 4. Check the download files

Buy a Kindle eBook on Amazon's local site, login on KindleforPC.

Right-click the corresponding book and click Download.

You can find the downloaded book in `Document\My Kindle`, where the `.azw` or `.azw3` files in folders named ASIN.

## Convert to images

### 1. Download and install the [Calibre](https://calibre-ebook.com/ja/download_windows) from the website.

### 2. Download the latest version [plug-in](https://github.com/noDRM/DeDRM_tools/releases/tag/v10.0.3).

### 3. Import Kindle books

Click and drag `.azw` file into Calibre.

Select the book and click `convert format`, you can convert the book to any format including `zip`, `epub`.

### 4. Get images

Extract the `zip` and you can find all the `jpeg` images contained in the `images` folder.
