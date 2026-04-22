import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {HealthHistoryResponse,TemperatureHistoryResponse
} from '../../shared/models/history.models';

@Injectable({
  providedIn: 'root'
})
export class HistoryService {
  private readonly http = inject(HttpClient);
  private readonly dbApiUrl = environment.dbApiBaseUrl;

  getTemperatureHistory(): Observable<TemperatureHistoryResponse> {
    return this.http.get<TemperatureHistoryResponse>(`${this.dbApiUrl}/api/history`);
  }

  getHealthHistory(): Observable<HealthHistoryResponse> {
    return this.http.get<HealthHistoryResponse>(`${this.dbApiUrl}/api/health`);
  }
}