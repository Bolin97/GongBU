# LLMCraft

🚀 LLMCraft is a comprehensive, all-in-one, no-code finetuning platform for large language models. Once deployed, there is no need to write any code to finetune a model, and the platform can be used by anyone with a web browser. The platform is built on top of the Transformers, Peft, etc. and is designed to be easy to use for non-technical users.

📈 You can easily finetune, evaluate, and deploy models with the platform. 

📦 Currently, by default, the platform should be started with docker-compose in a linux system with nvidia-docker. However, by installing the required dependencies, with correct configurations, the platform can be run locally. However, by installing locally, you need to manually twick the configurations, ports and the proxy settings.

## 📦 Recommended Way of Installation

The recommended installation is to use the docker-compose file provided in the repository on a linux system with nvidia-docker. This is the easiest way to install the platform.

It's simple, clone the repository, then run the `download.py` to download necessary files that are not included in the repository.

You need to install docker and [nvidia-docker](https://github.com/NVIDIA/nvidia-container-toolkit).

Then run the following command:

```bash
docker compose -f docker-compose.prod.yaml up
```

The platform should be running on `localhost:3000`.

## 🧾 Trivials

- We used [bun](https://bun.sh) instead of node, which is a blazingly-fast, all-in-one js bundler, runtime, test runner, package manager, etc. It is a relatively new project, but its performance attracted us to use it. Currently, it is stable for our use. However, if you want to switch to node for better stability, simply change all the bun-related command in the dockerfile to node or npm.

## ⚠️ Disclaimer

FOR ANY LOSS OR DAMAGE, THE DEVELOPER IS NOT RESPONSIBLE, AS IS STATED IN THE MIT LICENSE.

### 🔒 Security Issues

This project uses plain text to transfer data between the client and the server, which includes the username, password, and dataset. The password is hashed before being stored in the database, but the dataset is stored in plain text.

If you need to use the platform in open networks, please secure the database and secure the connections with SSL manually, this is not what we can provide. However, so long as SSL is enabled and the database is secured, equipped with other measures that are implemented by us, the platform should be secure.

### 📜 License Issues

The platform itself is distributed under the MIT license, but the dataset and the models are distributed under their respective licenses, with which the user should comply, and this platform is not shipped.