import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Start MSW when enabled in environment
async function enableMocking() {
    // Enable MSW based on environment variable
    if (import.meta.env.VITE_APP_USE_MSW === 'true') {
        const {worker} = await import('./mocks/browser')
        return worker.start({
            onUnhandledRequest: 'bypass',
        })
    }
}

enableMocking().then(() => {
    createRoot(document.getElementById('root')).render(
        <StrictMode>
            <App/>
        </StrictMode>,
    )
})