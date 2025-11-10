import React, { useState } from 'react';

function KnowledgeHub() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  const categories = [
    { id: 'all', name: 'All Articles' },
    { id: 'crop', name: 'Crop Management' },
    { id: 'pest', name: 'Pest Control' },
    { id: 'soil', name: 'Soil Health' },
    { id: 'irrigation', name: 'Irrigation' },
    { id: 'organic', name: 'Organic Farming' },
  ];
  
  // Helper function to get placeholder images
  const getPlaceholderImage = (category) => {
    const placeholders = {
      crop: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&h=250&fit=crop',
      pest: 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=250&fit=crop',
      soil: 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=250&fit=crop',
      irrigation: 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&h=250&fit=crop',
      organic: 'https://images.unsplash.com/photo-1500595046743-cd271d694d30?w=400&h=250&fit=crop',
      default: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&h=250&fit=crop'
    };
    return placeholders[category] || placeholders.default;
  };

  const articles = [
    {
      id: 1,
      title: 'Best Practices for Rice Cultivation',
      excerpt: 'Learn the most effective techniques for growing high-yield rice crops with minimal inputs.',
      category: 'crop',
      readTime: '8 min read',
      date: 'Jun 15, 2023',
      image: getPlaceholderImage('crop'),
      featured: true
    },
    {
      id: 2,
      title: 'Natural Pest Control Methods',
      excerpt: 'Discover eco-friendly ways to protect your crops from common pests without using harmful chemicals.',
      category: 'pest',
      readTime: '6 min read',
      date: 'Jun 10, 2023',
      image: getPlaceholderImage('pest'),
      featured: true
    },
    {
      id: 3,
      title: 'Improving Soil Fertility Organically',
      excerpt: 'Enhance your soil health with these proven organic farming techniques.',
      category: 'soil',
      readTime: '7 min read',
      date: 'Jun 5, 2023',
      image: getPlaceholderImage('soil')
    },
    {
      id: 4,
      title: 'Drip Irrigation: A Complete Guide',
      excerpt: 'Everything you need to know about setting up and maintaining an efficient drip irrigation system.',
      category: 'irrigation',
      readTime: '10 min read',
      date: 'May 28, 2023',
      image: getPlaceholderImage('irrigation')
    },
    {
      id: 5,
      title: 'Composting for Beginners',
      excerpt: 'Step-by-step guide to creating nutrient-rich compost for your farm or garden.',
      category: 'organic',
      readTime: '5 min read',
      date: 'May 22, 2023',
      image: getPlaceholderImage('organic')
    },
    {
      id: 6,
      title: 'Crop Rotation Strategies',
      excerpt: 'Maximize your yields and maintain soil health with effective crop rotation techniques.',
      category: 'crop',
      readTime: '6 min read',
      date: 'May 15, 2023',
      image: getPlaceholderImage('crop')
    },
    {
      id: 7,
      title: 'Water Conservation in Agriculture',
      excerpt: 'Innovative methods to reduce water usage while maintaining high crop yields.',
      category: 'irrigation',
      readTime: '9 min read',
      date: 'May 8, 2023',
      image: getPlaceholderImage('irrigation')
    },
    {
      id: 8,
      title: 'Beneficial Insects for Your Farm',
      excerpt: 'How to attract and maintain populations of helpful insects that control pests naturally.',
      category: 'pest',
      readTime: '7 min read',
      date: 'May 1, 2023',
      image: getPlaceholderImage('pest')
    },
  ];
  
  const filteredArticles = articles.filter(article => {
    const matchesCategory = activeCategory === 'all' || article.category === activeCategory;
    const matchesSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         article.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });
  
  const featuredArticles = articles.filter(article => article.featured);

  return (
    <div className="knowledge-hub">
      <div className="hero">
        <h1>Knowledge Hub</h1>
        <p className="subtitle">Expert farming insights, tips, and guides to help you succeed</p>
        
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search articles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button>Search</button>
        </div>
      </div>
      
      <div className="container">
        <div className="categories">
          {categories.map(category => (
            <button
              key={category.id}
              className={`category-tab ${activeCategory === category.id ? 'active' : ''}`}
              onClick={() => setActiveCategory(category.id)}
            >
              {category.name}
            </button>
          ))}
        </div>
        
        {searchQuery && (
          <div className="search-results-count">
            {filteredArticles.length} {filteredArticles.length === 1 ? 'article' : 'articles'} found for "{searchQuery}"
          </div>
        )}
        
        {activeCategory === 'all' && !searchQuery && (
          <div className="featured-section">
            <h2>Featured Articles</h2>
            <div className="featured-grid">
              {featuredArticles.map(article => (
                <div key={article.id} className="featured-article">
                  <div className="article-image">
                    <img 
                      src={article.image} 
                      alt={article.title}
                      onError={(e) => {
                        e.target.src = getPlaceholderImage('default');
                      }}
                    />
                    <span className="category-badge">
                      {categories.find(cat => cat.id === article.category)?.name}
                    </span>
                  </div>
                  <div className="article-content">
                    <h3>{article.title}</h3>
                    <p className="excerpt">{article.excerpt}</p>
                    <div className="article-meta">
                      <span className="read-time">{article.readTime}</span>
                      <span className="date">{article.date}</span>
                    </div>
                    <button className="read-more">Read Article →</button>
                  </div>
                </div>
              ))}
            </div>
            
            <h2 className="section-title">All Articles</h2>
          </div>
        )}
        
        <div className="articles-grid">
          {filteredArticles.length > 0 ? (
            filteredArticles.map(article => (
              <div key={article.id} className="article-card">
                <div className="article-image">
                  <img 
                    src={article.image} 
                    alt={article.title}
                    onError={(e) => {
                      e.target.src = getPlaceholderImage('default');
                    }}
                  />
                </div>
                <div className="article-content">
                  <span className="category">
                    {categories.find(cat => cat.id === article.category)?.name}
                  </span>
                  <h3>{article.title}</h3>
                  <p className="excerpt">{article.excerpt}</p>
                  <div className="article-meta">
                    <span className="read-time">{article.readTime}</span>
                    <span className="date">{article.date}</span>
                  </div>
                  <button className="read-more">Read More →</button>
                </div>
              </div>
            ))
          ) : (
            <div className="no-results">
              <h3>No articles found</h3>
              <p>Try adjusting your search or filter criteria</p>
            </div>
          )}
        </div>
        
        {filteredArticles.length > 0 && (
          <div className="pagination">
            <button className="active">1</button>
            <button>2</button>
            <button>3</button>
            <button>Next →</button>
          </div>
        )}
      </div>
      
      <div className="newsletter">
        <div className="newsletter-content">
          <h2>Stay Updated</h2>
          <p>Subscribe to our newsletter for the latest farming insights and updates</p>
          <div className="newsletter-form">
            <input type="email" placeholder="Your email address" />
            <button>Subscribe</button>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .knowledge-hub {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          color: #333;
          line-height: 1.6;
        }
        
        .hero {
          background: linear-gradient(135deg, #27ae60, #2ecc71);
          color: white;
          padding: 4rem 1rem;
          text-align: center;
          margin-bottom: 2rem;
        }
        
        .hero h1 {
          font-size: 2.5rem;
          margin: 0 0 1rem 0;
          font-weight: 700;
        }
        
        .subtitle {
          font-size: 1.2rem;
          margin: 0 0 2rem 0;
          opacity: 0.9;
        }
        
        .search-bar {
          max-width: 600px;
          margin: 0 auto;
          display: flex;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
          border-radius: 50px;
          overflow: hidden;
        }
        
        .search-bar input {
          flex: 1;
          padding: 1rem 1.5rem;
          border: none;
          font-size: 1rem;
          outline: none;
        }
        
        .search-bar button {
          background: #2c3e50;
          color: white;
          border: none;
          padding: 0 2rem;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }
        
        .search-bar button:hover {
          background: #1a252f;
        }
        
        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 1rem 4rem;
        }
        
        .categories {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 2rem;
          border-bottom: 1px solid #eee;
          padding-bottom: 1rem;
        }
        
        .category-tab {
          background: #f5f5f5;
          border: none;
          border-radius: 20px;
          padding: 0.5rem 1.25rem;
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .category-tab:hover {
          background: #e0e0e0;
        }
        
        .category-tab.active {
          background: #27ae60;
          color: white;
        }
        
        .search-results-count {
          margin: -1rem 0 1.5rem;
          color: #666;
          font-style: italic;
        }
        
        .featured-section {
          margin-bottom: 3rem;
        }
        
        h2 {
          font-size: 1.75rem;
          color: #2c3e50;
          margin: 0 0 1.5rem 0;
        }
        
        .section-title {
          margin-top: 3rem;
        }
        
        .featured-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 2rem;
          margin-bottom: 3rem;
        }
        
        .featured-article {
          background: white;
          border-radius: 10px;
          overflow: hidden;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
          transition: transform 0.3s, box-shadow 0.3s;
          display: flex;
          flex-direction: column;
        }
        
        .featured-article:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
        
        .article-image {
          position: relative;
          height: 200px;
          overflow: hidden;
        }
        
        .article-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.5s;
        }
        
        .featured-article:hover .article-image img {
          transform: scale(1.05);
        }
        
        .category-badge {
          position: absolute;
          top: 1rem;
          left: 1rem;
          background: rgba(39, 174, 96, 0.9);
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 500;
        }
        
        .article-content {
          padding: 1.5rem;
          flex: 1;
          display: flex;
          flex-direction: column;
        }
        
        .featured-article .article-content {
          padding: 1.5rem;
        }
        
        .category {
          display: inline-block;
          background: #e8f5e9;
          color: #27ae60;
          font-size: 0.75rem;
          font-weight: 600;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          margin-bottom: 0.75rem;
        }
        
        h3 {
          font-size: 1.25rem;
          color: #2c3e50;
          margin: 0 0 0.75rem 0;
          line-height: 1.4;
        }
        
        .excerpt {
          color: #555;
          margin: 0 0 1rem 0;
          flex: 1;
        }
        
        .article-meta {
          display: flex;
          justify-content: space-between;
          font-size: 0.85rem;
          color: #777;
          margin-bottom: 1rem;
        }
        
        .read-more {
          align-self: flex-start;
          background: none;
          border: none;
          color: #27ae60;
          font-weight: 600;
          cursor: pointer;
          padding: 0.5rem 0;
          display: flex;
          align-items: center;
          transition: color 0.2s;
        }
        
        .read-more:hover {
          color: #219653;
        }
        
        .read-more::after {
          content: '→';
          margin-left: 0.5rem;
          transition: transform 0.2s;
        }
        
        .read-more:hover::after {
          transform: translateX(3px);
        }
        
        .articles-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 2rem;
          margin-bottom: 3rem;
        }
        
        .article-card {
          background: white;
          border-radius: 10px;
          overflow: hidden;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
          transition: transform 0.3s, box-shadow 0.3s;
          display: flex;
          flex-direction: column;
        }
        
        .article-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
        
        .article-card .article-image {
          height: 160px;
        }
        
        .no-results {
          grid-column: 1 / -1;
          text-align: center;
          padding: 4rem 1rem;
          color: #666;
        }
        
        .no-results h3 {
          font-size: 1.5rem;
          margin-bottom: 0.5rem;
          color: #2c3e50;
        }
        
        .pagination {
          display: flex;
          justify-content: center;
          gap: 0.5rem;
          margin-top: 2rem;
        }
        
        .pagination button {
          width: 40px;
          height: 40px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 5px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .pagination button:not(:last-child):hover {
          border-color: #27ae60;
          color: #27ae60;
        }
        
        .pagination button:last-child {
          padding: 0 1rem;
          width: auto;
        }
        
        .pagination button.active {
          background: #27ae60;
          color: white;
          border-color: #27ae60;
        }
        
        .newsletter {
          background: #f8f9fa;
          padding: 4rem 1rem;
          text-align: center;
        }
        
        .newsletter-content {
          max-width: 600px;
          margin: 0 auto;
        }
        
        .newsletter h2 {
          color: #2c3e50;
          margin-bottom: 1rem;
        }
        
        .newsletter p {
          color: #555;
          margin-bottom: 1.5rem;
        }
        
        .newsletter-form {
          display: flex;
          max-width: 500px;
          margin: 0 auto;
        }
        
        .newsletter-form input {
          flex: 1;
          padding: 0.75rem 1.25rem;
          border: 1px solid #ddd;
          border-radius: 4px 0 0 4px;
          font-size: 1rem;
          outline: none;
        }
        
        .newsletter-form button {
          background: #27ae60;
          color: white;
          border: none;
          padding: 0 1.5rem;
          font-weight: 600;
          border-radius: 0 4px 4px 0;
          cursor: pointer;
          transition: background 0.2s;
        }
        
        .newsletter-form button:hover {
          background: #219653;
        }
        
        @media (max-width: 768px) {
          .hero h1 {
            font-size: 2rem;
          }
          
          .subtitle {
            font-size: 1.1rem;
          }
          
          .search-bar {
            flex-direction: column;
            border-radius: 8px;
            overflow: hidden;
          }
          
          .search-bar input {
            border-radius: 0;
            padding: 1rem;
          }
          
          .search-bar button {
            border-radius: 0;
            padding: 0.75rem;
          }
          
          .categories {
            overflow-x: auto;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
          }
          
          .category-tab {
            white-space: nowrap;
          }
          
          .featured-grid, .articles-grid {
            grid-template-columns: 1fr;
          }
          
          .newsletter-form {
            flex-direction: column;
            gap: 0.5rem;
          }
          
          .newsletter-form input,
          .newsletter-form button {
            border-radius: 4px;
            width: 100%;
          }
        }
        
        @media (max-width: 480px) {
          .hero {
            padding: 3rem 1rem;
          }
          
          .hero h1 {
            font-size: 1.75rem;
          }
          
          h2 {
            font-size: 1.5rem;
          }
          
          .featured-article .article-content,
          .article-content {
            padding: 1.25rem;
          }
          
          h3 {
            font-size: 1.1rem;
          }
          
          .pagination {
            flex-wrap: wrap;
          }
        }
      `}</style>
    </div>
  );
}

export default KnowledgeHub;
