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
