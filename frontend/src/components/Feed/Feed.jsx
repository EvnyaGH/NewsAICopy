import React, {useState, useEffect, useCallback, useMemo} from "react";
import { useAuth } from "../AuthContext/UseAuth";
import { api } from "../../services/api";
import FeedItem from "./FeedItem";
import { Button } from "@/components/ui/button";

const Feed = ({ category = null }) => {
    const { isAuthenticated, user } = useAuth();
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);

    const loadArticles = useCallback(async (pageNum = 1, reset = false) => {
        try {
            if (pageNum === 1) {
                setLoading(true);
                setError(null);
            } else {
                setLoadingMore(true);
            }

            const response = await api.getFeed(pageNum, 10);

            if (response.data?.code === 200) {
                const newArticles = response.data.data.articles || [];
                if (reset) setArticles(newArticles);
                else setArticles((prev) => [...prev, ...newArticles]);
                setHasMore(newArticles.length === 10);
                setPage(pageNum);
            } else {
                setError(response.data?.message || "Failed to load articles");
            }
        } catch (err) {
            console.error("Error loading articles:", err);
            setError(err.response?.data?.message || "Failed to load articles");
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    }, []);

    useEffect(() => {
        loadArticles(1, true);
    }, [loadArticles]);

    const loadMore = useCallback(() => {
        if (!loadingMore && hasMore) loadArticles(page + 1, false);
    }, [loadArticles, loadingMore, hasMore, page]);

    // 无限滚动
    useEffect(() => {
        const handleScroll = () => {
            if (
                window.innerHeight + document.documentElement.scrollTop >=
                document.documentElement.offsetHeight - 1000
            ) {
                loadMore();
            }
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, [loadMore]);

    // frontend filtering by category
    const visibleArticles = useMemo(() => {
        if (!category) return articles; // All
        return articles.filter(
            (a) =>
                Array.isArray(a.categories) &&
                a.categories.some((c) => c.toLowerCase() === category.toLowerCase())
        );
    }, [articles, category]);


    if (loading && articles.length === 0)
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-gray-600">
                <div className="h-10 w-10 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin mb-4"></div>
                <p>Loading news...</p>
            </div>
        );

    if (error)
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-center">
                <p className="mb-4 text-red-600">Failed to load: {error}</p>
                <Button onClick={() => loadArticles(1, true)}>Retry</Button>
            </div>
        );

    return (
        <div className="max-w-6xl mx-auto px-4 py-8">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">News Feed</h2>
                {isAuthenticated && user && (
                    <div className="text-sm text-gray-500">
                        Welcome back, {user.display_name || user.first_name}!
                    </div>
                )}
            </div>

            {/* 改为网格布局，每行 3 个 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {visibleArticles.map((article) => (
                    <FeedItem key={article.id} article={article} />
                ))}
            </div>

            {/* 加载更多 / 没有更多 */}
            <div className="mt-6 flex flex-col items-center text-gray-600">
                {loadingMore && (
                    <>
                        <div className="h-6 w-6 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin mb-2"></div>
                        <p className="text-sm">Loading more...</p>
                    </>
                )}
                {!hasMore && articles.length > 0 && !loadingMore && (
                    <p className="text-center text-gray-500 text-sm">No more content</p>
                )}
            </div>
        </div>
    );
};

export default Feed;
