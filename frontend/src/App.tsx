import { useState } from 'react';
import { DashboardLayout, type NavigationPage } from './components';
import { Dashboard, Analytics } from './pages';

function App() {
  const [currentPage, setCurrentPage] = useState<NavigationPage>('dashboard');

  return (
    <DashboardLayout
      activePage={currentPage}
      onNavigate={setCurrentPage}
      title={
        currentPage === 'dashboard'
          ? 'National Wind Generation Dashboard'
          : 'Forecast Accuracy & Performance Analytics'
      }
      subtitle={
        currentPage === 'dashboard'
          ? 'Live GB electricity settlement outturn and wind generation monitoring.'
          : 'MAE, RMSE, and bias evaluation comparing Elexon WINDFOR against FUELHH actuals.'
      }
    >
      {currentPage === 'dashboard' && <Dashboard />}
      {currentPage === 'analytics' && <Analytics />}
    </DashboardLayout>
  );
}

export default App;
