import React, { useState } from 'react';

function Marketplace() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [products] = useState([
    {
      id: 1,
      name: 'Hybrid Rice Seeds (5kg)',
      price: 1250,
      category: 'seeds',
      rating: 4.5,
      seller: 'AgroSeeds Co.'
    },
    {
      id: 2,
      name: 'NPK Fertilizer (50kg)',
      price: 1450,
      category: 'fertilizers',
      rating: 4.2,
      seller: 'FarmGrow Ltd.'
    },
    {
      id: 3,
      name: 'Hand Sprayer (5L)',
      price: 850,
      category: 'equipment',
      rating: 4.0,
      seller: 'AgriTools India'
    }
  ]);

  const categories = [
    { id: 'all', name: 'All Categories' },
    { id: 'seeds', name: 'Seeds' },
    { id: 'fertilizers', name: 'Fertilizers' },
    { id: 'equipment', name: 'Equipment' }
  ];

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="marketplace">
      <h1>Farmers' Marketplace</h1>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      
      <div className="filters">
        <select 
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          {categories.map(category => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </div>

      <div className="products-grid">
        {filteredProducts.map(product => (
          <div key={product.id} className="product-card">
            <div className="product-image">
              <img src={`/images/${product.id}.jpg`} alt={product.name} />
            </div>
            <div className="product-details">
              <h3>{product.name}</h3>
              <div className="price">₹{product.price}</div>
              <div className="seller">Sold by: {product.seller}</div>
              <div className="rating">
                {'★'.repeat(Math.floor(product.rating))}
                {'☆'.repeat(5 - Math.ceil(product.rating))}
                <span>({product.rating})</span>
              </div>
              <button className="add-to-cart">Add to Cart</button>
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        .marketplace {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem 1rem;
        }
        
        .search-bar {
          margin: 1.5rem 0;
        }
        
        .search-bar input {
          width: 100%;
          max-width: 500px;
          padding: 0.75rem 1rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        .filters {
          margin: 1rem 0;
        }
        
        .filters select {
          padding: 0.5rem 1rem;
          border-radius: 4px;
          border: 1px solid #ddd;
        }
        
        .products-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 2rem;
          margin-top: 2rem;
        }
        
        .product-card {
          border: 1px solid #eee;
          border-radius: 8px;
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .product-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .product-image {
          height: 180px;
          background: #f5f5f5;
        }
        
        .product-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        
        .product-details {
          padding: 1.25rem;
        }
        
        .product-details h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.1rem;
          color: #333;
        }
        
        .price {
          font-size: 1.25rem;
          font-weight: 600;
          color: #27ae60;
          margin: 0.5rem 0;
        }
        
        .seller {
          font-size: 0.9rem;
          color: #666;
          margin: 0.25rem 0;
        }
        
        .rating {
          color: #f1c40f;
          margin: 0.5rem 0;
        }
        
        .rating span {
          color: #666;
          margin-left: 0.5rem;
        }
        
        .add-to-cart {
          width: 100%;
          padding: 0.75rem;
          background: #27ae60;
          color: white;
          border: none;
          border-radius: 4px;
          font-weight: 500;
          cursor: pointer;
          margin-top: 0.75rem;
          transition: background 0.2s;
        }
        
        .add-to-cart:hover {
          background: #219653;
        }
        
        @media (max-width: 768px) {
          .products-grid {
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
}

export default Marketplace;