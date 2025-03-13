import { useState } from 'react'
import Header from './components/header'
import Footer from './components/footer'

function App() {
  const [example] = useState<string>('teste use state');
  return (
    <>
        <div className="flex flex-col min-h-screen">
            <Header/>
            <main className='flex-grow container mx-auto p-4'>
                <p>{example}</p>
                {/* <AppRoutes/> */}
            </main>
            <Footer/>
        </div>
    </>
  );
}

export default App