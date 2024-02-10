// export default interface DeploymentEntry {
// 	deployment_id: number;
// 	deployment_source: string;
// 	deployment_type: string;
// 	source_id: number;
// 	deployment_time: string;
// 	deployment_device: string;
// 	deployment_quant: boolean;
// 	deployment_creat_time: string;
// 	deployment_start_time: string;
// 	deployment_end_time: string;
// 	deployment_api: string;
// 	deployment_web: string;
// 	visit_times: number;
// 	visit_successful_times: number;
// 	last_accessed_time: string;
// }

interface DeploymentEntry {
    deploy_finetuned: boolean;
    entry_id: number;
    end_time: string;
    description: string;
    params: any;
    model_or_finetune_id: number;
    start_time: string;
    name: string;
    port: number;
    state: number;
    devices: string;
}