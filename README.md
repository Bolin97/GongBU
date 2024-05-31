# 工部/GongBU <img src="https://github.com/Bolin97/GongBU/blob/main/frontend/static/logo_new.jpg" alt="logo" width="30"/>


🚀 GongBU is a comprehensive, all-in-one, no-code, local finetuning platform for large language models. Once deployed, there is no need to write any code to finetune a model, and the platform can be used by anyone with a web browser. The platform is built on top of the Transformers, Peft, etc. and is designed to be easy to use for non-technical users.

📈 You can easily finetune, evaluate, and deploy models with the platform. 

📦 Currently, by default, the platform should be started with docker-compose in a linux system with nvidia-docker. However, by installing the required dependencies, with correct configurations, the platform can be run natively.

## 📦 Recommended Way of Installation

The recommended installation is to use the docker-compose file provided in the repository on a linux system with nvidia-docker. This is the easiest way to install the platform.

It's simple, clone the repository, then run the `download.py` (inquirer and rich libraries are required) to download necessary files that are not included in the repository, micromamba and a bert model to be exact.

You need to install docker and [nvidia-docker](https://github.com/NVIDIA/nvidia-container-toolkit).

Then run the following command:

```bash
docker compose -f docker-compose.prod.yaml up
```

The platform should be running on `localhost:5173` behind an nginx reverse proxy. Simply use `localhost:5173/home` to access the platform.

## 🔧 Usage

After accessing the platform, you will be welcomed by the log in page. By default, the platform does not provide any user, so you need to create a user by clicking the sign up button.

When signing up, by default, you will need a token to sign up. It will be in the `sign_up_token.txt` file in the root directory of the project. You can change the token in the `sign_up_token.txt` however you want. Nevertheless, you can use a permissive registering strategy by setting the environment variable `NO_SIGNUP_TOKEN` in the docker compose file, which will allow anyone to sign up.

After logging in, you will find everything to be empty, here's how you can import assets into the platform, only two kinds of assets are needed, the dataset and the model.

- To upload a dataset, you need to go to the data page. The datasets are arranged in pools, with each pools containing several datasets. You can create a new pool by clicking the create button, and follow the instructions to upload a dataset. You can also click the details button of an existing pool to upload a dataset to that pool.

- To download models, you need to go to the model download page. It will ask for a model list, which is a json list, and below is an example.

    ```json
    [
        {
            "model_display_name": "Bloom 560m",
            "model_name": "bloom-560m",
            "source": "git",
            "model_description": "This is the description for the bloom-560m model",
            "download_url": "https://huggingface.co/bigscience/bloomz-560m",
            "avatar_url": "https://aeiljuispo.cloudimg.io/v7/https://cdn-uploads.huggingface.co/production/uploads/1634806038075-5df7e9e5da6d0311fd3d53f9.png?w=200&h=200&f=face"
        }
    ]
    ```

    The avatar is optional, you can simply omit it. `source` defines how the model should be downloaded, and currently, only `git` is supported.

    Then, you can click the download button in the same page to download the models.

    We will soon provide a list for common models. Currently, we have to trouble you to write the json list yourself.

After you have uploaded the datasets and downloaded the models, you can fintune, evaluate and deploy the models on respective pages.

## ✅ Current Status

The platform is now fully functional, albeit under constant development and polishing, especially the frontend, and breaking changes may take place.

## 🧾 Trivial

- We used [bun](https://bun.sh) instead of node, which is a blazingly-fast, all-in-one js bundler, runtime, test runner, package manager, etc. It is a relatively new project, but its performance attracted us to use it. Currently, it is stable for our use. However, if you want to switch to node for better stability, simply change all the bun-related command in the dockerfile to node or npm.

## ⚠️ Disclaimer

FOR ANY LOSS OR DAMAGE, THE DEVELOPER IS NOT RESPONSIBLE, AS IS STATED IN THE MIT LICENSE.

### 🔒 Security Issues

This project uses plain text to transfer data between the client and the server, which includes the username, password, and dataset. The password is hashed before being stored in the database, but the dataset is stored in plain text.

If you need to use the platform in open networks, please secure the database and secure the connections with SSL manually, this is not what we can provide (by changing the nginx config under the proxy folder, all requests in production goes through nginx). However, so long as SSL is enabled and the database is secured, equipped with other measures that are implemented by us, the platform should be secure.

### 📜 License Issues

The platform itself is distributed under the MIT license, but the dataset and the models are distributed under their respective licenses, with which the user should comply, and this platform is not shipped.
