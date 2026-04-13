export interface SensorData {
  temperature: number;
  power_supply: string;
  power_alert: boolean;
  hw_error: boolean;
}

export interface ConfigData {
  thresholds: number[];
}

export interface StatusResponse {
  system_mode: 'AUTO' | 'MANUAL';
  sensor_data: SensorData;
  fans: boolean[];
  config: ConfigData;
}