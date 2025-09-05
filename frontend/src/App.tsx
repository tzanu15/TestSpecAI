import { Spin } from 'antd'
import { Suspense, lazy } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { Layout } from './components/common/Layout'
import { ProtectedRoute } from './components/common/ProtectedRoute'
import { PageTransition } from './components/common/PageTransition'

// Lazy load page components
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(module => ({ default: module.DashboardPage })))
const RequirementsPage = lazy(() => import('./pages/RequirementsPage').then(module => ({ default: module.RequirementsPage })))
const TestSpecsPage = lazy(() => import('./pages/TestSpecsPage').then(module => ({ default: module.TestSpecsPage })))
const ParametersPage = lazy(() => import('./pages/ParametersPage').then(module => ({ default: module.ParametersPage })))
const CommandsPage = lazy(() => import('./pages/CommandsPage').then(module => ({ default: module.CommandsPage })))
const LoginPage = lazy(() => import('./pages/LoginPage').then(module => ({ default: module.LoginPage })))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage').then(module => ({ default: module.NotFoundPage })))

function App() {
  const location = useLocation()
  
  return (
    <Layout>
      <Suspense
        fallback={
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '200px'
          }}>
            <Spin size="large" />
          </div>
        }
      >
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/login" element={
              <PageTransition>
                <LoginPage />
              </PageTransition>
            } />
            <Route path="/" element={
              <ProtectedRoute requireAuth={false}>
                <PageTransition>
                  <DashboardPage />
                </PageTransition>
              </ProtectedRoute>
            } />
            <Route path="/requirements" element={
              <ProtectedRoute requireAuth={false}>
                <PageTransition>
                  <RequirementsPage />
                </PageTransition>
              </ProtectedRoute>
            } />
            <Route path="/test-specs" element={
              <ProtectedRoute requireAuth={false}>
                <PageTransition>
                  <TestSpecsPage />
                </PageTransition>
              </ProtectedRoute>
            } />
            <Route path="/parameters" element={
              <ProtectedRoute requireAuth={false}>
                <PageTransition>
                  <ParametersPage />
                </PageTransition>
              </ProtectedRoute>
            } />
            <Route path="/commands" element={
              <ProtectedRoute requireAuth={false}>
                <PageTransition>
                  <CommandsPage />
                </PageTransition>
              </ProtectedRoute>
            } />
            <Route path="*" element={
              <PageTransition>
                <NotFoundPage />
              </PageTransition>
            } />
          </Routes>
        </AnimatePresence>
      </Suspense>
    </Layout>
  )
}

export default App
