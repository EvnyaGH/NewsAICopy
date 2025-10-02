import React from 'react';
import { useNavigate } from 'react-router-dom';

const slugify = (name) =>
    (name || '')
        .toString()
        .toLowerCase()
        .trim()
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '');

export default function CategoryBar({ categories = [], current /* string|null */ }) {
    const navigate = useNavigate();
    const options = ['All', ...Array.from(new Set(categories)).filter(Boolean)];

    const currentSlug = current ? slugify(current) : '';  // '' 代表 All

    const goto = (label) => {
        if (label === 'All') navigate('/');
        else navigate(`/${slugify(label)}`);
    };

    return (
        <div className="w-full py-3">
            <div className="flex flex-wrap justify-center gap-2">
                {options.map((label) => {
                    const labelSlug = label === 'All' ? '' : slugify(label);
                    const selected = currentSlug === labelSlug;   // 用 slug 判断选中
                    return (
                        <button
                            key={label}
                            type="button"
                            onClick={() => goto(label)}
                            aria-pressed={selected}
                            className={
                                'px-3 py-1.5 rounded-full border text-sm transition ' +
                                (selected
                                    ? 'bg-blue-600 text-white border-blue-600'
                                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100')
                            }
                        >
                            {label}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}

