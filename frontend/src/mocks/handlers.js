import {http, HttpResponse} from 'msw'
import {createErrorResponse, createSuccessResponse} from './utils'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

// mock user
const mockUser = {
    id: "6b7b2a55-8d8b-4a22-86d6-2b8b0c9a3c11",
    email: "test@example.com",
    display_name: "Test User",
    first_name: "Test",
    last_name: "User",
    role: [{id: "1", name: "USER"}],
    email_verified_at: "2024-09-18T12:34:56Z",
    profile_image_url: "https://cdn.example.com/u/123.png",
    created_at: "2024-09-18T12:34:56Z",
    updated_at: "2024-09-18T12:34:56Z"
}

// Category ingore case check
const hasCategory = (arr, target) =>
    Array.isArray(arr) &&
    typeof target === "string" &&
    arr.some((c) => c.toLowerCase() === target.toLowerCase());


// Field lists for interests
const FIELDS = [
    { slug: 'mathematics', name: 'Mathematics', subtopics: ['Probability', 'Statistics', 'Optimization', 'Algebra'] },
    { slug: 'computer-science', name: 'Computer Science', subtopics: ['AI', 'Databases', 'Systems', 'HCI'] },
    { slug: 'physics', name: 'Physics', subtopics: ['Astrophysics', 'Condensed Matter', 'High Energy Physics', 'Quantum Physics'] },
    { slug: 'biology', name: 'Biology', subtopics: ['Genetics', 'Epidemiology', 'Neuroscience', 'Immunology'] },
];

// Interests of the mock user
let mockUserInterests = {
    fields: ['computer-science', 'mathematics'],
    subtopics: ['AI', 'Statistics'],
};


export const handlers = [
    // login
    http.post(`${API_BASE_URL}/api/v1/login`, async ({request}) => {
        const credentials = await request.json()

        if (!credentials.email || !credentials.password) {
            return HttpResponse.json(
                {
                    code: 400,
                    title: "Bad Request",
                    message: "Email and password are required"
                },
                {status: 400}
            )
        }

        if (credentials.email === 'test@example.com' && credentials.password === 'password123') {
            return new HttpResponse(null, {status: 204});
        }

        return HttpResponse.json(
            {
                code: 401,
                title: "InvalidCredentialsError",
                message: "Invalid credentials"
            },
            {status: 401}
        )
    }),

    // get current user
    http.get(`${API_BASE_URL}/api/v1/users/me`, async () => {
        return HttpResponse.json(
            {
                code: 200,
                data: mockUser
            },
            {status: 200}
        );
        // return HttpResponse.json(
        //     {
        //         code: 401,
        //         title: "AuthenticationError",
        //         message: "AuthenticationError"
        //     },
        //     {status: 401}
        // );
    }),

    // logout
    http.post(`${API_BASE_URL}/api/v1/logout`, async () => {
        return new HttpResponse(null, {status: 204});
    }),

    // register
    http.post(`${API_BASE_URL}/api/v1/register`, async ({request}) => {
        const userData = await request.json()

        if (!userData.email || !userData.password) {
            return HttpResponse.json(
                createErrorResponse("ValidationError", "Email and password are required", 422),
                {status: 422}
            )
        }

        return new HttpResponse(null, {status: 204});
    }),

    // verify email
    http.post(`${API_BASE_URL}/api/v1/verify-email`, async ({request}) => {
        const {token} = await request.json();

        if (!token) {
            return HttpResponse.json(
                createErrorResponse("InvalidVerificationTokenError", "Invalid verification token", 400),
                {status: 400}
            )
        }

        return new HttpResponse(null, {status: 204});
    }),

    // resend email verification
    http.post(`${API_BASE_URL}/api/v1/resend-email-verification`, async ({request}) => {
        const {email, password} = await request.json();

        if (!email || !password) {
            return HttpResponse.json(
                createErrorResponse("InvalidCredentialsError", "Email and password are required", 401),
                {status: 401}
            )
        }

        return new HttpResponse(null, {status: 204});
    }),

    // // get news feed without category
    // http.get(`${API_BASE_URL}/api/v1/news/feed`, async ({request}) => {
    //     const url = new URL(request.url);
    //     const page = parseInt(url.searchParams.get('page')) || 1;
    //     const limit = parseInt(url.searchParams.get('limit')) || 10;
    //
    //     // Mock articles data
    //     const mockArticles = Array.from({length: limit}, (_, index) => ({
    //         id: `article-${(page - 1) * limit + index + 1}`,
    //         title: `News ${(page - 1) * limit + index + 1}: Important News Content and Latest Developments`,
    //         summary: `This is a news summary containing important information and key points. The news content covers various aspects including politics, economy, society and other important events and developments in different fields.`,
    //         content: `This is the complete news content. The first paragraph contains the main information and background of the news.\n\nSecond paragraph describes the specific situation and impact of the event in detail.\n\nThird paragraph analyzes the causes and possible consequences of the event.\n\nFourth paragraph provides relevant data and statistics.\n\nFifth paragraph summarizes the importance of the news and its impact on the public.`,
    //         source: `News Source ${index + 1}`,
    //         image_url: `https://picsum.photos/800/400?random=${(page - 1) * limit + index + 1}`,
    //         published_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
    //         categories: ['Technology', 'Politics', 'Economy', 'Society'].slice(0, Math.floor(Math.random() * 3) + 1),
    //         url: `https://example.com/article/${(page - 1) * limit + index + 1}`,
    //         author: `Author ${index + 1}`,
    //         reading_time: Math.floor(Math.random() * 10) + 3
    //     }));
    //
    //     return HttpResponse.json(
    //         createSuccessResponse({
    //             articles: mockArticles,
    //             pagination: {
    //                 page,
    //                 limit,
    //                 total: 100,
    //                 total_pages: Math.ceil(100 / limit),
    //                 has_next: page < Math.ceil(100 / limit),
    //                 has_prev: page > 1
    //             }
    //         })
    //     );
    // }),


    // get news feed with optional category filter
    http.get(`${API_BASE_URL}/api/v1/news/feed`, async ({ request }) => {
        const url = new URL(request.url);
        const page = parseInt(url.searchParams.get("page")) || 1;
        const limit = parseInt(url.searchParams.get("limit")) || 10;
        const category = url.searchParams.get("category"); // 可能为 null

        // Mock articles data
        const mockArticles = Array.from({ length: limit }, (_, index) => ({
            id: `article-${(page - 1) * limit + index + 1}`,
            title: `News ${(page - 1) * limit + index + 1}: Important News Content and Latest Developments`,
            summary:
                "This is a news summary containing important information and key points. The news content covers various aspects including politics, economy, society and other important events and developments in different fields.",
            content:
                "This is the complete news content. The first paragraph contains the main information and background of the news.\n\nSecond paragraph describes the specific situation and impact of the event in detail.\n\nThird paragraph analyzes the causes and possible consequences of the event.\n\nFourth paragraph provides relevant data and statistics.\n\nFifth paragraph summarizes the importance of the news and its impact on the public.",
            source: `News Source ${index + 1}`,
            image_url: `https://picsum.photos/800/400?random=${(page - 1) * limit + index + 1}`,
            published_at: new Date(
                Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000
            ).toISOString(),
            // 随机 1~3 个分类
            categories: ["Physics", "Mathematics", "Computer", "Engineering"].slice(
                0,
                Math.floor(Math.random() * 3) + 1
            ),
            url: `https://example.com/article/${(page - 1) * limit + index + 1}`,
            author: `Author ${index + 1}`,
            reading_time: Math.floor(Math.random() * 10) + 3,
        }));

        // with category filter
        const filtered = category
            ? mockArticles.filter((a) => hasCategory(a.categories, category))
            : mockArticles;

        return HttpResponse.json(
            createSuccessResponse({
                articles: filtered,
                pagination: {
                    page,
                    limit,
                    total: 100,
                    total_pages: Math.ceil(100 / limit),
                    has_next: page < Math.ceil(100 / limit),
                    has_prev: page > 1,
                },
            })
        );
    }),

    // get article detail
    http.get(`${API_BASE_URL}/api/v1/news/articles/:articleId`, async ({params}) => {
        const {articleId} = params;

        // Mock article detail
        const mockArticle = {
            id: articleId,
            title: `Detailed News Title: ${articleId}`,
            summary: `This is a detailed news summary containing complete information and background. This news event has important social significance and deserves in-depth analysis and discussion.`,
            content: `This is the complete news content.\n\nFirst paragraph: Basic situation and background introduction of the news event. This event occurred in recent days and has attracted widespread attention and discussion.\n\nSecond paragraph: Detailed description of the specific process of the event. Including time, location, personnel and institutions involved and other key information.\n\nThird paragraph: Analysis of the causes and impact of the event. From multiple perspectives, it explores the background of the event and the possible consequences it may bring.\n\nFourth paragraph: Provides relevant data and statistical information. Including official responses, expert opinions and public reactions.\n\nFifth paragraph: Summarizes the importance of the news and its significance to society. Emphasizes the impact of this event on related fields and public life.\n\nSixth paragraph: Looks forward to future development trends. Analyzes the possible development direction of the event and issues that need attention.`,
            source: 'Authoritative News Source',
            image_url: `https://picsum.photos/1200/600?random=${articleId}`,
            published_at: new Date(Date.now() - Math.random() * 3 * 24 * 60 * 60 * 1000).toISOString(),
            categories: ['Technology', 'Politics', 'Economy'],
            url: `https://example.com/article/${articleId}`,
            author: 'Senior Reporter',
            reading_time: 8,
            views: Math.floor(Math.random() * 10000) + 1000,
            likes: Math.floor(Math.random() * 500) + 50,
            shares: Math.floor(Math.random() * 100) + 10
        };

        return HttpResponse.json(
            createSuccessResponse(mockArticle)
        );
    }),



    // get all fields and subtopics
    http.get(`${API_BASE_URL}/api/v1/fields`, () => {
        return HttpResponse.json(createSuccessResponse(FIELDS));
    }),

    // get interests
    http.get(`${API_BASE_URL}/api/v1/users/me/interests`, () => {
        return HttpResponse.json(createSuccessResponse(mockUserInterests));
    }),

    // update interests
    http.put(`${API_BASE_URL}/api/v1/users/me/interests`, async ({ request }) => {
        const body = await request.json().catch(() => ({}));
        const { fields = [], subtopics = [] } = body || {};
        mockUserInterests = { fields, subtopics };
        return HttpResponse.json(createSuccessResponse(mockUserInterests));
    }),
]