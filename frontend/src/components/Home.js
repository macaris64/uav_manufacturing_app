import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useUser } from '../UserContext';

const Home = () => {
    const { user, logout } = useUser();
    const navigate = useNavigate();

    useEffect(() => {
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    return (
        <div>
            <h1>Welcome to the Home Page</h1>
            {user ? (
                <div>
                    <h3>Welcome, {user.username}</h3>
                    <button onClick={logout}>Logout</button>
                </div>
            ) : (
                <div>
                    <Link to="/login"><button>Login</button></Link>
                    <Link to="/register"><button>Register</button></Link>
                </div>
            )}
        </div>
    );
};

export default Home;
