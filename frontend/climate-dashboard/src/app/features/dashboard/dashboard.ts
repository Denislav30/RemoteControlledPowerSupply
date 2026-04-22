import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { catchError, finalize, forkJoin, interval, of, startWith, Subject, switchMap, takeUntil} from 'rxjs';

import { CardModule } from 'primeng/card';
import { TagModule } from 'primeng/tag';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { ButtonModule } from 'primeng/button';
import { InputNumberModule } from 'primeng/inputnumber';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { ChartModule } from 'primeng/chart';

import { MessageService } from 'primeng/api';

import { AuthService } from '../../core/services/auth.service';
import { StatusService } from '../../core/services/status.service';
import { ControlService } from '../../core/services/control.service';
import { HistoryService } from '../../core/services/history.service';

import { StatusResponse } from '../../shared/models/status.models';
import { HealthHistoryResponse, TemperatureHistoryResponse
} from '../../shared/models/history.models';

type TagSeverity = 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast';

interface HistoryPoint {
  timestamp: string;
  timeLabel: string;
  temperature: number | null;
  powerSupply: number | null;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [ CommonModule, FormsModule, ReactiveFormsModule, CardModule, TagModule, ProgressSpinnerModule, ButtonModule, InputNumberModule, ToggleSwitchModule, ChartModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit, OnDestroy {
  private readonly authService = inject(AuthService);
  private readonly statusService = inject(StatusService);
  private readonly controlService = inject(ControlService);
  private readonly historyService = inject(HistoryService);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);
  private readonly messageService = inject(MessageService);
  private readonly destroy$ = new Subject<void>();

  readonly loading = signal(true);
  readonly errorMessage = signal('');
  readonly status = signal<StatusResponse | null>(null);
  readonly lastUpdated = signal<Date | null>(null);

  readonly modeUpdating = signal(false);
  readonly fanUpdating = signal<number | null>(null);
  readonly thresholdsSaving = signal(false);

  readonly showPowerBanner = signal(false);

  readonly thresholdsForm = this.fb.nonNullable.group({
    t1: [28, [Validators.required, Validators.min(0), Validators.max(100)]],
    t2: [30, [Validators.required, Validators.min(0), Validators.max(100)]],
    t3: [32, [Validators.required, Validators.min(0), Validators.max(100)]]
  });

  private readonly maxHistoryPoints = 20;
  private readonly history: HistoryPoint[] = [];

  chartData: any = {
    labels: [],
    datasets: [
      {
        label: 'Temperature (°C)',
        data: [],
        tension: 0.3,
        fill: false,
        yAxisID: 'y',
        spanGaps: true
      },
      {
        label: 'Power Supply (V)',
        data: [],
        tension: 0.3,
        fill: false,
        yAxisID: 'y1',
        spanGaps: true
      }
    ]
  };

  chartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      legend: {
        display: true
      }
    },
    scales: {
      y: {
        type: 'linear',
        position: 'left',
        title: {
          display: true,
          text: 'Temperature (°C)'
        }
      },
      y1: {
        type: 'linear',
        position: 'right',
        title: {
          display: true,
          text: 'Power Supply (V)'
        },
        grid: {
          drawOnChartArea: false
        }
      }
    }
  };

  ngOnInit(): void {
    this.loadInitialHistory();
    this.startLiveStatusPolling();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  isManualMode(): boolean {
    return this.status()?.system_mode === 'MANUAL';
  }

  changeMode(isManual: boolean): void {
    this.modeUpdating.set(true);

    this.controlService.setMode(isManual)
      .pipe(finalize(() => this.modeUpdating.set(false)))
      .subscribe({
        next: () => {
          const current = this.status();

          if (current) {
            this.status.set({
              ...current,
              system_mode: isManual ? 'MANUAL' : 'AUTO'
            });
          }

          this.messageService.add({
            severity: 'success',
            summary: 'Mode updated',
            detail: `System mode set to ${isManual ? 'MANUAL' : 'AUTO'}`
          });
        },
        error: () => {
          this.messageService.add({
            severity: 'error',
            summary: 'Mode update failed',
            detail: 'Failed to update system mode.'
          });
        }
      });
  }

  toggleFan(fanIndex: number, nextValue: boolean): void {
    if (!this.isManualMode()) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Manual mode required',
        detail: 'Fans can be controlled only in MANUAL mode.'
      });
      return;
    }

    const fanId = fanIndex + 1;
    this.fanUpdating.set(fanId);

    this.controlService.setFan(fanId, nextValue)
      .pipe(finalize(() => this.fanUpdating.set(null)))
      .subscribe({
        next: () => {
          const current = this.status();
          if (!current) return;

          const updatedFans = [...current.fans];
          updatedFans[fanIndex] = nextValue;

          this.status.set({
            ...current,
            fans: updatedFans
          });

          this.messageService.add({
            severity: 'success',
            summary: 'Fan updated',
            detail: `Fan ${fanId} set to ${nextValue ? 'ON' : 'OFF'}`
          });
        },
        error: (err) => {
          const detail =
            err?.status === 403
              ? 'Backend rejects fan control outside MANUAL mode.'
              : 'Failed to send fan command.';

          this.messageService.add({
            severity: 'error',
            summary: 'Fan update failed',
            detail
          });
        }
      });
  }

  saveThresholds(): void {
    if (this.thresholdsForm.invalid) {
      this.thresholdsForm.markAllAsTouched();
      return;
    }

    const { t1, t2, t3 } = this.thresholdsForm.getRawValue();
    const thresholds = [t1, t2, t3];

    this.thresholdsSaving.set(true);

    this.controlService.setThresholds(thresholds)
      .pipe(finalize(() => this.thresholdsSaving.set(false)))
      .subscribe({
        next: () => {
          const sortedThresholds = [...thresholds].sort((a, b) => a - b);
          const current = this.status();

          if (current) {
            this.status.set({
              ...current,
              config: {
                ...current.config,
                thresholds: sortedThresholds
              }
            });
          }

          this.thresholdsForm.patchValue(
            {
              t1: sortedThresholds[0],
              t2: sortedThresholds[1],
              t3: sortedThresholds[2]
            },
            { emitEvent: false }
          );

          this.thresholdsForm.markAsPristine();

          this.messageService.add({
            severity: 'success',
            summary: 'Thresholds saved',
            detail: 'Temperature thresholds have been updated.'
          });
        },
        error: () => {
          this.messageService.add({
            severity: 'error',
            summary: 'Save failed',
            detail: 'Failed to save threshold values.'
          });
        }
      });
  }

  getFanLabel(index: number, isOn: boolean): string {
    return `Fan ${index + 1}: ${isOn ? 'ON' : 'OFF'}`;
  }

  getModeSeverity(mode: string): TagSeverity {
    return mode === 'AUTO' ? 'success' : 'warn';
  }

  getPowerSupplySeverity(): TagSeverity {
    const powerSupply = this.getPowerSupplyNumber();

    if (powerSupply === null) {
      return 'secondary';
    }

    return powerSupply > 10 ? 'success' : 'danger';
  }

  getPowerSupplyText(): string {
    const powerSupply = this.getPowerSupplyNumber();

    if (powerSupply === null) {
      const raw = this.status()?.sensor_data.power_supply;

      if (typeof raw === 'string' && raw.trim().length > 0) {
        return raw;
      }

      return 'N/A';
    }

    return `${powerSupply.toFixed(2)} V`;
  }

  private loadInitialHistory(): void {
    forkJoin({
      temperature: this.historyService.getTemperatureHistory().pipe(
        catchError(() => of<TemperatureHistoryResponse>({ data: [] }))
      ),
      health: this.historyService.getHealthHistory().pipe(
        catchError(() => of<HealthHistoryResponse>({ data: [] }))
      )
    })
      .pipe(takeUntil(this.destroy$))
      .subscribe(({ temperature, health }) => {
        this.buildChartFromDatabaseHistory(temperature, health);
      });
  }

  private startLiveStatusPolling(): void {
    interval(2000)
      .pipe(
        startWith(0),
        switchMap(() => this.statusService.getStatus()),
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (response) => {
          const previous = this.status();

          this.status.set(response);
          this.lastUpdated.set(new Date());
          this.loading.set(false);
          this.errorMessage.set('');

          if (!this.thresholdsForm.dirty) {
            this.thresholdsForm.patchValue(
              {
                t1: response.config.thresholds[0] ?? 28,
                t2: response.config.thresholds[1] ?? 30,
                t3: response.config.thresholds[2] ?? 32
              },
              { emitEvent: false }
            );
          }

          this.pushLiveHistoryPoint(response);
          this.handleAlerts(previous, response);
        },
        error: () => {
          this.loading.set(false);
          this.errorMessage.set('Failed connection to the server.');
        }
      });
  }

  private buildChartFromDatabaseHistory(
    temperatureResponse: TemperatureHistoryResponse,
    healthResponse: HealthHistoryResponse
  ): void {
    const temperatureRows = temperatureResponse.data
      .slice(0, this.maxHistoryPoints)
      .reverse();

    const healthRows = healthResponse.data
      .slice(0, this.maxHistoryPoints)
      .reverse();

    const pointsByTimestamp = new Map<string, HistoryPoint>();

    for (const row of temperatureRows) {
      const timestamp = row[6];

      pointsByTimestamp.set(timestamp, {
        timestamp,
        timeLabel: this.formatTimeLabel(timestamp),
        temperature: row[1],
        powerSupply: null
      });
    }

    for (const row of healthRows) {
      const timestamp = row[4];
      const existing = pointsByTimestamp.get(timestamp);

      if (existing) {
        existing.powerSupply = row[1];
      } else {
        pointsByTimestamp.set(timestamp, {
          timestamp,
          timeLabel: this.formatTimeLabel(timestamp),
          temperature: null,
          powerSupply: row[1]
        });
      }
    }

    const sortedPoints = Array.from(pointsByTimestamp.values())
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .slice(-this.maxHistoryPoints);

    this.history.length = 0;
    this.history.push(...sortedPoints);

    this.refreshChartData();
  }

  private pushLiveHistoryPoint(response: StatusResponse): void {
    const now = new Date();
    const timestamp = now.toISOString();

    const point: HistoryPoint = {
      timestamp,
      timeLabel: this.formatTimeLabel(timestamp),
      temperature: response.sensor_data.temperature,
      powerSupply: this.parsePowerSupply(response.sensor_data.power_supply)
    };

    this.history.push(point);

    if (this.history.length > this.maxHistoryPoints) {
      this.history.shift();
    }

    this.refreshChartData();
  }

  private refreshChartData(): void {
    this.chartData = {
      labels: this.history.map(point => point.timeLabel),
      datasets: [
        {
          label: 'Temperature (°C)',
          data: this.history.map(point => point.temperature),
          tension: 0.3,
          fill: false,
          yAxisID: 'y',
          spanGaps: true
        },
        {
          label: 'Power Supply (V)',
          data: this.history.map(point => point.powerSupply),
          tension: 0.3,
          fill: false,
          yAxisID: 'y1',
          spanGaps: true
        }
      ]
    };
  }

  private handleAlerts(previous: StatusResponse | null, current: StatusResponse): void {
    const prevTemp = previous?.sensor_data.temperature ?? null;
    const currentTemp = current.sensor_data.temperature;
    const currentPowerAlert = current.sensor_data.power_alert;

    this.showPowerBanner.set(currentPowerAlert);

    if ((prevTemp === null || prevTemp < 32) && currentTemp >= 32) {
      this.messageService.add({
        severity: 'warn',
        summary: 'High temperature',
        detail: `Temperature reached ${currentTemp} °C`
      });
    }
  }

  private getPowerSupplyNumber(): number | null {
    const current = this.status();

    if (!current) {
      return null;
    }

    return this.parsePowerSupply(current.sensor_data.power_supply);
  }

  private parsePowerSupply(value: number | string): number | null {
    if (typeof value === 'number') {
      return Number.isFinite(value) ? value : null;
    }

    const normalized = value.replace(',', '.');
    const match = normalized.match(/-?\d+(\.\d+)?/);

    if (!match) {
      return null;
    }

    const parsed = Number(match[0]);

    return Number.isFinite(parsed) ? parsed : null;
  }

  private formatTimeLabel(timestamp: string): string {
    const normalized = timestamp.includes('T')
      ? timestamp
      : timestamp.replace(' ', 'T');

    const date = new Date(normalized);

    if (Number.isNaN(date.getTime())) {
      return timestamp;
    }

    return date.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }
}