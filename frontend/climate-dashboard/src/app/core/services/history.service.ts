import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { HealthResponse, HistoryResponse } from '../../shared/models/history.models';

@Injectable({
  providedIn: 'root'
})
export class HistoryService {
  private readonly http = inject(HttpClient);
  private readonly dbApiUrl = environment.dbApiBaseUrl;

  getTemperatureHistory(): Observable<HistoryResponse> {
    return this.http.get<HistoryResponse>(`${this.dbApiUrl}/api/history`);
  }

  getHealthHistory(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.dbApiUrl}/api/health`);
  }
}