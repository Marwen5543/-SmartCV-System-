import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, tap } from 'rxjs/operators';

export interface CvData {
  personalInfo?: {
    fullName: string;
    email: string;
    phone: string;
    address?: string;
    linkedin?: string;
    portfolio?: string;
    summary?: string;
  };
  experiences?: any[];
  education?: any[];
  skills?: any[];
  languages?: any[];
  certifications?: any[];
}

@Injectable({
  providedIn: 'root'
})
export class CvService {

  private baseUrl = 'http://localhost:8080/api/cv';

  // Initialize with null, but it will hold the latest CV data
  private cvDataSubject = new BehaviorSubject<CvData | null>(null);
  cvData$ = this.cvDataSubject.asObservable();

  constructor(private http: HttpClient) {}

  uploadFile(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<any>(`${this.baseUrl}/upload`, formData)
      .pipe(
        tap(response => {
          console.log('Service received upload response:', response);
          if (response && response.cvData) {
            console.log('Service updating cvDataSubject with:', response.cvData);
            this.cvDataSubject.next(response.cvData);
            console.log('Current BehaviorSubject value:', this.cvDataSubject.value);
          }
        })
      );
  }

  // Get current CV data (useful for debugging)
  getCurrentCvData(): CvData | null {
    return this.cvDataSubject.value;
  }

  saveCv(cvData: CvData): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/save`, cvData)
      .pipe(
        tap(response => {
          if (response && response.cvData) {
            this.cvDataSubject.next(response.cvData);
          } else {
            this.cvDataSubject.next(cvData);
          }
        })
      );
  }

  setCvData(data: CvData) {
    this.cvDataSubject.next(data);
  }

  getCvById(id: number): Observable<CvData> {
    return this.http.get<any>(`${this.baseUrl}/${id}`)
      .pipe(
        map(response => response.cvData),
        tap(cvData => {
          if (cvData) {
            this.cvDataSubject.next(cvData);
          }
        })
      );
  }
}