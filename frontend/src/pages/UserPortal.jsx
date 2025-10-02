import React from 'react';
import { useAuth } from '../components/AuthContext/UseAuth';
import Feed from '../components/Feed/Feed';
import CategoryBar from '../components/Feed/CategoryBar';
import { useParams } from 'react-router-dom';


const CATEGORIES = [
    "Physics","Mathematics","Computer","Quantitative Biology",
    "Quantitative Finance","Statistics","Engineering","Economics"
];


const deslug = (slug) => (slug ? slug.replace(/-/g, " ") : null);

const UserPortal = () => {
    const { isAuthenticated, user, logout } = useAuth();
    const navigate = useNavigate();

    const handleSearchClick = () => {
        navigate('/search');
    };

    const handleSavedArticlesClick = () => {
        navigate('/saved');
    };

    const { category: categorySlug } = useParams(); // 可能是 undefined
    const currentCategory = categorySlug ? deslug(categorySlug) : null;


    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-5 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-blue-600">NewsAI</h1>
                    <div className="flex items-center gap-4">
                        {/* Search Button */}
                        <button
                            onClick={handleSearchClick}
                            className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        >
                            <Search className="h-4 w-4"/>
                            <span className="hidden sm:inline">Search</span>
                        </button>

                        {/* Saved Articles Button */}
                        <button
                            onClick={handleSavedArticlesClick}
                            className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        >
                            <Bookmark className="h-4 w-4"/>
                            <span className="hidden sm:inline">Saved</span>
                        </button>

                        {isAuthenticated && user && (
                            <div className="flex items-center gap-4 md:gap-6 flex-wrap md:flex-nowrap">
                            <span className="text-gray-700">
                                Welcome, {user.display_name || user.first_name}
                            </span>
                                <button
                                    onClick={logout}
                                    className="h-10 px-4 text-sm md:text-base !bg-red-600 !text-white !hover:bg-red-600 !transition-none rounded"
                                >
                                    Logout
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </header>

            {/* Main content */}
            <main className="max-w-7xl mx-auto px-5 py-5">
                <CategoryBar categories={CATEGORIES} current={currentCategory}/>
                <Feed category={currentCategory}/>
            </main>
        </div>
);
};

export default UserPortal;
