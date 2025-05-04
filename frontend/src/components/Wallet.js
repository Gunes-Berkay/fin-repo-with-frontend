import React, { useEffect, useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './wallet.css';
import axios from 'axios';

const Wallet = () => {
  const [portfolios, setPortfolios] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [portfolioName, setPortfolioName] = useState('');
  const [currentPortfolio, setCurrentPortfolio] = useState(null);
  const [showAddPaperModal, setShowAddPaperModal] = useState(false);
  const [papers, setPapers] = useState([]);
  const [filteredPapers, setFilteredPapers] = useState([]);
  const [selectedPaperName, setSelectedPaperName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [portfolioPapers, setPortfolioPapers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [showTransactionsModal, setShowTransactionsModal] = useState(false);
  const [showTransactionForm, setShowTransactionForm] = useState({});


  const [selectedPaper, setSelectedPaper] = useState('');
  const [selectedPortfolio, setSelectedPortfolio] = useState('');

  const [newTransaction, setNewTransaction] = useState({
    name: '',
    portfolio: '',
    entry_price: '',
    quantity: '',
    buy: true
  });

  

  // Yeni State

  useEffect(() => {
    fetchStartWatchList();
    updateFollowingPaper();
    updatePortfolioPaperPrice();
    fetchPortfolios();
    fetchPapers();
    fetchPortfolioPapers();
  }, []);

  useEffect(() => {
    if (selectedPaper && selectedPortfolio) {
      fetchTransactions(selectedPaper, selectedPortfolio);
    }
  }, [selectedPaper, selectedPortfolio]);

  const fetchTransactions = async (paperName, portfolioName) => {
    try {
      const response = await axios.get(`/wallet/transactions/`, {
        params: {
          paper_name: paperName,
          portfolio_name: portfolioName
        }
      });
      setTransactions(response.data);
    } catch (error) {
      console.error('Transaction listesi alınamadı:', error);
    }
  };

  const handleNewTransactionChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewTransaction(prevState => ({
      ...prevState,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const submitTransaction = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/wallet/create-transaction/', newTransaction);
      // Başarılı olursa listeyi tekrar al
      fetchTransactions(newTransaction.name, newTransaction.portfolio);
      // Formu sıfırla
      setNewTransaction({
        name: '',
        portfolio: '',
        entry_price: '',
        quantity: '',
        buy: true
      });
    } catch (error) {
      console.error('İşlem oluşturulamadı:', error);
    }
  };

  const handleTransactionChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewTransaction((prevState) => ({
      ...prevState,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleTransactionSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8000/wallet/create-transaction/', newTransaction);
      // Fetch updated transactions after successful submission
      fetchTransactions(newTransaction.name, newTransaction.portfolio);
      // Reset the transaction form
      setNewTransaction({
        name: '',
        portfolio: '',
        entry_price: '',
        quantity: '',
        buy: true,
      });
      console.log('Transaction created successfully:', response.data);
    } catch (error) {
      console.error('Error creating transaction:', error.response?.data || error.message);
    }
  };

  const updateFollowingPaper = async () => {
    const response = await fetch('http://127.0.0.1:8000/update-following-paper/', {
      method: 'POST',
    });
    if (response.ok) {
      console.log('Prices updated');
    } else {
      console.error('Failed to update prices');
    }
  }
  const fetchStartWatchList = async () => {
    const response = await fetch('http://127.0.0.1:8000/charts/'); 
    const data = await response.json(); 
  }
  const fetchPortfolios = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/wallet/portfolios/');
      setPortfolios(response.data);
    } catch (error) {
      console.error('Error fetching portfolios:', error);
    }
  };

  const updatePortfolioPaperPrice = async () => {
    try {
      await axios.get('http://127.0.0.1:8000/wallet/update-portfolio-paper-price/');
    } catch (error) {
      console.error('Error fetching portfolios:', error);
    }
  };

  const fetchPortfolioPapers = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/wallet/portfolio-papers/');
      setPortfolioPapers(response.data);
    } catch (error) {
      console.error('Error fetching portfolio-papers:', error);
    }
  };

  const fetchPapers = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/wallet/papers/');
      setPapers(response.data);
    } catch (error) {
      console.error('Error fetching papers:', error);
    }
  };

  const toggleModal = () => setShowModal(!showModal);
  const toggleAddPaperModal = () => setShowAddPaperModal(!showAddPaperModal);
  const toggleTransactionsModal = () => setShowTransactionsModal(!showTransactionsModal);

  const createPortfolio = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/wallet/create-portfolio/', {
        name: portfolioName,
        papers: [],
      });
      setPortfolios((prev) => [...prev, response.data]);
      setPortfolioName('');
      toggleModal();
    } catch (error) {
      console.error('Error creating portfolio:', error.response?.data || error.message);
    }
  };

  const deletePortfolio = async (portfolioId) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/wallet/delete-portfolio/${portfolioId}/`);
      setPortfolios(portfolios.filter((p) => p.portfolio_id !== portfolioId));
      setCurrentPortfolio(null);
    } catch (error) {
      console.error('Error deleting portfolio:', error.response?.data || error.message);
    }
  };

  const addPaperToPortfolio = async (paperName) => {
    if (!currentPortfolio) return;

    try {
      const response = await axios.post('http://127.0.0.1:8000/wallet/add-paper/', {
        portfolio_id: currentPortfolio.portfolio_id,
        paper_name: selectedPaperName,
      });

      setCurrentPortfolio((prev) => ({
        ...prev,
        papers_list: [...(prev.papers_list || []), response.data],
      }));

      setPortfolios((prevPortfolios) =>
        prevPortfolios.map((portfolio) =>
          portfolio.portfolio_id === currentPortfolio.portfolio_id
            ? { ...portfolio, papers_list: [...(portfolio.papers_list || []), selectedPaperName] }
            : portfolio
        )
      );

      setSelectedPaperName('');
      toggleAddPaperModal();
    } catch (error) {
      console.error('Error adding paper:', error.response?.data || error.message);
    }
  };

  const deletePaperFromPortfolio = async (portfolioId, paperId) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/wallet/delete-paper/${portfolioId}/${paperId}/`);
      setCurrentPortfolio((prev) => ({
        ...prev,
        papers_list: prev.papers_list.filter((p) => p.paper_id !== paperId),
      }));
    } catch (error) {
      console.error('Error deleting paper:', error.response?.data || error.message);
    }
  };

  const selectPortfolio = (portfolio) => {
    setCurrentPortfolio(portfolio);
  };

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
  };

  const handlePaperSelect = (paperName) => {
    setSelectedPaperName(paperName);
    setSearchQuery(paperName);
    setFilteredPapers([]);
  };

  const viewTransactions = async (paperId) => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/wallet/transactions/${paperId}/`);
      setTransactions(response.data);
      toggleTransactionsModal();
    } catch (error) {
      console.error('Error fetching transactions:', error.response?.data || error.message);
    }
  };

  return (
    <div className="container">
      <h1 className="mt-4">Wallet Page</h1>

      <div className="mb-4">
        <button className="btn btn-primary" onClick={toggleModal}>Create Portfolio</button>
      </div>

      {/* Portföy Listesi */}
      <div className="row">
        {portfolios.length > 0 ? (
          portfolios.map((portfolio) => (
            <div key={portfolio.portfolio_id} className="col-md-4 mb-3">
              <div className="card">
                <div className="card-body">
                  <h5 className="card-title">{portfolio.name}</h5>
                  <button className="btn btn-success btn-sm me-2" onClick={() => selectPortfolio(portfolio)}>Select</button>
                  <button className="btn btn-danger btn-sm" onClick={() => deletePortfolio(portfolio.portfolio_id)}>Delete</button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <p>No portfolios available.</p>
        )}
      </div>

      {/* Seçilen Portföy */}
      {currentPortfolio && (
              <div className="card mt-4">
                <div className="card-body">
                  <h4>Selected Portfolio: {currentPortfolio.name}</h4>
                  <h6 className="text-muted">Papers:</h6>

                  {portfolioPapers.length > 0 ? (
        <div className="table-responsive mb-3">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Name (Symbol)</th>
                <th>Total Quantity</th>
                <th>Current Price</th>
                <th>Average Buy Price</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
            {portfolioPapers
              .filter((portfolioPaper) => portfolioPaper.portfolio_id === currentPortfolio.portfolio_id)
              .map((paper) => (
                <React.Fragment key={paper.paper_id}>
                  <tr>
                    <td>{paper.name} ({paper.symbol})</td>
                    <td>{paper.total_quantity}</td>
                    <td>{paper.current_price}</td>
                    <td>{paper.average_buy_price}</td>
                    <td>
                      <button
                        className="btn btn-info btn-sm me-2"
                        onClick={() => {
                          setShowTransactionForm(prev => ({
                            ...prev,
                            [paper.paper_id]: !prev[paper.paper_id]
                          }));
                          viewTransactions(paper.paper_id);
                        }}
                      >
                        Transactions
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => deletePaperFromPortfolio(currentPortfolio.portfolio_id, paper.paper_id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>

                  {showTransactionForm[paper.paper_id] && (
                    <tr>
                      <td colSpan="5">
                        {/* Transaction Form */}
                        <form onSubmit={handleTransactionSubmit}>
                          <div className="mb-2">
                            <input
                              type="number"
                              name="quantity"
                              placeholder="Quantity"
                              value={newTransaction.quantity || ''}
                              onChange={handleTransactionChange}
                              className="form-control"
                              required
                            />
                          </div>
                          <div className="mb-2">
                            <input
                              type="number"
                              name="price"
                              placeholder="Price"
                              value={newTransaction.price || ''}
                              onChange={handleTransactionChange}
                              className="form-control"
                              required
                            />
                          </div>
                          <div className="mb-2">
                            <label>
                              <input
                                type="checkbox"
                                name="buy"
                                checked={newTransaction.buy || false}
                                onChange={handleTransactionChange}
                              /> Buy
                            </label>
                          </div>
                          <button className="btn btn-success btn-sm" type="submit">Submit Transaction</button>
                        </form>

                        {/* Transaction List */}
                        <div className="mt-3">
                          <h6>Transactions</h6>
                          {transactions[paper.paper_id] ? (
                            <ul className="list-group">
                              {transactions[paper.paper_id].map(txn => (
                                <li key={txn.id} className="list-group-item">
                                  {txn.buy ? 'Buy' : 'Sell'} - {txn.quantity} @ {txn.price}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <p>No transactions found.</p>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
            ))}

            </tbody>
          </table>
        </div>
      ) : (
        <p>There are no papers in the portfolio</p>
      )}


            

            <button className="btn btn-primary mt-3" onClick={toggleAddPaperModal}>Add Paper</button>
          </div>
        </div>
      )}

      {/* Modal: Create Portfolio */}
      {showModal && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Create Portfolio</h5>
                <button className="btn-close" onClick={toggleModal}></button>
              </div>
              <div className="modal-body">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Portfolio Name"
                  value={portfolioName}
                  onChange={(e) => setPortfolioName(e.target.value)}
                />
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={toggleModal}>Cancel</button>
                <button className="btn btn-primary" onClick={createPortfolio}>Save</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Add Paper */}
      {showAddPaperModal && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Add Paper</h5>
                <button className="btn-close" onClick={toggleAddPaperModal}></button>
              </div>
              <div className="modal-body">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search Paper"
                  value={searchQuery}
                  onChange={handleSearchChange}
                />
                {filteredPapers.length > 0 && (
                  <ul className="list-group mt-2">
                    {filteredPapers.map((paper) => (
                      <li
                        key={paper.paper_id}
                        className="list-group-item"
                        style={{ cursor: 'pointer' }}
                        onClick={() => handlePaperSelect(paper.name)}
                      >
                        {paper.name} ({paper.symbol})
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={toggleAddPaperModal}>Cancel</button>
                <button className="btn btn-primary" onClick={addPaperToPortfolio}>Save</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal: View Transactions */}
      {showTransactionsModal && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Transactions</h5>
                <button className="btn-close" onClick={toggleTransactionsModal}></button>
              </div>
              <div className="modal-body">
                {transactions.length > 0 ? (
                  <ul className="list-group">
                    {transactions.map((tx) => (
                      <li key={tx.transaction_id} className="list-group-item">
                        {tx.date} - {tx.type} - {tx.amount} shares at ${tx.price}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No transactions found.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default Wallet;
