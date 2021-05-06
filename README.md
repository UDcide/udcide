# UDcide

UDcide is a tool that provides alternative way to deal with Android malware. We help you to detect and remove specific behaviors in the malware rather than just delete the whole binary. This enables possibilities of malware research and makes good use of the normal behaviors in the malware.

![](https://i.imgur.com/TrvdsEr.gif)

## Requirements
+ JDK >= 11
+ Apktool >= 2.5.0

## Installation
```bash
git clone https://github.com/UDcide/udcide.git
cd udcide
pipenv install
pipenv run python udcide/cli.py <APK_File>
```
