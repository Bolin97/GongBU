export interface DeploymentRequestParams {
    "model_or_adpater_id": number,
    "deploy_base_model": boolean,
    "bits_and_bytes": boolean,
    "load_8bit": boolean,
    "load_4bit": boolean,
    "use_flash_attention": boolean,
    "use_deepspeed": boolean,
    "devices": string[],
    "port": number
}

export function default_deployment_request_params(): DeploymentRequestParams {
    return {
        "model_or_adpater_id": 0,
        "deploy_base_model": false,
        "bits_and_bytes": false,
        "load_8bit": false,
        "load_4bit": false,
        "use_flash_attention": false,
        "use_deepspeed": false,
        "devices": [],
        "port": 0
    }
}