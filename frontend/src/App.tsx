import { BrowserRouter, Route, Routes } from "react-router-dom";
import { NavTabs } from "./components/NavTabs";
import { PasswordGate } from "./components/PasswordGate";
import { ViewerToggle } from "./components/ViewerToggle";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ViewerProvider } from "./context/ViewerContext";
import { BrowsePage } from "./pages/BrowsePage";
import { FavoritesPage } from "./pages/FavoritesPage";
import { ShortlistPage } from "./pages/ShortlistPage";

function AppShell() {
  const { authenticated } = useAuth();

  if (authenticated === null) return null;
  if (!authenticated) return <PasswordGate />;

  return (
    <ViewerProvider>
      <BrowserRouter>
        <header className="app-header">
          <h1>Baby Name Finder</h1>
          <ViewerToggle />
        </header>
        <NavTabs />
        <main>
          <Routes>
            <Route path="/" element={<BrowsePage />} />
            <Route path="/favorites" element={<FavoritesPage />} />
            <Route path="/shortlist" element={<ShortlistPage />} />
          </Routes>
        </main>
      </BrowserRouter>
    </ViewerProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

export default App;
