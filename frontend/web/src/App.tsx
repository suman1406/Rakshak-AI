import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';

// Public Pages
import { LandingPage } from './screens/public/LandingPage';
import { AboutPage } from './screens/public/AboutPage';
import { HowItWorksPage } from './screens/public/HowItWorksPage';
import { PricingPage } from './screens/public/PricingPage';
import { ContactPage } from './screens/public/ContactPage';
import { PrivacyPage, TermsPage } from './screens/public/PrivacyPage';

// Auth Pages
import { LoginPage } from './screens/auth/LoginPage';
import { RegisterPage, ForgotPasswordPage } from './screens/auth/RegisterPage';
import { OnboardingPage } from './screens/auth/OnboardingPage';
import { ApplicationPage } from './screens/auth/ApplicationPage';
import { AdminDashboard } from './screens/admin/AdminDashboard';

// Agronomist Pages
import { AgronomistDashboard } from './screens/agronomist/AgronomistDashboard';
import { AgronomistCaseReviewPage } from './screens/agronomist/AgronomistCaseReviewPage';
import { AgronomistReportsPage } from './screens/agronomist/AgronomistReportsPage';

// Organization Pages
import { OrgDashboard } from './screens/organization/OrgDashboard';
import { OrgFarmDetailsPage } from './screens/organization/OrgFarmDetailsPage';
import { OrgFieldDetailsPage } from './screens/organization/OrgFieldDetailsPage';
import { OrgReportsPage } from './screens/organization/OrgReportsPage';

// Settings Pages
import { SettingsProfilePage } from './screens/settings/SettingsProfilePage';
import {
  SettingsOrgPage,
  SettingsNotificationsPage,
  SettingsSecurityPage,
} from './screens/settings/SettingsOrgPage';

export function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/terms" element={<TermsPage />} />

          {/* Authentication Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/apply/:kind" element={<ApplicationPage />} />
          <Route path="/admin/access" element={<LoginPage />} />

          {/* Agronomist Portal (Protected) */}
          <Route
            path="/agronomist"
            element={
              <ProtectedRoute allowedRoles={['agronomist', 'org_admin', 'admin', 'enterprise']}>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/agronomist/dashboard" replace />} />
            <Route path="dashboard" element={<AgronomistDashboard />} />
            <Route path="cases/:id" element={<AgronomistCaseReviewPage />} />
            <Route path="reports" element={<AgronomistReportsPage />} />
          </Route>

          {/* Organization Portal (Protected) */}
          <Route
            path="/organization"
            element={
              <ProtectedRoute allowedRoles={['org_admin', 'admin', 'enterprise']}>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/organization/dashboard" replace />} />
            <Route path="dashboard" element={<OrgDashboard />} />
            <Route path="farms/:id" element={<OrgFarmDetailsPage />} />
            <Route path="fields/:id" element={<OrgFieldDetailsPage />} />
            <Route path="reports" element={<OrgReportsPage />} />
          </Route>

          {/* Settings Routes (Protected) */}
          <Route
            path="/settings"
            element={
                <ProtectedRoute allowedRoles={['agronomist', 'org_admin', 'admin', 'enterprise']}>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/settings/profile" replace />} />
            <Route path="profile" element={<SettingsProfilePage />} />
            <Route path="organization" element={<SettingsOrgPage />} />
            <Route path="notifications" element={<SettingsNotificationsPage />} />
            <Route path="security" element={<SettingsSecurityPage />} />
          </Route>

          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="dashboard" element={<AdminDashboard />} />
          </Route>

          {/* Fallback Route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
