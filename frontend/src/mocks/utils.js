export const createSuccessResponse = (data, status = 200) => {
    return {
        code: status,
        data
    }
}

export const createErrorResponse = (title, message, status) => {
    return {
        code: status,
        title,
        message
    }
}