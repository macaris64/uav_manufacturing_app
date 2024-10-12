import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useUser } from '../UserContext';

const Register = () => {
    const { register } = useUser(); // Destructure the register function from UserContext
    const [username, setUsername] = useState(''); // State for the username
    const [password, setPassword] = useState(''); // State for the password
    const [team, setTeam] = useState(''); // State for the selected team
    const [teams, setTeams] = useState([]); // State for the list of teams
    const [errorMessage, setErrorMessage] = useState(''); // State for error messages

    // Fetch teams from the API when the component mounts
    useEffect(() => {
        const fetchTeams = async () => {
            try {
                const response = await axios.get('/api/teams/');
                setTeams(response.data); // Set teams data
            } catch (error) {
                setErrorMessage('Failed to load teams. Please try again later.'); // Handle error
            }
        };
        fetchTeams(); // Call the fetch function
    }, []);

    // Handle registration when the form is submitted
    const handleRegister = async (e) => {
        e.preventDefault(); // Prevent default form submission
        if (team) {
            await register(username, password, team); // Call the register function
        } else {
            setErrorMessage('Please select a team.'); // Show error if no team is selected
        }
    };

    return (
        <div>
            <h2>Register</h2>
            {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>} {/* Display error message */}
            <form onSubmit={handleRegister}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)} // Update username state
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)} // Update password state
                />
                <select value={team} onChange={(e) => setTeam(e.target.value)}> {/* Select team */}
                    <option value="">Select Team</option>
                    {teams.map((team) => ( // Map through teams to create options
                        <option key={team.id} value={team.id}>
                            {team.name}
                        </option>
                    ))}
                </select>
                <button type="submit">Register</button> {/* Submit button */}
            </form>
        </div>
    );
};

export default Register;
