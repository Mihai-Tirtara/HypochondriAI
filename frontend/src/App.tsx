import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TestEndpoint from './components/TestEndpoint';
import Conversation from './components/Conversation';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TestEndpoint />} />
        <Route path="/conversation" element={<Conversation />} />
      </Routes>
    </Router>
  );
}

export default App;
