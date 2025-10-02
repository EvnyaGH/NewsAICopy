import React, {useState} from 'react';
import {useAuth} from '../components/AuthContext/UseAuth';
import {Link, Navigate} from 'react-router-dom';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {api} from '@/services/api';

const RegisterPage = () => {
    const {user, loading} = useAuth();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        displayName: '',
        firstName: '',
        lastName: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    if (user) {
        return <Navigate to="/" replace/>;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        // Validate passwords match
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            setIsLoading(false);
            return;
        }

        try {
            const response = await api.register({
                email: formData.email,
                password: formData.password,
                display_name: formData.displayName,
                first_name: formData.firstName,
                last_name: formData.lastName
            });

            if (response.status === 204) {
                setSuccess(true);
            }
        } catch (error) {
            setError(error.response?.data?.message || 'Registration failed');
        }

        setIsLoading(false);
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <div className="text-lg">Loading...</div>
            </div>
        );
    }

    if (success) {
        return (
            <div
                className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-8">
                <Card className="border-0 shadow-xl w-full max-w-md">
                    <CardHeader className="text-center pb-8">
                        <CardTitle className="text-2xl font-semibold text-green-600">Registration
                            Successful!</CardTitle>
                        <CardDescription className="text-gray-600 text-base mt-4">
                            We've sent a verification email to <strong>{formData.email}</strong>.
                            Please check your inbox and click the verification link to activate your account.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="text-center pb-8">
                        <Link to="/login">
                            <Button className="bg-green-600 hover:bg-green-700">
                                Back to Login
                            </Button>
                        </Link>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
            <div className="flex min-h-screen">
                {/* Left side with branding */}
                <div
                    className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-green-600 to-green-800 relative overflow-hidden">
                    <div className="absolute inset-0 bg-black/20"></div>
                    <div className="relative z-10 flex flex-col justify-center px-8 xl:px-16 text-white w-full">
                        <div className="max-w-lg">
                            <h1 className="text-4xl xl:text-5xl font-bold mb-6">Join NewsAI</h1>
                            <p className="text-xl xl:text-2xl mb-8 leading-relaxed">
                                Create your account and start your personalized news journey today.
                            </p>
                            <div className="space-y-4">
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                                    <span className="text-lg">Free account creation</span>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                                    <span className="text-lg">Instant access to news feed</span>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                                    <span className="text-lg">Personalized recommendations</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="absolute top-20 right-20 w-32 h-32 border border-white/20 rounded-full"></div>
                    <div className="absolute bottom-32 right-32 w-16 h-16 border border-white/30 rounded-full"></div>
                    <div className="absolute top-1/2 right-8 w-8 h-8 border border-white/40 rounded-full"></div>
                </div>

                {/* Right side with registration form */}
                <div className="flex-1 lg:flex-1 flex items-center justify-center p-8 lg:p-16">
                    <div className="w-full max-w-lg">
                        <div className="text-center mb-8 lg:hidden">
                            <h2 className="text-3xl font-bold text-gray-900">NewsAI</h2>
                            <p className="mt-2 text-gray-600">AI-powered news platform</p>
                        </div>

                        <Card className="border-0 shadow-xl w-full">
                            <CardHeader className="space-y-1 pb-8">
                                <CardTitle className="text-2xl xl:text-3xl font-semibold text-center">
                                    Create Account
                                </CardTitle>
                                <CardDescription className="text-center text-gray-600 text-base">
                                    Enter your details to create your NewsAI account
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6 pb-8">
                                <form onSubmit={handleSubmit} className="space-y-6">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label htmlFor="firstName" className="text-sm font-medium text-gray-700">
                                                First Name
                                            </Label>
                                            <Input
                                                id="firstName"
                                                name="firstName"
                                                type="text"
                                                value={formData.firstName}
                                                onChange={handleChange}
                                                placeholder="John"
                                                className="h-12 text-base"
                                                required
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="lastName" className="text-sm font-medium text-gray-700">
                                                Last Name
                                            </Label>
                                            <Input
                                                id="lastName"
                                                name="lastName"
                                                type="text"
                                                value={formData.lastName}
                                                onChange={handleChange}
                                                placeholder="Doe"
                                                className="h-12 text-base"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="displayName" className="text-sm font-medium text-gray-700">
                                            Display Name
                                        </Label>
                                        <Input
                                            id="displayName"
                                            name="displayName"
                                            type="text"
                                            value={formData.displayName}
                                            onChange={handleChange}
                                            placeholder="johndoe"
                                            className="h-12 text-base"
                                            required
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                                            Email address
                                        </Label>
                                        <Input
                                            id="email"
                                            name="email"
                                            type="email"
                                            value={formData.email}
                                            onChange={handleChange}
                                            placeholder="john@example.com"
                                            className="h-12 text-base"
                                            required
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                                            Password
                                        </Label>
                                        <Input
                                            id="password"
                                            name="password"
                                            type="password"
                                            value={formData.password}
                                            onChange={handleChange}
                                            placeholder="Enter password"
                                            className="h-12 text-base"
                                            required
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                                            Confirm Password
                                        </Label>
                                        <Input
                                            id="confirmPassword"
                                            name="confirmPassword"
                                            type="password"
                                            value={formData.confirmPassword}
                                            onChange={handleChange}
                                            placeholder="Confirm password"
                                            className="h-12 text-base"
                                            required
                                        />
                                    </div>

                                    {error && (
                                        <div
                                            className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                                            {error}
                                        </div>
                                    )}

                                    <Button
                                        type="submit"
                                        className="w-full h-12 text-base bg-green-600 hover:bg-green-700 focus:ring-green-500"
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'Creating Account...' : 'Create Account'}
                                    </Button>
                                </form>

                                <div className="pt-6 border-t border-gray-100 text-center">
                                    <p className="text-sm text-gray-600">
                                        Already have an account?{' '}
                                        <Link to="/login" className="text-green-600 hover:text-green-700 font-medium">
                                            Sign in here
                                        </Link>
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;