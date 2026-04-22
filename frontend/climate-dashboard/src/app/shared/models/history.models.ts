export type TemperatureHistoryRow = [
  id: number,
  temperature: number,
  fan1: number,
  fan2: number,
  fan3: number,
  reason: string,
  timestamp: string
];

export type HealthHistoryRow = [
  id: number,
  voltage: number,
  fan_power_ok: number,
  hw_error: number,
  timestamp: string
];

export interface TemperatureHistoryResponse {
  data: TemperatureHistoryRow[];
}

export interface HealthHistoryResponse {
  data: HealthHistoryRow[];
}