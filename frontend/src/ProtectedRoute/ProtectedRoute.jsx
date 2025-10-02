import {Navigate, Outlet} from "react-router-dom";
import {useAuth} from "@/components/AuthContext/UseAuth.jsx";

export default function ProtectedRoute() {
    const {user, loading} = useAuth();

    if (loading) return <div>Loading...</div>;
    if (!user) return <Navigate to="/login" replace/>;
    return <Outlet/>;
}