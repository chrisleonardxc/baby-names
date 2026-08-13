import { BrowserRouter, Route, Routes } from "react-router-dom";
import { NavTabs } from "./components/NavTabs";
import { ViewerToggle } from "./components/ViewerToggle";
import { ViewerProvider } from "./context/ViewerContext";
import { BrowsePage } from "./pages/BrowsePage";
import { FavoritesPage } from "./pages/FavoritesPage";
import { ShortlistPage } from "./pages/ShortlistPage";

function App() {
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

export default App;
