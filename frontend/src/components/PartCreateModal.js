import React, { useEffect, useState } from 'react';
import { Modal, Box, Button, Select, MenuItem, InputLabel, FormControl } from '@mui/material';
import axios from 'axios';

// Modal styling
const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
    borderRadius: '8px',
};

const PartCreateModal = ({ isOpen, onClose, onPartCreated }) => {
    const [aircraftType, setAircraftType] = useState('');
    const [partType, setPartType] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    // Fetch user team and corresponding part type when the component mounts
    useEffect(() => {
        const fetchUserTeam = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await axios.get('/api/user/me', {
                    headers: { Authorization: `Token ${token}` },
                });
                assignPartType(response.data.personnel.team.name);
            } catch (error) {
                console.error('Error fetching user team:', error);
                setErrorMessage('Failed to fetch user team information.');
            }
        };

        fetchUserTeam();
    }, []);

    // Assign part type based on user team
    const assignPartType = (teamName) => {
        const partTypeMap = {
            'Wing Team': 'WING',
            'Body Team': 'BODY',
            'Tail Team': 'TAIL',
            'Avionics Team': 'AVIONICS',
        };

        const assignedPartType = partTypeMap[teamName];
        if (assignedPartType) {
            setPartType(assignedPartType);
        } else {
            setErrorMessage('User team does not have a valid part type assigned.');
        }
    };

    // Handle part creation
    const handleCreatePart = async (e) => {
        e.preventDefault();
        setErrorMessage('');

        const token = localStorage.getItem('token');
        try {
            await axios.post('/api/parts/',
                { name: partType, aircraft_type: aircraftType },
                { headers: { Authorization: `Token ${token}` } }
            );
            onPartCreated(); // Notify parent component to refresh part list
            onClose(); // Close modal
        } catch (error) {
            handleErrorResponse(error); // Handle error response
        }
    };

    // Handle error responses
    const handleErrorResponse = (error) => {
        if (error.response && error.response.data) {
            const errorMsg = error.response.data.detail || error.response.data[0] || 'An error occurred. Please try again.';
            setErrorMessage(errorMsg);
        } else {
            setErrorMessage('An error occurred. Please try again.');
        }
    };

    return (
        <Modal
            open={isOpen}
            onClose={onClose}
            aria-labelledby="create-part-modal"
            aria-describedby="create-new-part"
        >
            <Box sx={style}>
                <h2 id="create-part-modal">Create New Part</h2>
                {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
                <FormControl fullWidth sx={{ mt: 2 }}>
                    <InputLabel id="part-name-label">Part Name</InputLabel>
                    <Select
                        fullWidth
                        value={partType}
                        disabled
                        variant={'filled'}
                    >
                        <MenuItem value="WING">Wing</MenuItem>
                        <MenuItem value="BODY">Body</MenuItem>
                        <MenuItem value="TAIL">Tail</MenuItem>
                        <MenuItem value="AVIONICS">Avionics</MenuItem>
                    </Select>
                </FormControl>
                <FormControl fullWidth sx={{ mt: 2 }}>
                    <InputLabel id="aircraft-type-label">Aircraft Type</InputLabel>
                    <Select
                        fullWidth
                        value={aircraftType}
                        onChange={(e) => setAircraftType(e.target.value)}
                        variant={'filled'}
                    >
                        <MenuItem value="AKINCI">AKINCI</MenuItem>
                        <MenuItem value="TB2">TB2</MenuItem>
                        <MenuItem value="TB3">TB3</MenuItem>
                        <MenuItem value="KIZILELMA">KIZILELMA</MenuItem>
                    </Select>
                </FormControl>
                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleCreatePart}
                    sx={{ mt: 2 }}
                >
                    Create Part
                </Button>
            </Box>
        </Modal>
    );
};

export default PartCreateModal;
