import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ControlService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = environment.apiBaseUrl;

  setMode(manual: boolean): Observable<void> {
    const params = new HttpParams().set('manual', manual);
    return this.http.post<void>(`${this.apiUrl}/mode`, null, { params });
  }

  setFan(fanId: number, on: boolean): Observable<void> {
    const params = new HttpParams().set('on', on);
    return this.http.post<void>(`${this.apiUrl}/fans/${fanId}`, null, { params });
  }

  setThresholds(thresholds: number[]): Observable<{ status: string }> {
    return this.http.post<{ status: string }>(`${this.apiUrl}/thresholds`, thresholds);
  }
}