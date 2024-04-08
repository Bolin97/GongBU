import os

def get_deepspeed_config(
    zero_stage: int,
    zero_offload: bool
):
    config_folder = os.path.join(
        os.path.dirname(__file__),
        "deepspeed_config"
    )
    if zero_stage == 1:
        return os.path.join(config_folder, "deepspeed_1.json")
    elif zero_stage == 2:
        if zero_offload:
            return os.path.join(config_folder, "deepspeed_2_off.json")
        else:
            return os.path.join(config_folder, "deepspeed_2.json")
    elif zero_stage == 3:
        if zero_offload:
            return os.path.join(config_folder, "deepspeed_3_off.json")
        else:
            return os.path.join(config_folder, "deepspeed_3.json")
    else:
        raise ValueError("Invalid Deepspeed config.")