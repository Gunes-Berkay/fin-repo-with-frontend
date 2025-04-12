// TradingViewWidget.jsx
import axios from 'axios';
import React, { useEffect, useRef, memo, useState } from 'react';


function TradingViewWidget() {
  const [currentPaperSymbol, setCurrentPaperSymbol] = useState('');
  const [showSetPaperName, setShowSetPaperName] = useState(false);
  const [paperNameQuery, setPaperNameQuery] = useState('');
  const [filteredPapers, setFilteredPapers] = useState('');
  const [interval, setInterval] = useState('4h');
  const [paperData, setPaperData] = useState({});
  const toggleShowPaperName = () => {setShowSetPaperName(!showSetPaperName)}
  const [paperNamesList, setPaperNamesList] = useState([]);
  const [paperSymbolList, setPaperSymbolList] = useState([]);
  const [papersData, setPapersData] = useState({})
  const container = useRef()


  const handlePaperSelect = (paperSymbol) => {
    setCurrentPaperSymbol(paperSymbol); 
    setPaperNameQuery(paperSymbol); 
    setFilteredPapers([]); 
    
  
    fetch(`http://127.0.0.1:8000/charts/table/${paperSymbol}USDTon${interval}/`)
      .then(response => response.json())
      .then(data => setPaperData(data))
      .catch(error => console.error("Error fetching paper data:", error));
  };
  

  const handlePaperNameChanger = (e) => {
    const value = e.target.value;
    setPaperNameQuery(value);

    if (value) {
      const filtered = papersData.filter((paper) => 
          paper.symbol.toLowerCase().includes(value.toLowerCase()) || 
          paper.name.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredPapers(filtered);
    } else {
      setFilteredPapers([]);
    }

    
  }

  const getPaperData = (paperName) => {
      fetch(`http://127.0.0.1:8000/charts/table/${currentPaperSymbol}on${interval}`)
      .then((data) => setPapersData(data))
  }

  useEffect(() => {  // ✅ Now useEffect gets a function as an argument
    fetch('http://127.0.0.1:8000/charts/')
      .then((response) => response.json())
      .then((data) => setPapersData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);
  

  return (
    <div>
      <button onClick={() => setShowSetPaperName(!showSetPaperName)}>data getir</button>
      {showSetPaperName && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Coin seç</h5>
                <button type="button" className="btn-close" onClick={toggleShowPaperName}></button>
              </div>
              <div className="modal-body">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Paper Ara"
                  value={paperNameQuery}
                  onChange={handlePaperNameChanger}
                />

                {filteredPapers.length > 0 && (
                  <ul className="list-group mt-2">
                    {filteredPapers.map((paper) => (
                      <li
                        key={paper.paper_id}
                        className="list-group-item"
                        onClick={() => {handlePaperSelect(paper.symbol);
                          console.log(paper.name)
                        }}
                        style={{ cursor: 'pointer' }}
                      >
                        <span>{paper.name}({paper.symbol})</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={toggleShowPaperName}>İptal</button>
              </div>
            </div>
          </div>
        </div>
      )}
      <p>{JSON.stringify(paperData, null, 2)}</p>
    </div>
  )

}

export default TradingViewWidget
