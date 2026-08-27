import React from 'react';
import { Navigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';
import { ShieldAlert, ArrowLeft, LayoutDashboard, Lock } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, role, isAuthenticated } = useAuth();

  if (!isAuthenticated || !role || !user) {
    return <Navigate to="/login" replace />;
  }

  /*
   * FUTURE FASTAPI AUTHORIZATION CHECK:
   * Evaluate claims from decoded JWT token or call GET /api/v1/auth/authorize?route=...
   */
  const isAuthorized = allowedRoles.includes(role);

  if (!isAuthorized) {
    const getTargetDashboard = (userRole: UserRole) => {
      switch (userRole) {
        case 'farmer':
          return '/';
        case 'agronomist':
          return '/agronomist/dashboard';
        case 'org_admin':
          return '/organization/dashboard';
        default:
          return '/';
      }
    };

    const targetDashboard = getTargetDashboard(role);

    return (
      <div className="min-h-screen bg-field-canvas flex items-center justify-center p-6">
        <div className="bg-pure-surface border border-structural rounded-2xl p-8 max-w-md w-full shadow-sm text-center">
          <div className="w-16 h-16 bg-red-50 text-alert-red rounded-full flex items-center justify-center mx-auto mb-5">
            <ShieldAlert size={32} />
          </div>

          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-gray-100 text-muted-leaf text-xs font-mono font-medium rounded-full mb-3">
            <Lock size={12} /> RESTRICTED ACCESS
          </span>

          <h2 className="text-xl font-bold text-field-ink mb-2">Access Denied</h2>

          <p className="text-sm text-muted-leaf mb-6">
            Your current role (<span className="font-semibold text-field-ink capitalize">{role.replace('_', ' ')}</span>) does not have permission to access this portal page.
          </p>

          <div className="bg-field-canvas p-4 rounded-xl border border-structural mb-6 text-left text-xs text-muted-leaf space-y-1">
            <p className="font-medium text-field-ink">Role Access Scope:</p>
            <p>• Farmers access field scans & crop reports.</p>
            <p>• Agronomists access review queues & evidence verification.</p>
            <p>• Organization Admins access farm analytics & team settings.</p>
          </div>

          <Link
            to={targetDashboard}
            className="inline-flex items-center justify-center gap-2 w-full py-3 px-5 bg-field-ink text-white font-medium text-sm rounded-xl hover:bg-opacity-90 transition"
          >
            <LayoutDashboard size={16} />
            Return to {role.replace('_', ' ')} Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
