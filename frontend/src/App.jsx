import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import { AppErrorBoundary } from "./components/error";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import AdminLayout from "./components/layout/AdminLayout";
import LoginPage from "./pages/LoginPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import ActivationPage from "./pages/ActivationPage";
import ContractAcceptancePage from "./pages/ContractAcceptancePage";
import CreateManagerPage from "./pages/CreateManagerPage";
import DashboardPage from "./pages/DashboardPage";
import PacientesPage from "./pages/PacientesPage";
import ProfissionaisPage from "./pages/ProfissionaisPage";
import ProfessionalPage from "./pages/ProfessionalPage";
import ConsultasPage from "./pages/ConsultasPage";
import EmpresasPage from "./pages/EmpresasPage";
import CompaniesPage from "./pages/CompaniesPage";
import EstablishmentsPage from "./pages/EstablishmentsPage";
import ClientsPage from "./pages/ClientsPage";
import ContractsPage from "./pages/ContractsPage";
import ContractsPageWithTabs from "./pages/ContractsPageWithTabs";
import ContractDashboard from "./components/views/ContractDashboard";
import ContractLivesManager from "./components/views/ContractLivesManager";
import ContractDetails from "./components/views/ContractDetails";
import FlowbiteTableExamplePage from "./pages/FlowbiteTableExamplePage";
import ReportsPage from "./pages/ReportsPage";
import ServicesCatalogPage from "./pages/ServicesCatalogPage";
import MedicalAuthorizationsPage from "./pages/MedicalAuthorizationsPage";
import BillingDashboardPage from "./pages/BillingDashboardPage";
import B2BBillingPage from "./pages/B2BBillingPage";
import SubscriptionPlansPage from "./pages/SubscriptionPlansPage";
import InvoicesPage from "./pages/InvoicesPage";
import MenusPage from "./pages/MenusPage";
import UsersPage from "./pages/UsersPage";
import { RolesPage } from "./pages/RolesPage";
import NotificationDemo from "./pages/NotificationDemo";
import NotFoundPage from "./pages/NotFoundPage";
import { ActivityCreatePage } from "./pages/ActivityCreatePage";
import { ActivityEditPage } from "./pages/ActivityEditPage";
import { ActivityListPage } from "./pages/ActivityListPage";
import { PendencyBoardPage } from "./pages/PendencyBoardPage";
import { KanbanBoardPage } from "./pages/KanbanBoardPage";
import { KanbanCardCreatePage } from "./pages/KanbanCardCreatePage";
import KanbanAnalyticsPage from "./pages/KanbanAnalyticsPage";
// Secure session service removido

function App() {
  // Initialize secure session service on app start
  // Secure session service removido - simplificação

  return (
    <AppErrorBoundary>
      <AuthProvider>
        <ThemeProvider>
          <div className="h-full">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route
                path="/reset-password/:token"
                element={<ResetPasswordPage />}
              />
              <Route path="/activate/:token" element={<ActivationPage />} />
              <Route
                path="/contract-acceptance/:token"
                element={<ContractAcceptancePage />}
              />
              <Route
                path="/create-manager/:token"
                element={<CreateManagerPage />}
              />

               {/* Redirect root to admin */}
               <Route path="/" element={<Navigate to="/admin" replace />} />

               {/* Professional routes with AdminLayout */}
               <Route
                 path="/professional"
                 element={
                   <ProtectedRoute>
                     <AdminLayout />
                   </ProtectedRoute>
                 }
               >
                 <Route index element={<ProfessionalPage />} />
               </Route>

               {/* Admin routes with AdminLTE layout */}
               <Route
                 path="/admin"
                 element={
                   <ProtectedRoute>
                     <AdminLayout />
                   </ProtectedRoute>
                 }
               >
                <Route index element={<DashboardPage />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="patients" element={<PacientesPage />} />
                <Route path="professionals" element={<ProfissionaisPage />} />
                <Route path="appointments" element={<ConsultasPage />} />
                  <Route path="companies/:id?" element={<CompaniesPage />} />
                <Route
                  path="establishments"
                  element={<EstablishmentsPage />}
                />
                <Route
                  path="establishments/:id"
                  element={<EstablishmentsPage />}
                />
                <Route path="clients" element={<ClientsPage />} />
                <Route path="clients/:id" element={<ClientsPage />} />

                {/* Rotas específicas de contratos PRIMEIRO */}
                <Route
                  path="contracts/:id/edit"
                  element={<ContractsPage />}
                />
                <Route
                  path="contracts/view/:id"
                  element={<ContractDetails />}
                />
                <Route
                  path="contracts/:id/lives"
                  element={<ContractLivesManager />}
                />
                <Route
                  path="contracts/:id/settings"
                  element={<ContractsPage />}
                />
                <Route path="contracts/:id" element={<ContractsPage />} />
                <Route path="lives" element={<ContractLivesManager />} />

                {/* Rota principal com abas */}
                <Route path="contracts" element={<ContractsPageWithTabs />} />
                <Route
                  path="flowbite-table-exemplo"
                  element={<FlowbiteTableExamplePage />}
                />
                <Route path="reports" element={<ReportsPage />} />
                <Route path="services" element={<ServicesCatalogPage />} />
                <Route
                  path="authorizations"
                  element={<MedicalAuthorizationsPage />}
                />
                <Route
                  path="authorizations/:id"
                  element={<MedicalAuthorizationsPage />}
                />
                <Route
                  path="billing/dashboard"
                  element={<BillingDashboardPage />}
                />
                <Route path="billing/invoices" element={<InvoicesPage />} />
                <Route path="billing/b2b" element={<B2BBillingPage />} />
                <Route
                  path="billing/plans"
                  element={<SubscriptionPlansPage />}
                />
                <Route path="menus" element={<MenusPage />} />
                <Route path="users" element={<UsersPage />} />
                <Route path="users/:id" element={<UsersPage />} />
                <Route path="roles" element={<RolesPage />} />
                <Route path="roles/:id" element={<RolesPage />} />
                <Route
                  path="notification-demo"
                  element={<NotificationDemo />}
                />
                {/* Rotas de Atividades com IA (Modelo Antigo) */}
                <Route path="activities" element={<ActivityListPage />} />
                <Route path="activities/new" element={<ActivityCreatePage />} />
                <Route path="activities/:id/edit" element={<ActivityEditPage />} />
                <Route path="pendencies" element={<PendencyBoardPage />} />
                
                {/* Rotas do Kanban Board (Novo Modelo) */}
                <Route path="kanban" element={<KanbanBoardPage />} />
                <Route path="kanban/new" element={<KanbanCardCreatePage />} />
                <Route path="kanban/analytics" element={<KanbanAnalyticsPage />} />
              </Route>

              {/* 404 Page */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </div>
        </ThemeProvider>
      </AuthProvider>
    </AppErrorBoundary>
  );
}

export default App;
