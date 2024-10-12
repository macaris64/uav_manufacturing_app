import React, { createContext, useContext, useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const UserContext = createContext();

export const useUser = () => useContext(UserContext);

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    const fetchUser = async () => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const response = await axios.get('/api/user/me', {
                    headers: { Authorization: `Token ${token}` },
                });
                console.log("User data fetched:", response.data);
                setUser(response.data);
            } catch (error) {
                console.error('Error fetching user data:', error);
                logout();
            }
        } else {
            setUser(null);
        }
    };

    const login = async (username, password) => {
        try {
            const response = await axios.post('/auth/login/', { username, password });
            localStorage.setItem('token', response.data.key);
            await fetchUser();
            navigate('/');
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    const register = async (username, password, teamId) => {
        try {
            await axios.post('/api/register/', {
                username,
                password,
                team: teamId,
            });
            await login(username, password);
        } catch (error) {
            console.error('Registration failed:', error);
        }
    };

    const logout = async () => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                await axios.post('/auth/logout/', {}, {
                    headers: { Authorization: `Token ${token}` }
                });
                localStorage.removeItem('token');
                setUser(null);
                navigate('/login');
            } catch (error) {
                console.error('Logout failed:', error);
            }
        }
    };

    useEffect(() => {
        fetchUser();
    }, []);

    useEffect(() => {
        if (user) {
            navigate('/');
        }
    }, [user, navigate]);

    return (
        <UserContext.Provider value={{ user, login, register, logout }}>
            {children}
        </UserContext.Provider>
    );
};
