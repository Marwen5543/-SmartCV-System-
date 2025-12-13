import { Component, OnInit, OnDestroy, ChangeDetectorRef, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CvService } from '../../Services/cv.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-cv-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './cv-form.component.html',
  styleUrls: ['./cv-form.component.css']
  
})
export class CvFormComponent implements OnInit, OnDestroy {
  cvForm!: FormGroup;
  private cvSubscription!: Subscription;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private cvService: CvService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    console.log('CvFormComponent initialized');
    this.initializeForm();

    // Subscribe to CV data updates
    this.cvSubscription = this.cvService.cvData$.subscribe(data => {
      console.log('Form received CV data from service:', data);
      if (data) {
        console.log('Populating form with data...');
        this.populateForm(data);
        // Force Angular to detect changes
        this.cdr.detectChanges();
        console.log('Form value after population:', this.cvForm.value);
      }
    });
  }

  ngOnDestroy() {
    this.cvSubscription?.unsubscribe();
  }

  initializeForm() {
    this.cvForm = this.fb.group({
      personalInfo: this.fb.group({
        fullName: ['', Validators.required],
        email: ['', [Validators.required, Validators.email]],
        phone: ['', Validators.required],
        address: [''],
        linkedin: [''],
        portfolio: [''],
        summary: ['']
      }),
      experiences: this.fb.array([this.createExperience()]),
      education: this.fb.array([this.createEducation()]),
      skills: this.fb.array([]),
      languages: this.fb.array([this.createLanguage()]),
      certifications: this.fb.array([this.createCertification()])
    });
  }

  populateForm(data: any) {
    console.log('populateForm called with:', data);
    
    // Personal info
    if (data.personalInfo) {
      console.log('Setting personal info:', data.personalInfo);
      this.cvForm.get('personalInfo')?.patchValue({
        fullName: data.personalInfo.fullName || '',
        email: data.personalInfo.email || '',
        phone: data.personalInfo.phone || '',
        address: data.personalInfo.address || '',
        linkedin: data.personalInfo.linkedin || '',
        portfolio: data.personalInfo.portfolio || '',
        summary: data.personalInfo.summary || ''
      });
      
      console.log('Personal Info after patch:', this.cvForm.get('personalInfo')?.value);
    }

    // Experiences
    this.experiences.clear();
    if (data.experiences && data.experiences.length > 0) {
      console.log('Adding experiences:', data.experiences);
      data.experiences.forEach((exp: any) => {
        const group = this.fb.group({
          company: [exp.company || '', Validators.required],
          position: [exp.position || '', Validators.required],
          startDate: [exp.startDate || '', Validators.required],
          endDate: [{ value: exp.endDate || '', disabled: exp.current || false }],
          current: [exp.current || false],
          description: [exp.description || '']
        });
        this.setupCurrentCheckbox(group);
        this.experiences.push(group);
      });
    } else {
      console.log('No experiences, adding default empty one');
      this.experiences.push(this.createExperience());
    }

    // Education
    this.education.clear();
    if (data.education && data.education.length > 0) {
      console.log('Adding education:', data.education);
      data.education.forEach((edu: any) => {
        this.education.push(this.fb.group({
          institution: [edu.institution || '', Validators.required],
          degree: [edu.degree || '', Validators.required],
          field: [edu.field || '', Validators.required],
          startDate: [edu.startDate || ''],
          endDate: [edu.endDate || ''],
          gpa: [edu.gpa || '']
        }));
      });
    } else {
      console.log('No education, adding default empty one');
      this.education.push(this.createEducation());
    }

    // Skills
    this.skills.clear();
    if (data.skills && data.skills.length > 0) {
      console.log('Adding skills:', data.skills);
      data.skills.forEach((skill: any) => {
        const name = typeof skill === 'string' ? skill : skill.name;
        this.skills.push(this.createSkill(name));
      });
    }

    // Languages
    this.languages.clear();
    if (data.languages && data.languages.length > 0) {
      console.log('Adding languages:', data.languages);
      data.languages.forEach((lang: any) => {
        this.languages.push(this.fb.group({
          language: [lang.language || '', Validators.required],
          proficiency: [lang.proficiency || '', Validators.required]
        }));
      });
    } else {
      console.log('No languages, adding default empty one');
      this.languages.push(this.createLanguage());
    }

    // Certifications
    this.certifications.clear();
    if (data.certifications && data.certifications.length > 0) {
      console.log('Adding certifications:', data.certifications);
      data.certifications.forEach((cert: any) => {
        this.certifications.push(this.fb.group({
          name: [cert.name || '', Validators.required],
          issuer: [cert.issuer || ''],
          date: [cert.date || '']
        }));
      });
    } else {
      console.log('No certifications, adding default empty one');
      this.certifications.push(this.createCertification());
    }

    console.log('Form after complete population:', this.cvForm.value);
  }

  // Helper method to setup current checkbox behavior
  private setupCurrentCheckbox(group: FormGroup) {
    group.get('current')?.valueChanges.subscribe(currentValue => {
      if (currentValue) {
        group.get('endDate')?.disable();
      } else {
        group.get('endDate')?.enable();
      }
    });
  }

  createExperience(): FormGroup {
    const group = this.fb.group({
      company: ['', Validators.required],
      position: ['', Validators.required],
      startDate: ['', Validators.required],
      endDate: [{ value: '', disabled: false }],
      current: [false],
      description: ['']
    });

    this.setupCurrentCheckbox(group);
    return group;
  }

  createEducation(): FormGroup {
    return this.fb.group({
      institution: ['', Validators.required],
      degree: ['', Validators.required],
      field: ['', Validators.required],
      startDate: [''],
      endDate: [''],
      gpa: ['']
    });
  }

  createSkill(skillName: string = ''): FormGroup {
    return this.fb.group({
      name: [skillName, Validators.required]
    });
  }

  createLanguage(): FormGroup {
    return this.fb.group({
      language: ['', Validators.required],
      proficiency: ['', Validators.required]
    });
  }

  createCertification(): FormGroup {
    return this.fb.group({
      name: ['', Validators.required],
      issuer: [''],
      date: ['']
    });
  }

  // FormArray getters
  get experiences(): FormArray { return this.cvForm.get('experiences') as FormArray; }
  get education(): FormArray { return this.cvForm.get('education') as FormArray; }
  get skills(): FormArray { return this.cvForm.get('skills') as FormArray; }
  get languages(): FormArray { return this.cvForm.get('languages') as FormArray; }
  get certifications(): FormArray { return this.cvForm.get('certifications') as FormArray; }

  // Add/Remove helpers
  addExperience() { 
    this.experiences.push(this.createExperience()); 
  }
  
  removeExperience(i: number) { 
    if (this.experiences.length > 1) this.experiences.removeAt(i); 
  }
  
  addEducation() { 
    this.education.push(this.createEducation()); 
  }
  
  removeEducation(i: number) { 
    if (this.education.length > 1) this.education.removeAt(i); 
  }
  
  addSkill() { 
    this.skills.push(this.createSkill()); 
  }
  
  removeSkill(i: number) { 
    this.skills.removeAt(i); 
  }
  
  addLanguage() { 
    this.languages.push(this.createLanguage()); 
  }
  
  removeLanguage(i: number) { 
    if (this.languages.length > 1) this.languages.removeAt(i); 
  }
  
  addCertification() { 
    this.certifications.push(this.createCertification()); 
  }
  
  removeCertification(i: number) { 
    if (this.certifications.length > 1) this.certifications.removeAt(i); 
  }

  // Submit
  onSubmit() {
    if (this.cvForm.valid) {
      this.http.post('http://localhost:8080/api/cv/save', this.cvForm.value)
        .subscribe({
          next: () => alert('CV saved successfully!'),
          error: err => { 
            console.error(err); 
            alert('Error saving CV'); 
          }
        });
    } else {
      alert('Please fill all required fields');
      this.markFormGroupTouched(this.cvForm);
    }
  }

  markFormGroupTouched(formGroup: FormGroup | FormArray) {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
      if (control instanceof FormGroup || control instanceof FormArray) {
        this.markFormGroupTouched(control);
      }
    });
  }

  resetForm() {
    this.cvForm.reset();
    this.initializeForm();
  }
}