import logo from './logo.svg';
import './App.css';
import { Routes, Route } from 'react-router-dom';

import MainPage from './components/MainPage';
import NewsPage from './components/NewsPage';
import Wallet from './components/Wallet';
import Navbar from './components/Navbar';
import Charts from './components/Charts';

function App() {
  const myWidth = 220;
  return (
    <div className='App'>
      <Navbar drawerWidth={myWidth} />
      <div className="content-wrapper">
        <Routes>
          <Route path='' element={<MainPage />} />
          <Route path='/wallet' element={<Wallet />} />
          <Route path='/charts' element={<Charts />} />
          <Route path='/news' element={<NewsPage />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
