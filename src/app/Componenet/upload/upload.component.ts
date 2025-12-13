import { Component } from '@angular/core';
import { CommonModule, NgIf } from '@angular/common'; 
import { HttpClientModule } from '@angular/common/http'; 
import { CvService } from '../../Services/cv.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, NgIf, HttpClientModule],  
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  selectedFile: File | null = null;
  message: string = '';
  errorMsg: string = '';

  constructor(private cvService: CvService,private router: Router) {}

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
    this.message = '';
    this.errorMsg = '';
  }

  onUpload(): void {
    if (!this.selectedFile) {
      this.errorMsg = 'Please select a file first!';
      return;
    }

    this.cvService.uploadFile(this.selectedFile).subscribe({
      next: (response: any) => {
        this.message = 'Success! File ID: ' + response.id;
        console.log('Upload response:', response);
        console.log('CV Data:', response.cvData);
        
        // Navigate to the form page after upload
        setTimeout(() => {
          this.router.navigate(['/cv-form']); // Adjust route as needed
        }, 500);
      },
      error: (err: any) => {
        console.error('Upload error:', err);
        this.errorMsg = 'Upload failed: ' + (err.error?.message || 'Server error');
      }
    });

  this.cvService.uploadFile(this.selectedFile).subscribe({
    next: (response: any) => {
      this.message = 'Success! File ID: ' + response.id;
      console.log('Upload response:', response);
      console.log('CV Data:', response.cvData);
      
      // Navigate to the form or trigger form population
      // this.router.navigate(['/cv-form']);
    },
    error: (err: any) => {
      console.error('Upload error:', err);
      this.errorMsg = 'Upload failed: ' + (err.error?.message || 'Server error');
    }
  });
}
}
