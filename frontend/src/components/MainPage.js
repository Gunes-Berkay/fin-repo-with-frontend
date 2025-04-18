import React, { useEffect, useState } from 'react';
import ChartContainer from './Charts/ChartContainer.tsx';
import { FaBook, FaEye, FaNewspaper, FaTimes } from 'react-icons/fa'; // FontAwesome ikonları

const MainPage = () => {
  const [currentType, setCurrentType] = useState('default'); 
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showPaperNews, setShowPaperNews] = useState(false);
  const [showWatchlist, setShowWatchlist] = useState(false);
  const [showResearch, setShowResearch] = useState(false);
  const [watchListData, setWatchListData] = useState([]); 
  const [loading, setLoading] = useState(false);
  

  useEffect(() => {
    fetchStartWatchList(); 
  }, [])

  const handleIconClick = (type) => {   
    setIsSidebarOpen(true);   
    setShowPaperNews(type === 'paper');
    setShowWatchlist(type === 'watchlist');
    setShowResearch(type === 'research');
  };

  const fetchStartWatchList = async () => {
    const response = await fetch('http://127.0.0.1:8000/charts/'); 
    const data = await response.json();
    setWatchListData(data);
    console.log(data); 
  }


  const uptdateFollowingPaper = async () => {
    setLoading(true);
    const response = await fetch('http://127.0.0.1:8000/update-following-paper/', {
      method: 'POST',
    });
    setLoading(false);
    if (response.ok) {
      console.log('Prices updated');
      fetchStartWatchList();
    } else {
      console.error('Failed to update prices');
    }
  }

  const addPapertoWatchList = async (paper_id, follow_list_name) => {
    const formData = new FormData();
    formData.append('paper_id', paper_id);
    formData.append('follow_list_name', follow_list_name);
  
    const response = await fetch('http://127.0.0.1:8000/follow-lists/add-paper/', {
      method: 'POST',
      body: formData,
    });
  
    if (response.ok) {
      console.log('Paper added to watchlist:', paper_id);
    } else {
      console.error('Failed to add paper to watchlist');
    }
  };

  const createFollowList = async (follow_list_name) => {
    const formData = new FormData();
    formData.append('follow_list_name', follow_list_name);
  
    const response = await fetch('http://127.0.0.1:8000/follow-lists/create/', {
      method: 'POST',
      body: formData,
    });
  
    const data = await response.json();
    if (response.ok) {
      console.log('Follow list created:', data);
    } else {
      console.error('Failed to create follow list:', data);
    }
  };

  const getFollowLists = async () => {
    const response = await fetch('http://127.0.0.1:8000/follow-lists/get/');
    const data = await response.json();
  
    if (response.ok) {
      console.log('Follow lists:', data);
      return data;
    } else {
      console.error('Failed to fetch follow lists');
    }
  };

  const removePaperFromWatchList = async (paper_id, follow_list_name) => {
    const formData = new FormData();
    formData.append('paper_id', paper_id);
    formData.append('follow_list_name', follow_list_name);
  
    const response = await fetch('http://127.0.0.1:8000/follow-lists/remove-paper/', {
      method: 'POST',
      body: formData,
    });
  
    const data = await response.json();
    if (response.ok) {
      console.log('Paper removed from watchlist:', data);
    } else {
      console.error('Failed to remove paper from watchlist:', data);
    }
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
          {showWatchlist && (
            <>
              {loading ? <div>Loading...</div> : <div>Prices are updated!</div>}

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
                      {/* Watchlist data üzerinden döngü oluştur */}
                      console.log('watchListData:', watchListData);

                      {watchListData.data.map((item, index) => (
                        <tr key={index}>
                          <td style={{ border: '1px solid #ddd', padding: '3px' }}>{item.symbol}</td>
                          <td style={{ border: '1px solid #ddd', padding: '3px' }}>{item.price}</td>
                          <td style={{ border: '1px solid #ddd', padding: '3px' }}>{item.change_24h}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}


          {showResearch && <p>📚 Araştırmalar aktif</p>}
        </div>
      )}
    </div>
  );
};

export default MainPage;
