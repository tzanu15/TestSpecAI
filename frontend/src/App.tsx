import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/common/Layout'
import { CommandsPage } from './pages/CommandsPage'
import { DashboardPage } from './pages/DashboardPage'
import { ParametersPage } from './pages/ParametersPage'
import { RequirementsPage } from './pages/RequirementsPage'
import { TestSpecsPage } from './pages/TestSpecsPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/requirements" element={<RequirementsPage />} />
        <Route path="/test-specs" element={<TestSpecsPage />} />
        <Route path="/parameters" element={<ParametersPage />} />
        <Route path="/commands" element={<CommandsPage />} />
      </Routes>
    </Layout>
  )
}

export default App
