import React, {useState} from 'react';
import {useAuth} from '../components/AuthContext/UseAuth';
import {Link, Navigate} from 'react-router-dom';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';

const LoginPage = () => {
    const {user, login, loading} = useAuth();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    if (user) {
        return <Navigate to="/" replace/>;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        const result = await login(formData.email, formData.password);

        if (!result.success) {
            setError(result.message);
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

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
            <div className="flex min-h-screen">
                {/* left side with branding and features */}
                <div
                    className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-green-600 to-green-800 relative overflow-hidden">
                    <div className="absolute inset-0 bg-black/20"></div>
                    <div className="relative z-10 flex flex-col justify-center px-8 xl:px-16 text-white w-full">
                        <div className="max-w-lg">
                            <h1 className="text-4xl xl:text-5xl font-bold mb-6">NewsAI</h1>
                            <p className="text-xl xl:text-2xl mb-8 leading-relaxed">
                                Stay ahead with AI-powered news insights. Get personalized news feeds and intelligent
                                summaries.
                            </p>
                            <div className="space-y-4">
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                                    <span className="text-lg">Real-time news updates</span>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                                    <span className="text-lg">AI-powered content curation</span>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                                    <span className="text-lg">Personalized news experience</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* some decorative circles for visual appeal */}
                    <div className="absolute top-20 right-20 w-32 h-32 border border-white/20 rounded-full"></div>
                    <div className="absolute bottom-32 right-32 w-16 h-16 border border-white/30 rounded-full"></div>
                    <div className="absolute top-1/2 right-8 w-8 h-8 border border-white/40 rounded-full"></div>
                </div>

                {/* right side with the actual login form */}
                <div className="flex-1 lg:flex-1 flex items-center justify-center p-8 lg:p-16">
                    <div className="w-full max-w-lg">
                        {/* show logo on mobile when left side is hidden */}
                        <div className="text-center mb-8 lg:hidden">
                            <h2 className="text-3xl font-bold text-gray-900">NewsAI</h2>
                            <p className="mt-2 text-gray-600">AI-powered news platform</p>
                        </div>

                        <Card className="border-0 shadow-xl w-full">
                            <CardHeader className="space-y-1 pb-8">
                                <CardTitle className="text-2xl xl:text-3xl font-semibold text-center">
                                    Welcome back
                                </CardTitle>
                                <CardDescription className="text-center text-gray-600 text-base">
                                    Enter your credentials to access your account
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6 pb-8">
                                <form onSubmit={handleSubmit} className="space-y-6">
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
                                            placeholder="test@example.com"
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
                                            placeholder="password"
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
                                        {isLoading ? 'Signing in...' : 'Sign in'}
                                    </Button>
                                </form>

                                <div className="pt-6 border-t border-gray-100">
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-sm font-medium text-gray-700 mb-2">Demo credentials:</p>
                                        <p className="text-sm text-gray-600">
                                            Email: test@example.com<br/>
                                            Password: password123
                                        </p>
                                    </div>
                                </div>
                            </CardContent>

                            <div className="pt-4 text-center">
                                <p className="text-sm text-gray-600">
                                    Don't have an account?{' '}
                                    <Link to="/register" className="text-green-600 hover:text-green-700 font-medium">
                                        Sign up here
                                    </Link>
                                </p>
                            </div>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
