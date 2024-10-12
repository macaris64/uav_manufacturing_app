import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useUser } from '../UserContext';

const Register = () => {
    const { register } = useUser();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [team, setTeam] = useState('');
    const [teams, setTeams] = useState([]);
    const [errorMessage, setErrorMessage] = useState('');

    useEffect(() => {
        const fetchTeams = async () => {
            try {
                const response = await axios.get('/api/teams/');
                setTeams(response.data);
            } catch (error) {
                setErrorMessage('Failed to load teams. Please try again later.');
            }
        };
        fetchTeams();
    }, []);

    const handleRegister = async (e) => {
        e.preventDefault();
        if (team) {
            await register(username, password, team);
        } else {
            setErrorMessage('Please select a team.');
        }
    };

    return (
        <div>
            <h2>Register</h2>
            {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>} {/* Hata mesajını göster */}
            <form onSubmit={handleRegister}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <select value={team} onChange={(e) => setTeam(e.target.value)}>
                    <option value="">Select Team</option>
                    {teams.map((team) => (
                        <option key={team.id} value={team.id}>
                            {team.name}
                        </option>
                    ))}
                </select>
                <button type="submit">Register</button>
            </form>
        </div>
    );
};

export default Register;
