import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import Conversation from './components/Conversation';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/conversation" element={<Conversation />} />
      </Routes>
    </Router>
  );
}

export default App;
