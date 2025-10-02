import React, {useEffect, useState} from 'react';
import {useAuth} from '../components/AuthContext/UseAuth';
import {Link, Navigate, useSearchParams} from 'react-router-dom';
import {Button} from '@/components/ui/button';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {api} from '@/services/api';

const VerifyEmailPage = () => {
    const {user, loading} = useAuth();
    const [searchParams] = useSearchParams();
    const [verificationState, setVerificationState] = useState('verifying'); // 'verifying', 'success', 'error'
    const [error, setError] = useState('');

    const token = searchParams.get('token');

    useEffect(() => {
        if (token) {
            verifyEmail(token);
        } else {
            setVerificationState('error');
            setError('No verification token provided');
        }
    }, [token]);

    const verifyEmail = async (token) => {
        try {
            const response = await api.verifyEmail(token);

            if (response.status === 204) {
                setVerificationState('success');
            }
        } catch (error) {
            setVerificationState('error');
            setError(error.response?.data?.message || 'Email verification failed');
        }
    };

    if (user) {
        return <Navigate to="/" replace/>;
    }

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <div className="text-lg">Loading...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-8">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-gray-900">NewsAI</h2>
                    <p className="mt-2 text-gray-600">Email Verification</p>
                </div>

                <Card className="border-0 shadow-xl w-full">
                    <CardHeader className="text-center pb-8">
                        {verificationState === 'verifying' && (
                            <>
                                <CardTitle className="text-2xl font-semibold text-green-600">Verifying
                                    Email...</CardTitle>
                                <CardDescription className="text-gray-600 text-base mt-4">
                                    Please wait while we verify your email address.
                                </CardDescription>
                            </>
                        )}

                        {verificationState === 'success' && (
                            <>
                                <CardTitle className="text-2xl font-semibold text-green-600">Email Verified!</CardTitle>
                                <CardDescription className="text-gray-600 text-base mt-4">
                                    Your email has been successfully verified. You can now sign in to your account.
                                </CardDescription>
                            </>
                        )}

                        {verificationState === 'error' && (
                            <>
                                <CardTitle className="text-2xl font-semibold text-red-600">Verification
                                    Failed</CardTitle>
                                <CardDescription className="text-gray-600 text-base mt-4">
                                    {error}
                                </CardDescription>
                            </>
                        )}
                    </CardHeader>

                    <CardContent className="text-center pb-8">
                        {verificationState === 'verifying' && (
                            <div className="flex justify-center">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                            </div>
                        )}

                        {verificationState === 'success' && (
                            <Link to="/login">
                                <Button className="bg-green-600 hover:bg-green-700">
                                    Sign In Now
                                </Button>
                            </Link>
                        )}

                        {verificationState === 'error' && (
                            <div className="flex flex-col space-y-4">
                                <Link to="/register">
                                    <Button variant="outline"
                                            className="w-full border-green-600 text-green-600 hover:bg-green-50">
                                        Try Registration Again
                                    </Button>
                                </Link>
                                <Link to="/login">
                                    <Button className="w-full bg-green-600 hover:bg-green-700">
                                        Back to Login
                                    </Button>
                                </Link>
                            </div>
                        )}


                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default VerifyEmailPage;