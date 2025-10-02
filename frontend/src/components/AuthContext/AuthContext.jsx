import {useEffect, useState} from "react";
import {api} from "@/services/api.js";
import {AuthContext} from "./UseAuth.jsx";

export function AuthProvider({children}) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        initializeAuth();
    }, []);

    const initializeAuth = async () => {
        try {
            const response = await api.getCurrentUser();

            if (response.status === 200) {
                setUser(response.data.data);
            }
        } catch (error) {
            console.error('Auth initialization failed:', error);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
            const response = await api.login({email, password});

            if (response.status === 204) {
                const userResponse = await api.getCurrentUser();
                if (userResponse.status === 200) {
                    setUser(userResponse.data.data);
                    return {success: true, user: userResponse.data.data};
                }
            }

            return {success: false, message: response.data?.message || 'Login failed'};
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                message: error.response?.data?.message || error.message || 'Login failed'
            };
        }
    };

    const logout = async () => {
        try {
            await api.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{
            user,
            login,
            logout,
            loading,
            isAuthenticated: !!user
        }}>
            {children}
        </AuthContext.Provider>
    )
}