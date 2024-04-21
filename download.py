import inquirer
import rich
import os

supported_languages = {
    "English": "en",
    "简体中文": "zh-cn",
}

locales = {
    "zh-cn": {
        "license_warning": """
本应用程序使用MIT许可证，而其中的某些依赖项使用其他开源许可证。

此外，本应用程序中使用的模型和数据集是由用户导入的，可能使用不同的许可证，包括非自由许可证。

继续操作即表示您知晓 LLMCraft 本身可以自由分发、使用和修改。

但其他资源，尤其但不只是模型和数据集，应根据其各自的许可证使用。
        """,
        "agree_to_proceed": "我已知晓并同意以上内容。",
        "micromamba": "本项目使用了micromamba，它将从该链接下载 https://micro.mamba.pm/api/micromamba/linux-64/latest",
        "ok": "好的",
        "manually_download_micromamba": "你需要手动下载mciromamba的linux amd64版，并将其重命名，放在 本项目根目录/backend/dep/linux_mb.tar.bz2",
        "download_manually": "我将手动下载",
        "download_options": "本脚本将开始下载",
        "bert_model": "本项目使用了bert-base-model-chinese，它将从该链接下载 https://huggingface.co/google-bert/bert-base-chinese",
        "manually_download_bert_model": "你需要手动下载bert-base-model-chinese，并将其放在 本项目根目录/bert-base-chinese/ config.json及其它文件应在该目录下",
    },
    "en": {
        "license_warning": """
This application uses MIT license, whereas some of its dependency uses other open-source license. 

In addition, the models and datasets used in this application is imported by the user, and may use different licenses, even not free ones.

By proceeding, you are aware that the LLMCraft itself can be freely distributed, used and modified.

But other resources, especially, but not only models and datasets, should be used according to their respective licenses. 
        """,
        "agree_to_proceed": "I am aware and agree to the above.",
        "micromamba": "This app will use micromamba, it will be downloaded from https://micro.mamba.pm/api/micromamba/linux-64/latest",
        "ok": "OK",
        "manually_download_micromamba": "You need to download the linux amd64 version of micromamba manually, rename it, and put it in the root_directory_of_this_project/backend/dep/linux_mb.tar.bz2",
        "download_manually": "I will download it manually.",
        "download_options": "This script will start downloading",
        "bert_model": "This app uses bert-base-model-chinese, it will be downloaded from https://huggingface.co/google-bert/bert-base-chinese",
        "manually_download_bert_model": "You need to download bert-base-model-chinese manually, and put it in the root_directory_of_this_project/bert-base-chinese/ make sure that the config.json and other files are in the same directory.",
    },
}

questions = [
    inquirer.List(
        "language",
        message="Choose a language",
        choices=supported_languages.keys(),
        default="English",
    ),
]

answers = inquirer.prompt(questions)

# Set the language according to the user's choice
language = supported_languages[answers["language"]]

print()
rich.print(locales[language]["license_warning"])
print()

questions = [
    inquirer.Confirm(
        "license", message=locales[language]["agree_to_proceed"], default=True
    ),
]

answers = inquirer.prompt(questions)

if not answers["license"]:
    print("You need to agree to the license to proceed.")
    exit(1)

print()
rich.print(locales[language]["micromamba"])
print()

questions = [
    inquirer.List(
        "micromamba",
        message=locales[language]["download_options"],
        choices=[locales[language]["ok"], locales[language]["download_manually"]],
        default=locales[language]["ok"],
    ),
]

answers = inquirer.prompt(questions)

if answers["micromamba"] == locales[language]["download_manually"]:
    rich.print(locales[language]["manually_download_micromamba"])
else:
    os.system("mkdir -p ./backend/dep")
    os.system(
        "wget -O ./backend/dep/linux_mb.tar.bz2 https://micro.mamba.pm/api/micromamba/linux-64/latest"
    )

print()
rich.print(locales[language]["bert_model"])
print()

questions = [
    inquirer.List(
        "bert_model",
        message=locales[language]["download_options"],
        choices=[locales[language]["ok"], locales[language]["download_manually"]],
        default=locales[language]["ok"],
    ),
]

answers = inquirer.prompt(questions)

if answers["bert_model"] == locales[language]["download_manually"]:
    rich.print(locales[language]["manually_download_bert_model"])
else:
    os.system("mkdir -p ../bert-base-chinese")
    os.system("cd ../bert-base-chinese && git init && git lfs install")
    os.system("rm -rf ../bert-base-chinese")
    os.system(
        "cd .. && git clone https://huggingface.co/google-bert/bert-base-chinese.git"
    )

print("Download complete.")
