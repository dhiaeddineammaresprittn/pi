import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmployabiliteDashboardComponent } from './employabilite-dashboard.component';

describe('EmployabiliteDashboardComponent', () => {
  let component: EmployabiliteDashboardComponent;
  let fixture: ComponentFixture<EmployabiliteDashboardComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [EmployabiliteDashboardComponent]
    });
    fixture = TestBed.createComponent(EmployabiliteDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
  
});
