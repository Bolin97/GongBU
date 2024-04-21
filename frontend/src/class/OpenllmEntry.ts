export default interface OpenllmEntry {
  id: string;
  model_name: string;
  display_name: string;
  model_description: string;
  view_pic: string;
  remote_path: string;
  local_path: string;
  local_store: number;
  storage_state: string;
  storage_date: string;
  owner: string;
  public: boolean;
}
