import { Navigate, Outlet } from 'react-router-dom'

export default function PrivateRoute({token}) {
  return token != null ? <Outlet /> : <Navigate to='/login' />;
}