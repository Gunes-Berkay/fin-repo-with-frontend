import React, { useState } from 'react';
import ChartContainer from './Charts/ChartContainer.tsx';
import { FaBook, FaEye, FaNewspaper, FaTimes } from 'react-icons/fa'; // FontAwesome ikonları

const MainPage = () => {
  const [currentType, setCurrentType] = useState('default'); 
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showPaperNews, setShowPaperNews] = useState(false);
  const [showWatchlist, setShowWatchlist] = useState(false);
  const [showResearch, setShowResearch] = useState(false);

  const handleIconClick = (type) => {   
    setIsSidebarOpen(true);   
    setShowPaperNews(type === 'paper');
    setShowWatchlist(type === 'watchlist');
    setShowResearch(type === 'research');
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Ana İçerik */}
      <div
        style={{
          flexGrow: 1,
          transition: 'width 0.3s ease',
          width: isSidebarOpen ? 'calc(100% - 370px)' : 'calc(100% - 70px)',
          padding: '20px',
        }}
      >
        <h2>Grafik Sayfası</h2>
        <ChartContainer />
      </div>

      <div
        style={{
          width: '70px',
          backgroundColor: '#fafafa',
          padding: '10px 5px',
          borderLeft: '1px solid #ddd',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '20px',
        }}
      >
        <button onClick={() => setIsSidebarOpen(false)}         
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '24px' }}>
          <FaTimes/>
        </button>

        <button
          onClick={() => handleIconClick('paper')}
          title="Haberler"
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '24px' }}
        >
          <FaNewspaper />
        </button>
        <button
          onClick={() => handleIconClick('watchlist')}
          title="İzleme Listesi"
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '24px' }}
        >
          <FaEye />
        </button>
        <button
          onClick={() => handleIconClick('research')}
          title="Araştırmalar"
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '24px' }}
        >
          <FaBook />
        </button>

        
      </div>

      {/* Sağ Sidebar */}
      {isSidebarOpen && (
        <div
          style={{
            width: '300px',
            backgroundColor: '#f5f5f5',
            padding: '20px',
            borderLeft: '1px solid #ddd',
            transition: 'transform 0.3s ease',
          }}
        >
          <h3>Sidebar</h3>
          <p>Buraya her şeyi koyabilirsin.</p>

          {showPaperNews && <p>📰 Haberler aktif</p>}
          {showWatchlist && 
          <div>
            <p>👁️ İzleme Listesi aktif</p>
            <div>
              <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                <thead>
                  <tr>
                    <th style={{ border: '1px solid #ddd', padding: '3px' }}>Symbol</th>
                    <th style={{ border: '1px solid #ddd', padding: '3px' }}>Price</th>
                    <th style={{ border: '1px solid #ddd', padding: '3px' }}>24h%</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ border: '1px solid #ddd', padding: '3px' }}>Örnek İzleme 1</td>
                  </tr>
                  <tr>
                    <td style={{ border: '1px solid #ddd', padding: '3px' }}>Örnek İzleme 2</td>
                  </tr>
                  <tr>
                    <td style={{ border: '1px solid #ddd', padding: '8px' }}>Örnek İzleme 3</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>}
          {showResearch && <p>📚 Araştırmalar aktif</p>}
        </div>
      )}
    </div>
  );
};

export default MainPage;
