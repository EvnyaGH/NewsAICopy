import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { api } from "../../services/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const ArticleDetail = () => {
    const { articleId } = useParams();
    const navigate = useNavigate();
    const [article, setArticle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadArticle = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await api.getArticle(articleId);
                if (response.data?.code === 200) {
                    setArticle(response.data.data);
                } else {
                    setError(response.data?.message || "Failed to load article");
                }
            } catch (err) {
                console.error(err);
                setError(err.response?.data?.message || "Failed to load article");
            } finally {
                setLoading(false);
            }
        };
        if (articleId) loadArticle();
    }, [articleId]);

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString("zh-CN", {
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    if (loading)
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-gray-600">
                <div className="h-10 w-10 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin mb-4"></div>
                <p>Loading article...</p>
            </div>
        );

    if (error)
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-center">
                <h2 className="text-xl font-bold text-red-600 mb-2">Failed to Load</h2>
                <p className="mb-4">{error}</p>
                <Button variant="outline" onClick={() => navigate(-1)}>
                    Back to Articles
                </Button>
            </div>
        );

    if (!article)
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-center">
                <h2 className="text-xl font-bold text-gray-700 mb-2">Article Not Found</h2>
                <p className="mb-4">Sorry, the article you are looking for does not exist or has been deleted.</p>
                <Button variant="outline" onClick={() => navigate(-1)}>
                    Back to Articles
                </Button>
            </div>
        );

    return (
        <div className="max-w-3xl mx-auto px-4 py-8">
            <Helmet>
                <title>{article.title} - NewsAI</title>
                <meta name="description" content={article.summary} />
                <meta name="keywords" content={article.categories?.join(", ")} />
                <meta name="author" content={article.author || article.source} />
            </Helmet>

            {/* Header with Back button */}
            <div className="mb-6 flex items-center justify-between">
                <Button variant="outline" onClick={() => navigate(-1)}>
                    ← Back
                </Button>
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">{article.title}</h1>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                        <span>{article.source}</span>
                        <span>{formatDate(article.published_at)}</span>
                    </div>
                </div>
            </div>

            {/* Image */}
            {article.image_url && (
                <div className="mb-6">
                    <img src={article.image_url} alt={article.title} className="w-full rounded-lg shadow" />
                </div>
            )}

            {/* Content */}
            <div className="prose max-w-none mb-8">
                <div className="text-gray-700 mb-4">
                    <p>{article.summary}</p>
                </div>
                <div className="space-y-4">
                    {article.content.split("\n").map((paragraph, index) => (
                        <p key={index} className="text-gray-800 leading-relaxed">
                            {paragraph}
                        </p>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between border-t pt-4">
                <div className="flex flex-wrap gap-2">
                    {article.categories?.map((category, index) => (
                        <Badge key={index} variant="secondary">
                            {category}
                        </Badge>
                    ))}
                </div>
                <div className="flex gap-2">
                    <Button variant="outline">Share</Button>
                    <Button>Bookmark</Button>
                </div>
            </div>
        </div>
    );
};

export default ArticleDetail;
