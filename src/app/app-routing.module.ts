import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AdmissionDashboardComponent } from './dashboards/admission-dashboard/admission-dashboard.component';
import { EmployabiliteDashboardComponent } from './dashboards/employabilite-dashboard/employabilite-dashboard.component';

const routes: Routes = [
  { path: 'admission', component: AdmissionDashboardComponent },
  { path: 'employabilite', component: EmployabiliteDashboardComponent },
  { path: '', redirectTo: '/admission', pathMatch: 'full' },  // Redirection vers /admission
  // Supprime ou modifie toute route /welcome si elle existe
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }