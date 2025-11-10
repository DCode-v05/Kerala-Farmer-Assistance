import React, { useState } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, BarChart, Bar
} from 'recharts';

const Financials = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('year');

  // Sample data
  const incomeExpenseData = [
    { month: 'Jan', income: 120000, expense: 85000 },
    { month: 'Feb', income: 95000, expense: 70000 },
    { month: 'Mar', income: 150000, expense: 110000 },
    { month: 'Apr', income: 180000, expense: 95000 },
    { month: 'May', income: 210000, expense: 130000 },
    { month: 'Jun', income: 175000, expense: 105000 },
    { month: 'Jul', income: 190000, expense: 120000 },
  ];

  const expenseByCategory = [
    { name: 'Seeds', value: 35 },
    { name: 'Fertilizers', value: 25 },
    { name: 'Labor', value: 20 },
    { name: 'Equipment', value: 12 },
    { name: 'Others', value: 8 },
  ];

  const yearlyData = [
    { year: '2020', income: 1850000, expense: 1250000 },
    { year: '2021', income: 2100000, expense: 1450000 },
    { year: '2022', income: 2450000, expense: 1680000 },
    { year: '2023', income: 2750000, expense: 1920000 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{`${label}`}</p>
          <p className="income">Income: ₹{payload[0].value.toLocaleString()}</p>
          <p className="expense">Expense: ₹{payload[1].value.toLocaleString()}</p>
          <p className="profit">Profit: ₹{(payload[0].value - payload[1].value).toLocaleString()}</p>
        </div>
      );
    }
    return null;
  };

  // Calculate totals
  const totalIncome = incomeExpenseData.reduce((sum, item) => sum + item.income, 0);
  const totalExpense = incomeExpenseData.reduce((sum, item) => sum + item.expense, 0);
  const profit = totalIncome - totalExpense;
  const profitMargin = ((profit / totalIncome) * 100).toFixed(1);

  return (
    <div className="financials">
      <div className="financials-header">
        <h1>Financial Overview</h1>
        <div className="time-range">
          <button 
            className={timeRange === 'month' ? 'active' : ''}
            onClick={() => setTimeRange('month')}
          >
            Monthly
          </button>
          <button 
            className={timeRange === 'year' ? 'active' : ''}
            onClick={() => setTimeRange('year')}
          >
            Yearly
          </button>
        </div>
      </div>

      <div className="financial-summary">
        <div className="summary-card income">
          <h3>Total Income</h3>
          <div className="amount">₹{totalIncome.toLocaleString()}</div>
          <div className="trend up">+12.5% from last period</div>
        </div>
        <div className="summary-card expense">
          <h3>Total Expenses</h3>
          <div className="amount">₹{totalExpense.toLocaleString()}</div>
          <div className="trend up">+8.2% from last period</div>
        </div>
        <div className="summary-card profit">
          <h3>Net Profit</h3>
          <div className="amount">₹{profit.toLocaleString()}</div>
          <div className="trend up">+{profitMargin}% margin</div>
        </div>
      </div>

      <div className="tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={activeTab === 'expenses' ? 'active' : ''}
          onClick={() => setActiveTab('expenses')}
        >
          Expenses
        </button>
        <button 
          className={activeTab === 'reports' ? 'active' : ''}
          onClick={() => setActiveTab('reports')}
        >
          Reports
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="chart-container">
              <h3>Income vs Expenses</h3>
              <div className="chart">
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart
                    data={timeRange === 'month' ? incomeExpenseData : yearlyData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey={timeRange === 'month' ? 'month' : 'year'} 
                      tick={{ fill: '#666' }}
                    />
                    <YAxis 
                      tick={{ fill: '#666' }}
                      tickFormatter={(value) => `₹${(value / 1000)}k`}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Area 
                      type="monotone" 
                      dataKey="income" 
                      name="Income" 
                      stroke="#4CAF50" 
                      fill="#E8F5E9" 
                      strokeWidth={2}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="expense" 
                      name="Expense" 
                      stroke="#F44336" 
                      fill="#FFEBEE" 
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="expense-breakdown">
              <h3>Expense Breakdown</h3>
              <div className="chart">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={expenseByCategory}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {expenseByCategory.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `₹${(value * totalExpense / 100).toLocaleString()}`} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'expenses' && (
          <div className="expenses-tab">
            <div className="expense-categories">
              <h3>Expense Categories</h3>
              <div className="category-list">
                {expenseByCategory.map((category, index) => (
                  <div key={index} className="category-item">
                    <div className="category-header">
                      <span className="category-name">{category.name}</span>
                      <span className="category-amount">
                        ₹{Math.round((category.value / 100) * totalExpense).toLocaleString()}
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className="progress" 
                        style={{
                          width: `${category.value}%`,
                          backgroundColor: COLORS[index % COLORS.length]
                        }}
                      ></div>
                    </div>
                    <div className="category-percentage">{category.value}% of total expenses</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="recent-transactions">
              <h3>Recent Transactions</h3>
              <div className="transactions-list">
                {[
                  { id: 1, date: '2023-06-15', description: 'Organic Fertilizer Purchase', amount: 12500, category: 'Fertilizers' },
                  { id: 2, date: '2023-06-12', description: 'Labor Wages', amount: 18500, category: 'Labor' },
                  { id: 3, date: '2023-06-08', description: 'Rice Seeds', amount: 9800, category: 'Seeds' },
                  { id: 4, date: '2023-06-03', description: 'Tractor Maintenance', amount: 7500, category: 'Equipment' },
                  { id: 5, date: '2023-05-28', description: 'Pesticides', amount: 6500, category: 'Others' },
                ].map(transaction => (
                  <div key={transaction.id} className="transaction-item">
                    <div className="transaction-date">
                      {new Date(transaction.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                    </div>
                    <div className="transaction-details">
                      <div className="transaction-description">{transaction.description}</div>
                      <div className="transaction-category">{transaction.category}</div>
                    </div>
                    <div className="transaction-amount">
                      -₹{transaction.amount.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="reports-tab">
            <div className="yearly-comparison">
              <h3>Yearly Performance</h3>
              <div className="chart">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={yearlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="income" name="Income" fill="#4CAF50" />
                    <Bar dataKey="expense" name="Expense" fill="#F44336" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="financial-metrics">
              <h3>Key Metrics</h3>
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-value">
                    {profitMargin}%
                  </div>
                  <div className="metric-label">Profit Margin</div>
                  <div className="metric-change up">+2.3% from last year</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">
                    ₹{(totalIncome / incomeExpenseData.length).toLocaleString()}
                  </div>
                  <div className="metric-label">Avg. Monthly Income</div>
                  <div className="metric-change up">+8.7% from last year</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">
                    {(totalExpense / totalIncome * 100).toFixed(1)}%
                  </div>
                  <div className="metric-label">Expense to Income Ratio</div>
                  <div className="metric-change down">-3.2% from last year</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .financials {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem 1rem;
        }
        
        .financials-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }
        
        .financials-header h1 {
          color: #2c3e50;
          margin: 0;
        }
        
        .time-range {
          display: flex;
          background: #f5f5f5;
          border-radius: 20px;
          padding: 4px;
        }
        
        .time-range button {
          background: none;
          border: none;
          padding: 0.5rem 1.25rem;
          border-radius: 16px;
          cursor: pointer;
          font-size: 0.9rem;
          color: #666;
          transition: all 0.2s;
        }
        
        .time-range button.active {
          background: white;
          color: #27ae60;
          box-shadow: 0 2px 5px rgba(0,0,0,0.1);
          font-weight: 500;
        }
        
        .financial-summary {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }
        
        .summary-card {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          border-top: 4px solid #27ae60;
        }
        
        .summary-card.income { border-color: #4CAF50; }
        .summary-card.expense { border-color: #F44336; }
        .summary-card.profit { border-color: #2196F3; }
        
        .summary-card h3 {
          color: #555;
          margin-top: 0;
          margin-bottom: 0.75rem;
          font-size: 1rem;
          font-weight: 500;
        }
        
        .summary-card .amount {
          font-size: 1.75rem;
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 0.5rem;
        }
        
        .summary-card .trend {
          font-size: 0.85rem;
        }
        
        .trend.up { color: #4CAF50; }
        .trend.down { color: #F44336; }
        
        .tabs {
          display: flex;
          border-bottom: 1px solid #eee;
          margin-bottom: 1.5rem;
        }
        
        .tabs button {
          padding: 0.75rem 1.5rem;
          background: none;
          border: none;
          border-bottom: 3px solid transparent;
          color: #666;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .tabs button.active {
          color: #27ae60;
          border-bottom-color: #27ae60;
          font-weight: 500;
        }
        
        .tab-content {
          margin-bottom: 2rem;
        }
        
        .chart-container, .expense-breakdown {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          margin-bottom: 1.5rem;
        }
        
        .chart {
          margin-top: 1.5rem;
          height: 300px;
        }
        
        .expense-categories, .recent-transactions, .yearly-comparison, .financial-metrics {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          margin-bottom: 1.5rem;
        }
        
        .category-item {
          margin-bottom: 1.5rem;
        }
        
        .category-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.5rem;
        }
        
        .category-name {
          font-weight: 500;
          color: #2c3e50;
        }
        
        .category-amount {
          font-weight: 600;
          color: #2c3e50;
        }
        
        .progress-bar {
          height: 8px;
          background: #f0f0f0;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 0.25rem;
        }
        
        .progress {
          height: 100%;
          border-radius: 4px;
        }
        
        .category-percentage {
          font-size: 0.85rem;
          color: #777;
        }
        
        .transaction-item {
          display: flex;
          align-items: center;
          padding: 1rem 0;
          border-bottom: 1px solid #eee;
        }
        
        .transaction-item:last-child {
          border-bottom: none;
        }
        
        .transaction-date {
          width: 70px;
          font-weight: 500;
          color: #2c3e50;
        }
        
        .transaction-details {
          flex: 1;
          padding: 0 1rem;
        }
        
        .transaction-description {
          color: #2c3e50;
          margin-bottom: 0.25rem;
        }
        
        .transaction-category {
          font-size: 0.85rem;
          color: #777;
          background: #f5f5f5;
          display: inline-block;
          padding: 0.1rem 0.5rem;
          border-radius: 10px;
        }
        
        .transaction-amount {
          font-weight: 600;
          color: #F44336;
        }
        
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-top: 1.5rem;
        }
        
        .metric-card {
          text-align: center;
          padding: 1.5rem;
          background: #f9f9f9;
          border-radius: 8px;
        }
        
        .metric-value {
          font-size: 2rem;
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 0.5rem;
        }
        
        .metric-label {
          color: #666;
          margin-bottom: 0.5rem;
        }
        
        .metric-change {
          font-size: 0.85rem;
        }
        
        .custom-tooltip {
          background: white;
          border: 1px solid #eee;
          border-radius: 4px;
          padding: 0.75rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .custom-tooltip .label {
          font-weight: 600;
          margin: 0 0 0.5rem 0;
          color: #2c3e50;
        }
        
        .custom-tooltip p {
          margin: 0.25rem 0;
          font-size: 0.9rem;
        }
        
        .custom-tooltip .income { color: #4CAF50; }
        .custom-tooltip .expense { color: #F44336; }
        .custom-tooltip .profit { 
          color: #2196F3;
          font-weight: 500;
          margin-top: 0.5rem;
          padding-top: 0.5rem;
          border-top: 1px solid #eee;
        }
        
        @media (max-width: 768px) {
          .financials-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }
          
          .time-range {
            width: 100%;
          }
          
          .time-range button {
            flex: 1;
            text-align: center;
          }
          
          .tabs {
            overflow-x: auto;
            padding-bottom: 0.5rem;
          }
          
          .tabs button {
            white-space: nowrap;
          }
          
          .transaction-item {
            flex-wrap: wrap;
            gap: 0.5rem;
          }
          
          .transaction-details {
            flex: 100%;
            order: 3;
            padding: 0.5rem 0 0 0;
          }
          
          .transaction-amount {
            margin-left: auto;
          }
        }
      `}</style>
    </div>
  );
};

export default Financials;
