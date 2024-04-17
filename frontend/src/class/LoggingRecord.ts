export default interface LoggingRecord {
	id: number;
	learning_rate: number;
	step: number;
	loss: number;
	epoch: number;
	entry_id: number;
}
