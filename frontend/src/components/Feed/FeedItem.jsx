import React from "react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";

const FeedItem = ({ article }) => {
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
        if (diffInHours < 1) return "Just now";
        if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? "s" : ""} ago`;
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays} day${diffInDays > 1 ? "s" : ""} ago`;
    };

    const truncateText = (text, maxLength = 200) => {
        if (!text) return "";
        return text.length <= maxLength ? text : text.substring(0, maxLength) + "...";
    };

    return (
        <article className="relative flex flex-col border rounded-lg shadow-sm p-4 bg-white hover:shadow-md transition h-full">
            {article.image_url && (
                <div className="w-full h-40 overflow-hidden rounded-md mb-3">
                    <img src={article.image_url} alt={article.title} loading="lazy" className="w-full h-full object-cover" />
                </div>
            )}

            <div className="flex-1 flex flex-col">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{article.title}</h3>
                <div className="text-xs text-gray-500 mb-2">{formatDate(article.published_at)}</div>
                <p className="text-sm text-gray-700 mb-12">{truncateText(article.summary || article.content, 160)}</p>
            </div>

            <div className="flex items-center justify-between absolute bottom-4 left-4 right-4">
                <div className="flex flex-wrap gap-2">
                    {article.categories?.map((category, idx) => (
                        <Badge key={idx} variant="secondary">
                            {category}
                        </Badge>
                    ))}
                </div>
                <Link to={`/article/${article.id}`} className="text-sm text-blue-600 hover:underline">
                    Read more
                </Link>
            </div>
        </article>
    );
};

export default FeedItem;
