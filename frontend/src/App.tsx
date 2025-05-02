import SymptomForm from './components/Symptomps';
import TestEndpoint from './components/TestEndpoint';
import './App.css';

function App() {

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-primary-700 text-white p-4 shadow-md">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold">Health Anxiety Management App</h1>
          <p className="text-sm opacity-80">Helping you manage health concerns with evidence-based information</p>
        </div>
      </header>

      <main className="container mx-auto py-8 px-4">
        <TestEndpoint></TestEndpoint>
      </main>

      <footer className="bg-gray-800 text-white p-6 mt-12">
        <div className="container mx-auto">
          <p className="text-center text-sm opacity-70">
            Health Anxiety Management App - This is a proof of concept application and not a substitute for professional medical advice.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
