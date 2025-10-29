# clu-set-timer
Using CLU to recognise a set timer command (text-based)

This programme is based on [Microsoft IoT For Beginners | Chapter 6, lesson 2](https://github.com/microsoft/IoT-For-Beginners/tree/main/6-consumer/lessons/2-language-understanding).
Since LUIS is reaching EOS in October of 2025, this is migrated to CLU.

## Precaution
This runs on Python 3.9, I have not tested it elsewhere so proceed at your own risk.
> Recommend using a virtual environment, things can get messy.

## Usage
1. Run the python app
2. From Command Prompt
```
curl.exe --request POST "[your url]" --header "Content-Type: application/json" --data "{\text\:\"[add your command here]\"}"
```
