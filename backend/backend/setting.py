# from pydantic import BaseSettings


# class Settings(BaseSettings):
#     require_auth: bool = False
#     auth_pass_env_var: str = ""
#     auth_user_env_var: str = ""
#     default_env: str = ""
#     repo_root: str = "D:\tinyGit\client\demo\repo"
#     git_bin_path: str = "/usr/bin/git"
#     upload_pack: bool = True
#     receive_pack: bool = True
#     route_prefix: str = ""
#     server_address: str = "0.0.0.0:8000"

#     class Config:
#         env_prefix = "GIT_HTTP_"

# settings = Settings()