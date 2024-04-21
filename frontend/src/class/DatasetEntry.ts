export default interface DatasetEntry {
  id: number;
  pool_id: number;
  name: string;
  description: string;
  type: string;
  created_on: string;
  size: number;
  owner: string;
  public: boolean;
}
