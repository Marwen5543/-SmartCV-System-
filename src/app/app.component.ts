import { Component, ViewEncapsulation } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CvFormComponent } from './Componenet/cv-form/cv-form.component';
import { UploadComponent } from './Componenet/upload/upload.component';


@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CvFormComponent, UploadComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})

export class AppComponent {
  title = 'smartcv-frontend';
}
