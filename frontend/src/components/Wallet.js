import React, { useEffect, useState } from 'react'
import 'bootstrap/dist/css/bootstrap.min.css';
import './wallet.css'
import axios from "axios";




const Wallet = () => {
  const [portfolios, setPortfolios] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [portfolioName, setPortfolioName] = useState([]);
  const [currentPortfolio, setCurrentPortfolio] = useState([]);
  const [paperData, setPaperData] = useState({
    name: '',
  });
  const [showAddPaperModal, setShowAddPaperModal] = useState(false);

  const [papers, setPapers] = useState([]); 
  const [filteredPapers, setFilteredPapers] = useState([]); // Filtrelenmiş Paper'lar
  const [selectedPaperName, setSelectedPaperName] = useState(''); // Seçilen Paper ismi
  const [searchQuery, setSearchQuery] = useState(''); // Kullanıcı input'u


  let counter = 0;

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/portfolios/")
    .then(response => response.json())
    .then(portfolios => setPortfolios(portfolios))
    .catch(error => console.error("Error fetching portfolios:", error));

    
  }, []);

  useEffect(()=> {
    fetch("http://127.0.0.1:8000/api/papers/")
    .then(response => response.json())
    .then(papers => setPapers(papers))
    .catch(error => console.error("Error fetching portfolios:", error));

  }, [])


  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);

    if (value) {
      const filtered = papers.filter((paper) => 
          paper.symbol.toLowerCase().includes(value.toLowerCase()) || 
          paper.name.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredPapers(filtered);
  } else {
      setFilteredPapers([]);
  }
  }

  const handlePaperSelect = (paperName) => {
    setSelectedPaperName(paperName); 
    setSearchQuery(paperName); 
    setFilteredPapers([]); 
  };
  

  const toggleModal = () => {
    setShowModal(!showModal);
  }
  const toggleAddPaperModal = () => setShowAddPaperModal(!showAddPaperModal);


  const createPortfolio = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/api/create-portfolio/", {
        name: portfolioName, 
        papers: [],
      });
  
      console.log("Başarılı:", response.data);
      setPortfolios((prevPortfolios) => [...prevPortfolios, response.data]);
      setPortfolioName('');
      toggleModal();
      
      
    } catch (error) {
      console.error("Hata:", error.response?.data || error.message);
    }
  };

  const selectPortfolio = (portfolio) => {
    setCurrentPortfolio(portfolio);
  };

  const handlePaperDataChange = (e) => {
    const { name, value } = e.target;
    setPaperData({ ...paperData, [name]: value });
  };

  const addPaperToPortfolio = async () => {
    if (!currentPortfolio) return;

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/add-paper/", {
        portfolio_id: currentPortfolio.portfolio_id,
        paper_name: selectedPaperName,
        ...paperData,
      });

      console.log("Hisse başarıyla eklendi:", response.data);

      setPortfolios((prevPortfolios) =>
        prevPortfolios.map((portfolio) =>
          portfolio.portfolio_id === currentPortfolio.portfolio_id
            ? { ...portfolio, papers_list: [...portfolio.papers_list, response.data] }
            : portfolio
        )
      );

    
      // Portföy güncellemesi (React state)
      setCurrentPortfolio((prevPortfolio) => ({
        ...prevPortfolio,
        papers_list: [...(prevPortfolio.papers_list || []), response.data]
      }));

      

      setPaperData({ paper_name: selectedPaperName});
      toggleAddPaperModal();
    } catch (error) {
      console.error("Hata:", error.response?.data || error.message);
    }
  };

  return (
    <div>
      <h1>Wallet PAGE</h1>
      <div>
          <button className='btn btn-primary' onClick={toggleModal}>Create Portfolio</button>
      </div>

      <div className='mui-container portfolios-left-div'>
        {portfolios.length > 0 ? (
          portfolios.map((portfolio, index) => (
            <div>
              <button key={index} className="btn btn-secondary m-2"  onClick={() => selectPortfolio(portfolio)}>             
                  <h5 className="card-title">{portfolio.name}</h5>               
              </button>
            </div>
            
          ))
        ) : (
          <p>Henüz bir portföy oluşturulmadı.</p>
        )}
      </div>

      {/* Seçilen Portföy Detayları */}
      <div className='bootstrap-container portfolio-div'>
        {currentPortfolio ? (
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Portföy: {currentPortfolio.name}</h5>
              <h6 className="card-subtitle mb-2 text-muted">Papers:</h6>
              {currentPortfolio.papers_list && currentPortfolio.papers_list.length > 0 ? (
                <ul>
                  {currentPortfolio.papers_list.map((paper, idx) => (
                    <li key={idx}>
                    {paper.name} (İsim: {paper.name})
                      {/* Burada buton olacak, butona basılınca ilgili fonksiyon yeni bir sayfa açıcak, açtığı sayfa ilgili paper'ın transaction'larını gösterecek */}
                    </li>
                  ))}
                </ul>
              ) : (
                <p>Bu portföyde henüz bir hisse yok.</p>
              )}
              <button
                className="btn btn-success mt-3"
                onClick={toggleAddPaperModal}
              >
                Add Paper
              </button>
            </div>
          </div>
        ) : (
          <p>Bir portföy seçmek için düğmeye tıklayın.</p>
        )}
      </div>


       {/* Modal */}
       {showModal && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Yeni Portföy Oluştur</h5>
                <button type="button" className="btn-close" onClick={toggleModal}></button>
              </div>
              <div className="modal-body">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Portföy İsmi"
                  value={portfolioName}
                  onChange={(e) => setPortfolioName(e.target.value)}
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={toggleModal}>İptal</button>
                <button type="button" className="btn btn-primary" onClick={createPortfolio}>Kaydet</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showAddPaperModal && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Hisse Ekle</h5>
                <button type="button" className="btn-close" onClick={toggleAddPaperModal}></button>
              </div>
              <div className="modal-body">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Paper Ara"
                  value={searchQuery}
                  onChange={handleSearchChange}
                />

                {filteredPapers.length > 0 && (
                  <ul className="list-group mt-2">
                    {filteredPapers.map((paper) => (
                      <li
                        key={paper.paper_id}
                        className="list-group-item"
                        onClick={() => handlePaperSelect(paper.name)}
                        style={{ cursor: 'pointer' }}
                      >
                        <span>{paper.name}({paper.symbol})</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={toggleAddPaperModal}>İptal</button>
                <button type="button" className="btn btn-primary" onClick={addPaperToPortfolio}>Kaydet</button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
    

    
  )
}

export default Wallet