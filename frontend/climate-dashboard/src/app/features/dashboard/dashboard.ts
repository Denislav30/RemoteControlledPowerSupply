import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { interval, Subject, switchMap, startWith, takeUntil, finalize } from 'rxjs';

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
import { StatusResponse } from '../../shared/models/status.models';

type TagSeverity = 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast';

interface TempPoint {
  timeLabel: string;
  value: number;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    CardModule,
    TagModule,
    ProgressSpinnerModule,
    ButtonModule,
    InputNumberModule,
    ToggleSwitchModule,
    ChartModule
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit, OnDestroy {
  private readonly authService = inject(AuthService);
  private readonly statusService = inject(StatusService);
  private readonly controlService = inject(ControlService);
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

  readonly showHwBanner = signal(false);
  readonly showPowerBanner = signal(false);

  readonly thresholdsForm = this.fb.nonNullable.group({
    t1: [28, [Validators.required, Validators.min(0), Validators.max(100)]],
    t2: [30, [Validators.required, Validators.min(0), Validators.max(100)]],
    t3: [32, [Validators.required, Validators.min(0), Validators.max(100)]]
  });

  private readonly maxHistoryPoints = 20;
  private readonly temperatureHistory: TempPoint[] = [];

  chartData: any = {
    labels: [],
    datasets: [
      {
        label: 'Temperature (°C)',
        data: [],
        tension: 0.3,
        fill: false
      }
    ]
  };

  chartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true
      }
    },
    scales: {
      y: {
        beginAtZero: false
      }
    }
  };

  ngOnInit(): void {
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

          this.thresholdsForm.patchValue(
            {
              t1: response.config.thresholds[0] ?? 28,
              t2: response.config.thresholds[1] ?? 30,
              t3: response.config.thresholds[2] ?? 32
            },
            { emitEvent: false }
          );

          this.pushTemperaturePoint(response.sensor_data.temperature);
          this.handleAlerts(previous, response);
        },
        error: () => {
          this.loading.set(false);
          this.errorMessage.set('Failed connection to the server.');
        }
      });
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
            detail: 'Failed mode change.'
          });
        }
      });
  }

  toggleFan(fanIndex: number, nextValue: boolean): void {
    if (!this.isManualMode()) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Manual mode required',
        detail: 'The fans can only be controlled in MANUAL mode.'
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
              ? 'Backend refuses fan control outside of MANUAL mode.'
              : 'Failed command to the fan.';

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
          const current = this.status();
          if (current) {
            this.status.set({
              ...current,
              config: {
                ...current.config,
                thresholds: [...thresholds].sort((a, b) => a - b)
              }
            });
          }

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

  getPowerSeverity(power: string): TagSeverity {
    return power === 'OK' ? 'success' : 'danger';
  }

  private pushTemperaturePoint(temp: number): void {
    const now = new Date();
    const label = now.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });

    this.temperatureHistory.push({
      timeLabel: label,
      value: temp
    });

    if (this.temperatureHistory.length > this.maxHistoryPoints) {
      this.temperatureHistory.shift();
    }

    this.chartData = {
      labels: this.temperatureHistory.map(point => point.timeLabel),
      datasets: [
        {
          label: 'Temperature (°C)',
          data: this.temperatureHistory.map(point => point.value),
          tension: 0.3,
          fill: false
        }
      ]
    };
  }

  private handleAlerts(previous: StatusResponse | null, current: StatusResponse): void {
    const prevHwError = previous?.sensor_data.hw_error ?? false;
    const prevPowerAlert = previous?.sensor_data.power_alert ?? false;
    const prevTemp = previous?.sensor_data.temperature ?? null;

    const currentHwError = current.sensor_data.hw_error;
    const currentPowerAlert = current.sensor_data.power_alert;
    const currentTemp = current.sensor_data.temperature;

    this.showHwBanner.set(currentHwError);
    this.showPowerBanner.set(currentPowerAlert);

    if (!prevHwError && currentHwError) {
      this.messageService.add({
        severity: 'error',
        summary: 'Hardware error',
        detail: 'The system is in HW ERROR / safe state.'
      });
    }

    if (!prevPowerAlert && currentPowerAlert) {
      this.messageService.add({
        severity: 'error',
        summary: 'Power alert',
        detail: 'A problem has been detected with the power supply to the fans.'
      });
    }

    if ((prevTemp === null || prevTemp < 32) && currentTemp >= 32) {
      this.messageService.add({
        severity: 'warn',
        summary: 'High temperature',
        detail: `The temperature reached ${currentTemp} °C`
      });
    }
  }
}