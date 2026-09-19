import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ToastProvider } from "./hooks/useToast";
import { AboutPage } from "./pages/AboutPage";
import { ChatAssistant } from "./pages/ChatAssistant";
import { Dashboard } from "./pages/Dashboard";
import { DocumentRAG } from "./pages/DocumentRAG";
import { HistoryPage } from "./pages/HistoryPage";
import { ImageAnalyzer } from "./pages/ImageAnalyzer";
import { WasteAnalyzer } from "./pages/WasteAnalyzer";

export default function App() {
  return (
    <ToastProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="analyzer" element={<WasteAnalyzer />} />
          <Route path="image" element={<ImageAnalyzer />} />
          <Route path="chat" element={<ChatAssistant />} />
          <Route path="documents" element={<DocumentRAG />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="about" element={<AboutPage />} />
        </Route>
      </Routes>
    </ToastProvider>
  );
}
