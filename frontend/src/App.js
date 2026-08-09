import "@/App.css";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "@/pages/Home";
import PocTest from "@/pages/PocTest";
import { Toaster } from "@/components/ui/sonner";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/poc-test" element={<PocTest />} />
        </Routes>
      </BrowserRouter>
      <Toaster richColors position="top-right" />
    </div>
  );
}

export default App;
