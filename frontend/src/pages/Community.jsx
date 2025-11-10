import React, { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext';

function Community() {
  const [posts, setPosts] = useState([]);
  const [newPost, setNewPost] = useState('');
  const [loading, setLoading] = useState(true);
  const [userDistrict, setUserDistrict] = useState('');
  const { user } = useUser();

  useEffect(() => {
    loadCommunityPosts();
  }, []);

  const loadCommunityPosts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/community/posts', {
        method: 'GET',
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        setPosts(data.posts);
        setUserDistrict(data.user_district);
      } else {
        console.error('Failed to load community posts:', data.error);
      }
    } catch (error) {
      console.error('Error loading community posts:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleLike = (postId) => {
    setPosts(posts.map(post => {
      if (post.id === postId) {
        return {
          ...post,
          likes: post.isLiked ? post.likes - 1 : post.likes + 1,
          isLiked: !post.isLiked
        };
      }
      return post;
    }));
  };
  
  const handleSubmitPost = async (e) => {
    e.preventDefault();
    if (!newPost.trim()) return;
    
    try {
      const response = await fetch('http://localhost:5000/api/community/post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ content: newPost })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setPosts([data.post, ...posts]);
        setNewPost('');
      } else {
        console.error('Failed to create post:', data.error);
        alert('Failed to create post. Please try again.');
      }
    } catch (error) {
      console.error('Error creating post:', error);
      alert('Error creating post. Please check your connection.');
    }
  };

  if (loading) {
    return (
      <div className="community">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading community posts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="community">
      <h1>{userDistrict ? `${userDistrict} ` : ''}Community Forum</h1>
      <p className="subtitle">
        Connect, share, and learn from fellow farmers
        {userDistrict && ` in ${userDistrict}`}
      </p>
      
      <div className="create-post">
        <form onSubmit={handleSubmitPost}>
          <div className="form-group">
            <textarea
              value={newPost}
              onChange={(e) => setNewPost(e.target.value)}
              placeholder="What's on your mind? Share your farming experiences, ask questions, or start a discussion..."
              rows="3"
            ></textarea>
          </div>
          <div className="post-actions">
            <button type="submit" className="post-button">Post</button>
          </div>
        </form>
      </div>
      
      <div className="posts">
        {posts.map(post => (
          <div key={post.id} className="post-card">
            <div className="post-header">
              <div className="user-avatar">
                {post.user.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="user-info">
                <div className="user-name">{post.user}</div>
                <div className="user-details">{post.role} • {post.location} • {post.time}</div>
              </div>
            </div>
            
            <div className="post-content">
              {post.content}
            </div>
            
            <div className="post-actions">
              <button 
                className={`action-button ${post.isLiked ? 'liked' : ''}`}
                onClick={() => handleLike(post.id)}
              >
                <span className="icon">👍</span> {post.likes} {post.likes === 1 ? 'Like' : 'Likes'}
              </button>
              <button className="action-button">
                <span className="icon">💬</span> {post.comments} {post.comments === 1 ? 'Comment' : 'Comments'}
              </button>
              <button className="action-button">
                <span className="icon">↗️</span> Share
              </button>
            </div>
          </div>
        ))}
      </div>
      
      <div className="community-guidelines">
        <h3>Community Guidelines</h3>
        <ul>
          <li>Be respectful and kind to others</li>
          <li>Share accurate and helpful information</li>
          <li>No spam or promotional content</li>
          <li>Keep discussions relevant to farming and agriculture</li>
        </ul>
      </div>
      
      <style jsx>{`
        .community {
          max-width: 800px;
          margin: 0 auto;
          padding: 2rem 1rem;
        }
        
        h1 {
          color: #2c3e50;
          margin-bottom: 0.5rem;
        }
        
        .subtitle {
          color: #555;
          margin-bottom: 2rem;
          font-size: 1.1rem;
        }
        
        .create-post {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          margin-bottom: 2rem;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        textarea {
          width: 100%;
          padding: 1rem;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 1rem;
          resize: vertical;
          min-height: 100px;
        }
        
        .post-actions {
          display: flex;
          justify-content: flex-end;
        }
        
        .post-button {
          background: #27ae60;
          color: white;
          border: none;
          padding: 0.5rem 1.5rem;
          border-radius: 20px;
          font-size: 1rem;
          cursor: pointer;
          transition: background 0.2s;
        }
        
        .post-button:hover {
          background: #219653;
        }
        
        .posts {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          margin-bottom: 2rem;
        }
        
        .post-card {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .post-header {
          display: flex;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .user-avatar {
          width: 50px;
          height: 50px;
          background: #e8f5e9;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          color: #2e7d32;
          margin-right: 1rem;
          font-size: 1.2rem;
        }
        
        .user-name {
          font-weight: 600;
          color: #2c3e50;
        }
        
        .user-details {
          font-size: 0.85rem;
          color: #777;
        }
        
        .post-content {
          margin: 1rem 0;
          line-height: 1.6;
          color: #333;
        }
        
        .post-actions {
          display: flex;
          gap: 1rem;
          border-top: 1px solid #eee;
          padding-top: 1rem;
        }
        
        .action-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: none;
          border: none;
          color: #555;
          cursor: pointer;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          transition: all 0.2s;
        }
        
        .action-button:hover {
          background: #f5f5f5;
        }
        
        .action-button.liked {
          color: #27ae60;
          font-weight: 500;
        }
        
        .community-guidelines {
          background: #f8f9fa;
          border-radius: 10px;
          padding: 1.5rem;
          margin-top: 2rem;
        }
        
        .community-guidelines h3 {
          margin-top: 0;
          color: #2c3e50;
          margin-bottom: 1rem;
        }
        
        .community-guidelines ul {
          padding-left: 1.5rem;
          margin: 0;
        }
        
        .community-guidelines li {
          margin-bottom: 0.5rem;
          color: #555;
        }
        
        @media (max-width: 768px) {
          .post-actions {
            flex-wrap: wrap;
          }
          
          .action-button {
            padding: 0.4rem 0.8rem;
            font-size: 0.9rem;
          }
        }
      `}</style>
    </div>
  );
}

export default Community;
