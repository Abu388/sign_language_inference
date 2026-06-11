import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import SignToRecognition from './SignRecognition/SignToRecognition';
import LanguageTranslation from './LanguageTranslation/LanguageTranslation';
import './App.css';
import Ai_refinement from './AIRefinement/Ai_refinement';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/sign-to-recognition" element={<SignToRecognition />} />
        <Route path="/language-translation" element={<LanguageTranslation />} />
        <Route path="/ai-refinement" element={<Ai_refinement />} />
      </Routes>
    </Router>
  );
}

export default App;