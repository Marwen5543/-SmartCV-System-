import { Routes } from '@angular/router';
import { UploadComponent } from './Componenet/upload/upload.component';
import { CvFormComponent } from './Componenet/cv-form/cv-form.component';

export const routes: Routes = [

    { path: '', component: UploadComponent },
    { path: 'cv', component: CvFormComponent }
];
