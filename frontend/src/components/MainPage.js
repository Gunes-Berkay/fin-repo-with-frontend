import React, { useEffect, useState } from 'react';
import ChartContainer from './Charts/ChartContainer.tsx';
import { FaBook, FaEye, FaNewspaper, FaTimes } from 'react-icons/fa'; // FontAwesome ikonları
import Modal from 'react-modal'; // Modal bileşeni

const MainPage = () => {
  const [currentType, setCurrentType] = useState('default'); 
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showPaperNews, setShowPaperNews] = useState(false);
  const [showWatchlist, setShowWatchlist] = useState(false);
  const [showResearch, setShowResearch] = useState(false);
  const [watchListData, setWatchListData] = useState([]); 
  const [loading, setLoading] = useState(false);
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [interval, setInterval] = useState('4h');
  const [paperNames, setPaperNames] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchInput, setSearchInput] = useState('');


  const [expandedLists, setExpandedLists] = useState({});

  const fetchPaperNames = async () => {
    const response = await fetch('http://127.0.0.1:8000/get-paper-names/'); 
    const data = await response.json();
    setPaperNames(data);
    console.log(data); 
  }

  const toggleList = (listName) => {
    setExpandedLists((prev) => ({
      ...prev,
      [listName]: !prev[listName],
    }));
  };


  

  useEffect(() => {
    fetchStartWatchList(); 
    fetchPaperNames();
  }, [])

  const handleIconClick = (type) => {   
    setIsSidebarOpen(true);   
    setShowPaperNews(type === 'paper');
    setShowWatchlist(type === 'watchlist');
    setShowResearch(type === 'research');
    updateFollowingPaper();
  };

  const fetchStartWatchList = async () => {
    const response = await fetch('http://127.0.0.1:8000/charts/'); 
    const data = await response.json();
    setWatchListData(data);
    console.log(data); 
  }

  


  const updateFollowingPaper = async () => {
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
        <button onClick={() => setIsModalOpen(true)}>Grafik Değiştir</button>
        <ChartContainer interval={interval} key = {symbol} symbol={symbol} />
      </div>

      <Modal
          isOpen={isModalOpen}
          onRequestClose={() => setIsModalOpen(false)}
          contentLabel="Paper Seç"
          style={{
            content: {
              width: '400px',
              margin: 'auto',
              padding: '20px',
            }
          }}
        >
          <h3>Paper Seç</h3>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="İsim ya da sembol girin"
            style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
          />

          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {paperNames
              .filter(paper =>
                paper.name.toLowerCase().includes(searchInput.toLowerCase()) ||
                paper.symbol.toLowerCase().includes(searchInput.toLowerCase())
              )
              .map((paper, index) => (
                <div
                  key={index}
                  style={{ padding: '5px', cursor: 'pointer', borderBottom: '1px solid #ddd' }}
                  onClick={() => {
                    setSymbol(paper.symbol + 'USDT');
                    setIsModalOpen(false);
                    setSearchInput('');
                  }}
                >
                  {paper.name} ({paper.symbol})
                </div>
              ))}
          </div>

          <button onClick={() => setIsModalOpen(false)} style={{ marginTop: '10px' }}>Kapat</button>
        </Modal>

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
                    {Object.entries(watchListData).map(([listName, items]) => (
                      <React.Fragment key={listName}>
                        {/* Group Header Row */}
                        <tr onClick={() => toggleList(listName)} style={{ cursor: 'pointer', background: '#f0f0f0' }}>
                          <td colSpan={4} style={{ border: '1px solid #ddd', padding: '6px', fontWeight: 'bold' }}>
                            {expandedLists[listName] ? '▼' : '►'} {listName}
                          </td>
                        </tr>

                        {/* Group Content Rows */}
                        {expandedLists[listName] &&
                          items.map((item, index) => (
                            <tr key={`${listName}-${index}`}>
                              
                              <td style={{ border: '1px solid #ddd', padding: '3px' }}>
                                <button
                                  onClick={() => {
                                    setSymbol(item.symbol + 'USDT');
                                  }}
                                >
                                  {item.symbol}
                                </button>
                              </td>
                              <td style={{ border: '1px solid #ddd', padding: '3px' }}>{item.price}</td>
                              <td
                                style={{
                                  border: '1px solid #ddd',
                                  padding: '3px',
                                  color: item.change_24h >= 0 ? 'green' : 'red',
                                }}
                              >
                                {parseFloat(item.change_24h).toFixed(2)}%
                              </td>
                            </tr>
                          ))}
                      </React.Fragment>
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
