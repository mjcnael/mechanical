import { Route, Routes } from "react-router-dom";
import UserSelectionPage from "./pages/user-selection-page";
import TechniciansPage from "./pages/technicians-page";
import ForemenPage from "./pages/foremen-page";

const App = () => {
  return (
    <div>
      <Routes>
        <Route path="/" element={<UserSelectionPage />} />
        <Route path="/technicians/:id" element={<TechniciansPage />} />
        <Route path="/foremen" element={<ForemenPage />} />
      </Routes>
    </div>
  );
};

export default App;
