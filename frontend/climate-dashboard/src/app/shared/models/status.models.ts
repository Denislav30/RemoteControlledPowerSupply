export interface SensorData {
  temperature: number;
  power_supply: number | string;
  power_alert: boolean;
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