import { Navigate, Route, Routes } from "react-router-dom";
import type { ReactNode } from "react";
import UserSelectionPage from "./pages/user-selection-page";
import TechniciansPage from "./pages/technicians-page";
import ForemenPage from "./pages/foremen-page";
import { CurrentUser, getCurrentUser, getToken } from "./shared/auth";

type ProtectedRouteProps = {
  children: ReactNode;
  role?: CurrentUser["role"];
};

const ProtectedRoute = ({ children, role }: ProtectedRouteProps) => {
  const user = getCurrentUser();
  if (!getToken() || !user) {
    return <Navigate to="/" replace />;
  }
  if (role && user.role !== role) {
    return <Navigate to="/" replace />;
  }
  return children;
};

const App = () => {
  return (
    <div>
      <Routes>
        <Route path="/" element={<UserSelectionPage />} />
        <Route
          path="/technicians/:id"
          element={
            <ProtectedRoute role="technician">
              <TechniciansPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/foremen"
          element={
            <ProtectedRoute role="foreman">
              <ForemenPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
};

export default App;
