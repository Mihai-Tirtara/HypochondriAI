import TestEndpoint from './components/TestEndpoint';
function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-purple-100">
      <main className="min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-md sm:max-w-lg lg:max-w-xl xl:max-w-2xl">
          <TestEndpoint />
        </div>
      </main>
    </div>
  );
}

export default App;
